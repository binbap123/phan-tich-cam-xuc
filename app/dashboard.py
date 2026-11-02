"""Dashboard phân tích cảm xúc review Shopee.

Chạy từ thư mục gốc dự án:  streamlit run app/dashboard.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from src.aspects import absa
from src.data import ASPECTS, load_gold
from src.preprocess import preprocess, strip_accents

st.set_page_config(page_title="Phân tích cảm xúc review", page_icon="💬", layout="wide")

ASP_VI = {"giao_hang": "Giao hàng", "chat_luong": "Chất lượng", "gia_ca": "Giá cả", "dich_vu": "Dịch vụ"}
LAB_VI = {"pos": "Tích cực", "neu": "Trung lập", "neg": "Tiêu cực"}
COLORS = {"Tích cực": "#55A868", "Trung lập": "#CCB974", "Tiêu cực": "#C44E52"}
HITL_TAU = 0.6           # xác suất cao nhất < ngưỡng này -> chuyển nhân viên kiểm tra

# Khuyến nghị hành động cho (khía cạnh, tiêu cực)
ACTIONS = {
    "giao_hang": "Kiểm tra mã vận đơn, liên hệ đơn vị vận chuyển; gửi lời xin lỗi kèm voucher phí ship.",
    "chat_luong": "Mời khách gửi ảnh/video, đề xuất đổi mới hoặc hoàn tiền; báo bộ phận kiểm hàng về lô này.",
    "gia_ca": "Giải thích giá trị sản phẩm, gợi ý combo hoặc voucher cho lần mua sau.",
    "dich_vu": "Quản lý CSKH gọi lại trong 24 giờ; rà soát kịch bản trả lời tin nhắn.",
}


@st.cache_resource
def load_model():
    return joblib.load(ROOT / "models" / "tfidf_lr_AB.joblib")


@st.cache_data
def load_predicted():
    return pd.read_csv(ROOT / "data" / "processed" / "shopee_predicted.csv")


@st.cache_data
def gold_scores():
    gold, temp = load_gold()
    p = load_model().predict_proba(gold[["text_prep", "text_raw"]])
    return gold[["rating", "label"]].assign(p_neg=p[:, 0]), temp


def predict(texts):
    model = load_model()
    X = pd.DataFrame({"text_prep": [preprocess(t) for t in texts], "text_raw": list(texts)})
    return model.predict_proba(X), X


def word_contrib(x_prep, k, top=8):
    """SHAP của mô hình tuyến tính cho 1 câu: hệ số × (tf-idf − trung bình). Xem notebook 09."""
    model = load_model()
    ct, clf = model.named_steps["vec"], model.named_steps["clf"]
    x = ct.transform(pd.DataFrame({"text_prep": [x_prep], "text_raw": [""]})).toarray().ravel()
    vocab = np.array([v.split("__", 1)[1] for v in ct.get_feature_names_out()])
    phi = x * clf.coef_[k]          # bỏ phần trung bình (gần 0 với từ hiếm) để nhanh trong app
    idx = np.argsort(np.abs(phi))[::-1][:top]
    idx = idx[phi[idx] != 0]
    return pd.DataFrame({"từ": vocab[idx], "đóng góp": phi[idx]})


def recommend(label, aspects, conf):
    recs = []
    if conf < HITL_TAU:
        recs.append(f"⚠️ Mô hình không chắc chắn (xác suất cao nhất {conf:.0%}): **chuyển nhân viên đọc lại**.")
    neg_asp = [a for a, s in aspects.items() if s == "neg"]
    for a in neg_asp:
        recs.append(f"**{ASP_VI[a]}:** {ACTIONS[a]}")
    if label == "neg" and not neg_asp:
        recs.append("Review tiêu cực chung: phản hồi công khai trong 24 giờ, hỏi rõ vấn đề qua tin nhắn.")
    if label == "pos" and not neg_asp:
        recs.append("Cảm ơn khách; cân nhắc dùng review làm nội dung giới thiệu sản phẩm.")
    return recs


st.title("💬 Phân tích cảm xúc đánh giá sản phẩm")
st.caption("Mô hình: TF-IDF + Logistic Regression, huấn luyện trên ViSD4SA + Shopee. "
           "ABSA 4 khía cạnh bằng từ điển + mô hình cảm xúc trên từng mệnh đề.")
tab1, tab2, tab3 = st.tabs(["🔎 Phân tích review", "🧪 What-if", "📊 Tổng quan Shopee"])

# ---------------------------------------------------------------- Tab 1
with tab1:
    txt = st.text_area("Nhập một review", height=110,
                       value="Giao hàng nhanh, đóng gói cẩn thận nhưng vải mỏng, mặc một lần đã bung chỉ. Nhắn shop không thấy trả lời.")
    if st.button("Phân tích", type="primary") and txt.strip():
        P, X = predict([txt])
        p = P[0]
        k = int(p.argmax())
        label = load_model().classes_[k]
        asp = absa(txt, load_model())
        c1, c2 = st.columns([1, 1])
        with c1:
            st.metric("Cảm xúc tổng thể", LAB_VI[label], f"độ tin cậy {p[k]:.0%}", delta_color="off")
            fig = px.bar(x=[LAB_VI[c] for c in load_model().classes_], y=p, color=[LAB_VI[c] for c in load_model().classes_],
                         color_discrete_map=COLORS, labels={"x": "", "y": "Xác suất"}, height=260)
            fig.update_layout(showlegend=False, margin=dict(t=10, b=10))
            st.plotly_chart(fig, width="stretch")
        with c2:
            st.markdown("**Khía cạnh được nhắc tới**")
            if asp:
                st.dataframe(pd.DataFrame({"Khía cạnh": [ASP_VI[a] for a in asp], "Cảm xúc": [LAB_VI[s] for s in asp.values()]}),
                             hide_index=True, width="stretch")
            else:
                st.write("Không tìm thấy khía cạnh nào trong từ điển.")
            st.markdown(f"**Từ ảnh hưởng nhiều nhất tới dự đoán '{LAB_VI[label]}'**")
            wc = word_contrib(X.text_prep[0], k)
            st.dataframe(wc.style.format({"đóng góp": "{:+.3f}"}), hide_index=True, width="stretch")
        st.subheader("Khuyến nghị hành động")
        for r in recommend(label, asp, p[k]):
            st.markdown(f"- {r}")

    st.divider()
    st.markdown("**Phân tích hàng loạt:** tải lên file CSV có cột `text`.")
    up = st.file_uploader("CSV", type="csv", label_visibility="collapsed")
    if up is not None:
        df = pd.read_csv(up)
        if "text" not in df:
            st.error("File phải có cột `text`.")
        else:
            df = df.dropna(subset=["text"]).head(2000)
            with st.spinner(f"Đang phân tích {len(df)} review…"):
                P, _ = predict(df.text.astype(str))
                df["cam_xuc"] = [LAB_VI[c] for c in np.array(load_model().classes_)[P.argmax(1)]]
                df["p_tieu_cuc"] = P[:, 0].round(3)
                df["can_nguoi_doc"] = P.max(1) < HITL_TAU
                asp = df.text.astype(str).map(lambda s: absa(s, load_model()))
                for a in ASPECTS:
                    df[ASP_VI[a]] = asp.map(lambda d: LAB_VI.get(d.get(a), ""))
            st.dataframe(df.sort_values("p_tieu_cuc", ascending=False), width="stretch", hide_index=True)
            st.download_button("Tải kết quả", df.to_csv(index=False).encode("utf-8-sig"), "ket_qua.csv", "text/csv")

# ---------------------------------------------------------------- Tab 2
with tab2:
    st.subheader("1. Thay đổi câu chữ: dự đoán đổi thế nào?")
    base = st.text_input("Câu gốc", "Sản phẩm đẹp, giao hàng nhanh")
    variants = {
        "Câu gốc": base,
        "Thêm phủ định": base.replace("đẹp", "không đẹp").replace("nhanh", "không nhanh"),
        "Thêm ý trái chiều": base + " nhưng dùng 2 ngày đã hỏng",
        "Bỏ dấu (gõ không dấu)": strip_accents(base),
        "Tự sửa": st.text_input("Câu tự sửa", base + " nhưng giao chậm quá"),
    }
    P, _ = predict(list(variants.values()))
    cls = load_model().classes_
    wi = pd.DataFrame(P, columns=[LAB_VI[c] for c in cls]).assign(**{"Biến thể": list(variants), "Câu": list(variants.values())})
    wi["Dự đoán"] = [LAB_VI[c] for c in cls[P.argmax(1)]]
    st.dataframe(wi[["Biến thể", "Câu", "Dự đoán", "Tiêu cực", "Trung lập", "Tích cực"]]
                 .style.format({c: "{:.0%}" for c in ["Tiêu cực", "Trung lập", "Tích cực"]})
                 .background_gradient(subset=["Tiêu cực"], cmap="Reds", vmin=0, vmax=1),
                 hide_index=True, width="stretch")

    st.subheader("2. Ngưỡng cảnh báo và chi phí vận hành")
    gs, temp = gold_scores()
    if temp:
        st.warning("Đang dùng nhãn sao tạm thời (chưa đủ nhãn tay), nên phương án 'lọc theo sao' đúng tuyệt đối một cách giả tạo.")
    c1, c2, c3, c4 = st.columns(4)
    n = c1.number_input("Review mỗi tháng", 100, 100_000, 3000, step=500)
    c_read = c2.number_input("Chi phí đọc 1 review (đ)", 0, 50_000, 1_000, step=500)
    c_miss = c3.number_input("Thiệt hại khi bỏ sót 1 lời chê (đ)", 0, 1_000_000, 50_000, step=10_000)
    t = c4.slider("Ngưỡng P(tiêu cực)", 0.05, 0.95, 0.35, 0.05)
    is_neg = (gs.label == "neg").values
    scale = n / len(gs)

    def cost(flag):
        fn = (is_neg & ~flag).sum()
        return {"Review phải đọc": flag.sum() * scale, "Lời chê bị bỏ sót": fn * scale,
                "Recall tiêu cực": (is_neg & flag).sum() / max(is_neg.sum(), 1),
                "Tổng chi phí/tháng (đ)": flag.sum() * scale * c_read + fn * scale * c_miss}

    table = pd.DataFrame({"Đọc tay toàn bộ": cost(np.ones(len(gs), bool)),
                          "Lọc theo sao (1–2 sao)": cost((gs.rating <= 2).values),
                          f"Mô hình (P ≥ {t:.2f})": cost(gs.p_neg.values >= t)}).T
    st.dataframe(table.style.format({"Review phải đọc": "{:,.0f}", "Lời chê bị bỏ sót": "{:,.0f}",
                                     "Recall tiêu cực": "{:.0%}", "Tổng chi phí/tháng (đ)": "{:,.0f}"}),
                 width="stretch")
    ts = np.linspace(0.05, 0.95, 19)
    curve = pd.DataFrame([{"Ngưỡng": x, **cost(gs.p_neg.values >= x)} for x in ts])
    fig = px.line(curve, x="Ngưỡng", y="Tổng chi phí/tháng (đ)", markers=True, height=300)
    fig.add_vline(x=t, line_dash="dot", line_color="green")
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- Tab 3
with tab3:
    df = load_predicted()
    c1, c2 = st.columns(2)
    cats = c1.multiselect("Ngành hàng", sorted(df.category.dropna().unique()))
    if cats:
        df = df[df.category.isin(cats)]
    prods = c2.multiselect("Sản phẩm", sorted(df["product"].unique()))
    if prods:
        df = df[df["product"].isin(prods)]
    m1, m2, m3 = st.columns(3)
    m1.metric("Số review", f"{len(df):,}")
    m2.metric("Tỉ lệ tiêu cực (mô hình)", f"{(df.pred == 'neg').mean():.1%}")
    m3.metric("Sao trung bình", f"{df.rating.mean():.2f}")

    c1, c2 = st.columns(2)
    sent = df.pred.map(LAB_VI).value_counts().reset_index()
    c1.plotly_chart(px.pie(sent, names="pred", values="count", color="pred", color_discrete_map=COLORS,
                           title="Cảm xúc tổng thể", hole=0.4, height=330), width="stretch")
    long = df.melt(value_vars=ASPECTS, var_name="Khía cạnh", value_name="Cảm xúc")
    long = long[long["Cảm xúc"] != "none"]
    long["Khía cạnh"] = long["Khía cạnh"].map(ASP_VI)
    long["Cảm xúc"] = long["Cảm xúc"].map(LAB_VI)
    agg = long.value_counts(["Khía cạnh", "Cảm xúc"]).reset_index()
    c2.plotly_chart(px.bar(agg, x="Khía cạnh", y="count", color="Cảm xúc", color_discrete_map=COLORS,
                           title="Cảm xúc theo khía cạnh", height=330, labels={"count": "Số mệnh đề"}),
                    width="stretch")
    st.markdown("**Review tiêu cực nổi bật**")
    st.dataframe(df[df.pred == "neg"].sort_values("p_neg", ascending=False)
                 [["category", "rating", "p_neg", "text_clean"] + ASPECTS].head(50),
                 hide_index=True, width="stretch")
