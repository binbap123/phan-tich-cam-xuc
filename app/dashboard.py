"""Dashboard phân tích cảm xúc review Shopee.

Chạy từ thư mục gốc dự án:  streamlit run app/dashboard.py
"""
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.aspects import absa, top_negative_keywords
from src.data import ASPECTS, load_gold
from src.preprocess import preprocess, strip_accents

st.set_page_config(page_title="Phân tích cảm xúc review", page_icon="💬", layout="wide")

ASP_VI = {"giao_hang": "Giao hàng", "chat_luong": "Chất lượng", "gia_ca": "Giá cả", "dich_vu": "Dịch vụ"}
ASP_ICON = {"giao_hang": "🚚", "chat_luong": "🧵", "gia_ca": "💰", "dich_vu": "🎧"}
LAB_VI = {"pos": "Tích cực", "neu": "Trung lập", "neg": "Tiêu cực"}
COLORS = {"Tích cực": "#2E9E6B", "Trung lập": "#C99A1E", "Tiêu cực": "#D64545"}
HITL_TAU = 0.6           # xác suất cao nhất < ngưỡng này -> chuyển nhân viên kiểm tra

# Khuyến nghị hành động cho (khía cạnh, tiêu cực)
ACTIONS = {
    "giao_hang": "Kiểm tra mã vận đơn, liên hệ đơn vị vận chuyển; gửi lời xin lỗi kèm voucher phí ship.",
    "chat_luong": "Mời khách gửi ảnh/video, đề xuất đổi mới hoặc hoàn tiền; báo bộ phận kiểm hàng về lô này.",
    "gia_ca": "Giải thích giá trị sản phẩm, gợi ý combo hoặc voucher cho lần mua sau.",
    "dich_vu": "Quản lý CSKH gọi lại trong 24 giờ; rà soát kịch bản trả lời tin nhắn.",
}

SAMPLES = {
    "Khen lẫn chê": "Giao hàng nhanh, đóng gói cẩn thận nhưng vải mỏng, mặc một lần đã bung chỉ. Nhắn shop không thấy trả lời.",
    "Chê giao hàng": "Giao hàng chậm, hộp bị móp, hàng bên trong bị vỡ.",
    "Khen": "Sản phẩm đẹp, đúng mô tả, giá hợp lý. Sẽ ủng hộ shop lần sau.",
    "Gõ không dấu": "giao hang cham, hang bi vo nhung shop ho tro nhanh",
}

# ---------------------------------------------------------------- Giao diện chung
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, .stTextArea textarea, .stTextInput input, button, label {
  font-family: 'Be Vietnam Pro', sans-serif !important;
}
.block-container { padding-top: 2rem; max-width: 1180px; }
h1, h2, h3 { letter-spacing: -0.01em; }
.hero {
  background: linear-gradient(120deg, #0F766E 0%, #115E59 55%, #134E4A 100%);
  color: #fff; border-radius: 18px; padding: 26px 30px; margin-bottom: 18px;
}
.hero h1 { color: #fff; font-size: 1.9rem; margin: 0 0 6px 0; padding: 0; }
.hero p { color: #CCFBF1; margin: 0; font-size: 0.98rem; }
.hero .tags { margin-top: 14px; }
.hero .tag {
  display: inline-block; background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.25);
  color: #fff; border-radius: 999px; padding: 3px 12px; margin: 0 6px 6px 0; font-size: 0.8rem;
}
.card {
  background: #fff; border: 1px solid #E5E7EB; border-radius: 14px; padding: 18px 20px; height: 100%;
}
.card-label { color: #6B7280; font-size: 0.8rem; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px; }
.card-value { font-size: 1.7rem; font-weight: 700; color: #111827; line-height: 1.2; }
.card-sub { color: #6B7280; font-size: 0.85rem; margin-top: 4px; }
.pill {
  display: inline-block; border-radius: 999px; padding: 6px 16px; font-weight: 600; font-size: 1.05rem; color: #fff;
}
.chip {
  display: inline-flex; align-items: center; gap: 6px; border-radius: 10px; padding: 7px 12px;
  margin: 0 8px 8px 0; font-weight: 500; font-size: 0.92rem; border: 1px solid;
}
.rec {
  background: #fff; border: 1px solid #E5E7EB; border-left: 4px solid #0F766E; border-radius: 10px;
  padding: 12px 16px; margin-bottom: 10px;
}
.rec.warn { border-left-color: #C99A1E; background: #FFFBEB; }
.rec.neg { border-left-color: #D64545; }
.rec b { color: #111827; }
.section-title { font-weight: 700; font-size: 1.15rem; margin: 6px 0 2px 0; color: #111827; }
.section-sub { color: #6B7280; font-size: 0.9rem; margin-bottom: 10px; }
.muted { color: #6B7280; font-size: 0.85rem; }
[data-testid="stTabs"] button[role="tab"] { font-size: 0.98rem; padding: 10px 18px; }
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { color: #0F766E; }
[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 14px !important; background: #fff; }
</style>
""", unsafe_allow_html=True)


def style_fig(fig, height=None):
    fig.update_layout(font=dict(family="Be Vietnam Pro, sans-serif", color="#374151", size=13),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(t=30, b=10, l=10, r=10), legend_title_text="",
                      title_font=dict(size=15, color="#111827"))
    fig.update_xaxes(gridcolor="#EEF0F3", zeroline=False)
    fig.update_yaxes(gridcolor="#EEF0F3", zeroline=False)
    if height:
        fig.update_layout(height=height)
    return fig


def card(label, value, sub=""):
    return (f'<div class="card"><div class="card-label">{label}</div>'
            f'<div class="card-value">{value}</div><div class="card-sub">{sub}</div></div>')


def section(title, sub=""):
    st.markdown(f'<div class="section-title">{title}</div>' + (f'<div class="section-sub">{sub}</div>' if sub else ""),
                unsafe_allow_html=True)


# ---------------------------------------------------------------- Mô hình và dữ liệu
@st.cache_resource
def load_model():
    # underthesea nạp mô hình tách từ lúc gọi lần đầu và không an toàn đa luồng.
    # Gọi ở đây vì cache_resource bắt các lượt chạy song song phải chờ nạp xong.
    preprocess("khởi tạo")
    return joblib.load(ROOT / "models" / "tfidf_lr_AB.joblib")


@st.cache_data
def load_predicted():
    return pd.read_csv(ROOT / "data" / "processed" / "shopee_predicted.csv")


@st.cache_data
def gold_scores():
    gold, temp = load_gold()
    p = load_model().predict_proba(gold[["text_prep", "text_raw"]])
    # Tập vàng lấy dư review 1–3 sao: trọng số đưa tỉ lệ sao về đúng toàn bộ review (notebook 09).
    star = pd.read_csv(ROOT / "data" / "processed" / "shopee_clean_all.csv").rating.value_counts(normalize=True)
    w = gold.rating.map(star / gold.rating.value_counts(normalize=True))
    pb = pd.read_csv(ROOT / "report" / "phobert" / "phobert_gold_pool_proba.csv").set_index("id").loc[gold.id]
    pb_not_pos = pb[["p_neg", "p_neu", "p_pos"]].values.argmax(1) != 2
    return gold[["rating", "label"]].assign(p_neg=p[:, 0], w=(w / w.sum()).values, pb_not_pos=pb_not_pos), temp


def predict(texts):
    model = load_model()
    X = pd.DataFrame({"text_prep": [preprocess(t) for t in texts], "text_raw": list(texts)})
    return model.predict_proba(X), X


MAX_ROWS = 2000


@st.cache_data(show_spinner=False, max_entries=8, ttl=3600)
def read_upload(data: bytes):
    for enc in ("utf-8-sig", "cp1258"):
        try:
            return pd.read_csv(io.BytesIO(data), encoding=enc, nrows=MAX_ROWS + 1)
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
    return None


@st.cache_data(show_spinner=False, max_entries=8, ttl=3600)
def analyze_upload(data: bytes, text_col: str):
    """Chạy mô hình + ABSA trên file tải lên; trả về bảng cùng cột với shopee_predicted.csv."""
    raw = read_upload(data)
    raw = raw[raw[text_col].notna() & (raw[text_col].astype(str).str.strip() != "")].head(MAX_ROWS)
    texts = raw[text_col].astype(str).tolist()
    P, X = predict(texts)
    df = pd.DataFrame({"text_clean": texts, "text_prep": X.text_prep.values,
                       "pred": np.array(load_model().classes_)[P.argmax(1)],
                       "p_neg": P[:, 0].round(3), "p_max": P.max(1)})
    asp = [absa(t, load_model()) for t in texts]
    for a in ASPECTS:
        df[a] = [d.get(a, "none") for d in asp]
    if "rating" in raw:
        df["rating"] = pd.to_numeric(raw["rating"], errors="coerce").values
    for c in ("category", "product"):
        if c in raw:
            df[c] = raw[c].astype(str).values
    return df


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
    """Trả về danh sách (loại, nội dung) để hiển thị thành thẻ."""
    recs = []
    if conf < HITL_TAU:
        recs.append(("warn", f"⚠️ Mô hình không chắc chắn (xác suất cao nhất {conf:.0%}): <b>chuyển nhân viên đọc lại</b>."))
    neg_asp = [a for a, s in aspects.items() if s == "neg"]
    for a in neg_asp:
        recs.append(("neg", f"{ASP_ICON[a]} <b>{ASP_VI[a]}:</b> {ACTIONS[a]}"))
    if label == "neg" and not neg_asp:
        recs.append(("neg", "Review tiêu cực chung: phản hồi công khai trong 24 giờ, hỏi rõ vấn đề qua tin nhắn."))
    if label == "pos" and not neg_asp:
        recs.append(("ok", "Cảm ơn khách; cân nhắc dùng review làm nội dung giới thiệu sản phẩm."))
    return recs


# ---------------------------------------------------------------- Header
st.markdown("""
<div class="hero">
  <h1>💬 Phân tích cảm xúc đánh giá sản phẩm</h1>
  <p>Phân loại cảm xúc review tiếng Việt, tách theo khía cạnh và gợi ý việc cần làm cho chủ shop và nhân viên CSKH.</p>
  <div class="tags">
    <span class="tag">TF-IDF + Logistic Regression</span>
    <span class="tag">Train: ViSD4SA + Shopee</span>
    <span class="tag">ABSA 4 khía cạnh</span>
    <span class="tag">Có người kiểm tra (HITL)</span>
  </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔎  Phân tích review", "🧪  What-if", "📊  Tổng quan"])

# ---------------------------------------------------------------- Tab 1
with tab1:
    if "review" not in st.session_state:
        st.session_state.review = SAMPLES["Khen lẫn chê"]

    left, right = st.columns([5, 7], gap="large")
    with left:
        with st.container(border=True):
            section("Nhập review", "Dán nội dung đánh giá của khách hoặc chọn một câu mẫu.")
            names = list(SAMPLES)
            for i in range(0, len(names), 2):
                for col, name in zip(st.columns(2), names[i:i + 2]):
                    if col.button(name, width="stretch"):
                        st.session_state.review = SAMPLES[name]
                        st.session_state.done = True
            txt = st.text_area("Review", key="review", height=150, label_visibility="collapsed")
            if st.button("Phân tích review", type="primary", width="stretch"):
                st.session_state.done = True

    with right:
        if st.session_state.get("done") and txt.strip():
            P, X = predict([txt])
            p = P[0]
            k = int(p.argmax())
            classes = load_model().classes_
            label = classes[k]
            asp = absa(txt, load_model())
            color = COLORS[LAB_VI[label]]

            c1, c2 = st.columns([1, 1])
            c1.markdown(f'<div class="card"><div class="card-label">Cảm xúc tổng thể</div>'
                        f'<span class="pill" style="background:{color}">{LAB_VI[label]}</span>'
                        f'<div class="card-sub">Độ tin cậy {p[k]:.0%}</div></div>', unsafe_allow_html=True)
            need_human = p[k] < HITL_TAU
            hcol = "#C99A1E" if need_human else "#0F766E"
            c2.markdown(f'<div class="card"><div class="card-label">Xử lý</div>'
                        f'<span class="pill" style="background:{hcol}">{"Cần người đọc" if need_human else "Tự động được"}</span>'
                        f'<div class="card-sub">Chuyển người khi xác suất cao nhất &lt; {HITL_TAU:.0%}</div></div>',
                        unsafe_allow_html=True)

            order = ["neg", "neu", "pos"]
            fig = go.Figure()
            for c in order:
                v = p[list(classes).index(c)]
                fig.add_bar(y=[""], x=[v], orientation="h", name=LAB_VI[c], marker_color=COLORS[LAB_VI[c]],
                            text=f"{LAB_VI[c]} {v:.0%}" if v >= 0.2 else (f"{v:.0%}" if v >= 0.07 else ""),
                            textposition="inside", textangle=0, insidetextanchor="middle",
                            hovertemplate=f"{LAB_VI[c]}: %{{x:.1%}}<extra></extra>")
            fig.update_layout(barmode="stack", showlegend=False, uniformtext=dict(minsize=11, mode="hide"),
                              xaxis=dict(range=[0, 1], tickformat=".0%", showgrid=False))
            st.plotly_chart(style_fig(fig, 120), width="stretch", config={"displayModeBar": False})

            section("Khía cạnh được nhắc tới")
            if asp:
                chips = ""
                for a, s in asp.items():
                    col = COLORS[LAB_VI[s]]
                    chips += (f'<span class="chip" style="color:{col};border-color:{col}33;background:{col}12">'
                              f'{ASP_ICON[a]} {ASP_VI[a]} · {LAB_VI[s]}</span>')
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.markdown('<span class="muted">Không tìm thấy khía cạnh nào trong từ điển.</span>', unsafe_allow_html=True)

            section("Khuyến nghị hành động")
            for kind, r in recommend(label, asp, p[k]):
                st.markdown(f'<div class="rec {kind}">{r}</div>', unsafe_allow_html=True)

            wc = word_contrib(X.text_prep[0], k)
            if len(wc):
                section(f"Từ ảnh hưởng nhiều nhất tới dự đoán “{LAB_VI[label]}”",
                        "Đóng góp tuyến tính (hệ số × TF-IDF): dương là đẩy về nhãn này, âm là kéo ra xa.")
                wc = wc.iloc[::-1]
                fig = go.Figure(go.Bar(x=wc["đóng góp"], y=wc["từ"].str.replace("_", " "), orientation="h",
                                       marker_color=[color if v > 0 else "#9CA3AF" for v in wc["đóng góp"]],
                                       hovertemplate="%{y}: %{x:+.3f}<extra></extra>"))
                st.plotly_chart(style_fig(fig, 40 + 32 * len(wc)), width="stretch", config={"displayModeBar": False})
        else:
            st.markdown('<div class="card" style="text-align:center;padding:60px 20px">'
                        '<div style="font-size:2.4rem">🔎</div>'
                        '<div class="section-title">Kết quả sẽ hiện ở đây</div>'
                        '<div class="muted">Nhập review bên trái rồi bấm <b>Phân tích review</b>.</div></div>',
                        unsafe_allow_html=True)

    st.write("")
    st.markdown('<span class="muted">📂 Muốn phân tích nhiều review cùng lúc? Tải file CSV ở tab <b>Tổng quan</b>.</span>',
                unsafe_allow_html=True)

# ---------------------------------------------------------------- Tab 2
with tab2:
    with st.container(border=True):
        section("1. Thay đổi câu chữ, dự đoán đổi thế nào?",
                "Thêm phủ định, ý trái chiều hoặc bỏ dấu để xem mô hình phản ứng ra sao.")
        c1, c2 = st.columns(2)
        base = c1.text_input("Câu gốc", "Sản phẩm đẹp, giao hàng nhanh")
        own = c2.text_input("Câu tự sửa", base + " nhưng giao chậm quá")
        variants = {
            "Câu gốc": base,
            "Thêm phủ định": base.replace("đẹp", "không đẹp").replace("nhanh", "không nhanh"),
            "Thêm ý trái chiều": base + " nhưng dùng 2 ngày đã hỏng",
            "Bỏ dấu (gõ không dấu)": strip_accents(base),
            "Tự sửa": own,
        }
        P, _ = predict(list(variants.values()))
        cls = load_model().classes_
        wi = pd.DataFrame(P, columns=[LAB_VI[c] for c in cls]).assign(**{"Biến thể": list(variants), "Câu": list(variants.values())})
        wi["Dự đoán"] = [LAB_VI[c] for c in cls[P.argmax(1)]]
        fig = go.Figure()
        for lab in ["Tiêu cực", "Trung lập", "Tích cực"]:
            fig.add_bar(y=wi["Biến thể"], x=wi[lab], orientation="h", name=lab, marker_color=COLORS[lab],
                        text=[f"{v:.0%}" if v >= 0.1 else "" for v in wi[lab]], textposition="inside",
                        customdata=wi["Câu"], hovertemplate="%{customdata}<br>" + lab + ": %{x:.0%}<extra></extra>")
        fig.update_layout(barmode="stack", xaxis=dict(range=[0, 1], tickformat=".0%"),
                          yaxis=dict(autorange="reversed"), legend=dict(orientation="h", y=1.15, x=0))
        st.plotly_chart(style_fig(fig, 300), width="stretch", config={"displayModeBar": False})
        st.dataframe(wi[["Biến thể", "Câu", "Dự đoán"]], hide_index=True, width="stretch")

    st.write("")
    with st.container(border=True):
        section("2. Ngưỡng cảnh báo và chi phí vận hành",
                "Nhập số liệu của shop để so sánh chi phí giữa các cách sàng lọc review.")
        gs, temp = gold_scores()
        if temp:
            st.warning("Đang dùng nhãn sao tạm thời (chưa đủ nhãn tay), nên phương án 'lọc theo sao' đúng tuyệt đối một cách giả tạo.")
        c1, c2, c3, c4 = st.columns(4)
        n = c1.number_input("Review mỗi tháng", 100, 100_000, 3000, step=500)
        c_read = c2.number_input("Chi phí đọc 1 review (đ)", 0, 50_000, 1_000, step=500)
        c_miss = c3.number_input("Thiệt hại khi bỏ sót 1 lời chê (đ)", 0, 1_000_000, 50_000, step=10_000)
        t = c4.slider("Ngưỡng P(tiêu cực)", 0.05, 0.95, 0.35, 0.05)
        is_neg = (gs.label == "neg").values
        w = gs.w.values

        def cost(flag):
            read, fn = w[flag].sum() * n, w[is_neg & ~flag].sum() * n
            return {"Review phải đọc": read, "Lời chê bị bỏ sót": fn,
                    "Recall tiêu cực": w[is_neg & flag].sum() / max(w[is_neg].sum(), 1e-9),
                    "Tổng chi phí/tháng (đ)": read * c_read + fn * c_miss}

        sao_13 = (gs.rating <= 3).values
        table = pd.DataFrame({"Đọc tay toàn bộ": cost(np.ones(len(gs), bool)),
                              "Lọc theo sao (1–2 sao)": cost((gs.rating <= 2).values),
                              "Lọc theo sao (1–3 sao)": cost(sao_13),
                              f"TF-IDF+LR (P ≥ {t:.2f})": cost(gs.p_neg.values >= t),
                              "Ghép: ≤ 3 sao hoặc PhoBERT không đoán tích cực": cost(sao_13 | gs.pb_not_pos.values)}).T
        cur = table.loc[f"TF-IDF+LR (P ≥ {t:.2f})"]
        best = table["Tổng chi phí/tháng (đ)"].idxmin()
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(card("Review phải đọc", f"{cur['Review phải đọc']:,.0f}", f"mỗi tháng, ngưỡng {t:.2f}"), unsafe_allow_html=True)
        m2.markdown(card("Lời chê bị bỏ sót", f"{cur['Lời chê bị bỏ sót']:,.0f}", "mỗi tháng"), unsafe_allow_html=True)
        m3.markdown(card("Recall tiêu cực", f"{cur['Recall tiêu cực']:.0%}", "TF-IDF+LR"), unsafe_allow_html=True)
        m4.markdown(card("Rẻ nhất", f"{table.loc[best, 'Tổng chi phí/tháng (đ)'] / 1e6:,.2f} tr", best), unsafe_allow_html=True)
        st.write("")
        st.dataframe(table.style.format({"Review phải đọc": "{:,.0f}", "Lời chê bị bỏ sót": "{:,.0f}",
                                         "Recall tiêu cực": "{:.0%}", "Tổng chi phí/tháng (đ)": "{:,.0f}"})
                     .highlight_min(subset=["Tổng chi phí/tháng (đ)"], color="#CCFBF1"),
                     width="stretch")
        ts = np.linspace(0.05, 0.95, 19)
        curve = pd.DataFrame([{"Ngưỡng": x, **cost(gs.p_neg.values >= x)} for x in ts])
        fig = px.line(curve, x="Ngưỡng", y="Tổng chi phí/tháng (đ)", markers=True, title="Tổng chi phí theo ngưỡng")
        fig.update_traces(line_color="#0F766E")
        fig.add_vline(x=t, line_dash="dot", line_color="#D64545", annotation_text="ngưỡng đang chọn")
        st.plotly_chart(style_fig(fig, 320), width="stretch", config={"displayModeBar": False})
        st.caption("Tính trên tập vàng, đã hiệu chỉnh theo tỉ lệ sao thực tế. Chi phí là giả định, hãy nhập số của shop bạn. "
                   "Mọi so sánh ở đây là phân tích thăm dò vì tập vàng đã được xem khi phát triển, "
                   "chưa được kiểm chứng trên dữ liệu mới.")

# ---------------------------------------------------------------- Tab 3
with tab3:
    with st.container(border=True):
        section("Nguồn dữ liệu",
                "Mặc định là 2.548 review Shopee của đồ án. Tải file CSV của shop lên để xem tổng quan trên dữ liệu đó.")
        up = st.file_uploader("Tải file CSV", type="csv", label_visibility="collapsed")
        st.caption(f"Cần một cột nội dung review (ưu tiên tên `text`). Có thể thêm cột `rating` (1–5 sao), "
                   f"`category` (ngành hàng), `product` (sản phẩm) để lọc và so sánh. File tối đa 5 MB; chỉ lấy {MAX_ROWS:,} dòng đầu tiên.")

        uploaded = False
        df = load_predicted()
        if up is not None:
            raw = read_upload(up.getvalue())
            text_cols = [] if raw is None else [c for c in raw.columns
                                                     if not pd.api.types.is_numeric_dtype(raw[c])]
            if not text_cols:
                st.error("Không đọc được file hoặc file không có cột chữ nào. Hãy lưu file dạng CSV UTF-8.")
            else:
                text_col = "text" if "text" in text_cols else st.selectbox(
                    "Cột chứa nội dung review", text_cols, help="File không có cột `text`, hãy chọn cột chứa review.")
                with st.spinner("Đang phân tích review trong file…"):
                    res = analyze_upload(up.getvalue(), text_col)
                if len(res):
                    df, uploaded = res, True
                    st.success(f"Đang hiển thị {len(df):,} review từ **{up.name}**"
                               + (f" (chỉ lấy {MAX_ROWS:,} dòng đầu)" if len(raw) > MAX_ROWS else "") + ".")
                else:
                    st.error(f"Cột `{text_col}` không có review nào.")

        has_rating = "rating" in df and df.rating.notna().any()
        filters = [c for c in ("category", "product") if c in df]
        if filters:
            cols = st.columns(len(filters))
            if "category" in filters:
                cats = cols[0].multiselect("Ngành hàng", sorted(df.category.dropna().unique()),
                                           placeholder="Tất cả ngành hàng")
                if cats:
                    df = df[df.category.isin(cats)]
            if "product" in filters:
                prods = cols[-1].multiselect("Sản phẩm", sorted(df["product"].dropna().unique()),
                                             placeholder="Tất cả sản phẩm")
                if prods:
                    df = df[df["product"].isin(prods)]

    st.write("")
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(card("Số review", f"{len(df):,}",
                     f"{df['product'].nunique()} sản phẩm" if "product" in df else (up.name if uploaded else "")),
                unsafe_allow_html=True)
    m2.markdown(card("Tỉ lệ tiêu cực", f"{(df.pred == 'neg').mean():.1%}" if len(df) else "–",
                     "theo dự đoán của mô hình"), unsafe_allow_html=True)
    if has_rating:
        m3.markdown(card("Sao trung bình", f"{df.rating.mean():.2f} ★", "trên thang 5"), unsafe_allow_html=True)
        m4.markdown(card("Review 4–5 sao bị đoán chê", f"{((df.rating >= 4) & (df.pred == 'neg')).sum():,}",
                         "lời chê dễ bị bỏ sót nếu chỉ lọc theo sao"), unsafe_allow_html=True)
    else:
        neg_asp = {ASP_VI[a]: int((df[a] == "neg").sum()) for a in ASPECTS}
        worst = max(neg_asp, key=neg_asp.get)
        m3.markdown(card("Cần người đọc", f"{(df.p_max < HITL_TAU).sum():,}",
                         f"xác suất cao nhất &lt; {HITL_TAU:.0%}"), unsafe_allow_html=True)
        m4.markdown(card("Khía cạnh bị chê nhiều nhất", worst if neg_asp[worst] else "–",
                         f"{neg_asp[worst]:,} lượt chê" if neg_asp[worst] else "chưa có lượt chê"),
                    unsafe_allow_html=True)
    st.write("")

    if not len(df):
        st.info("Nhóm đang chọn không có review nào.")
        st.stop()

    c1, c2 = st.columns([2, 3], gap="large")
    with c1, st.container(border=True):
        section("Cảm xúc tổng thể")
        sent = df.pred.map(LAB_VI).value_counts().reset_index()
        fig = px.pie(sent, names="pred", values="count", color="pred", color_discrete_map=COLORS, hole=0.55)
        fig.update_traces(textinfo="percent", sort=False)
        fig.update_layout(legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center"))
        st.plotly_chart(style_fig(fig, 320), width="stretch", config={"displayModeBar": False})
    with c2, st.container(border=True):
        section("Cảm xúc theo khía cạnh")
        long = df.melt(value_vars=ASPECTS, var_name="Khía cạnh", value_name="Cảm xúc")
        long = long[long["Cảm xúc"] != "none"]
        if len(long):
            long["Khía cạnh"] = long["Khía cạnh"].map(ASP_VI)
            long["Cảm xúc"] = long["Cảm xúc"].map(LAB_VI)
            agg = long.value_counts(["Khía cạnh", "Cảm xúc"]).reset_index()
            fig = px.bar(agg, y="Khía cạnh", x="count", color="Cảm xúc", color_discrete_map=COLORS, orientation="h",
                         labels={"count": "Số lượt nhắc", "Khía cạnh": ""},
                         category_orders={"Cảm xúc": ["Tiêu cực", "Trung lập", "Tích cực"]})
            fig.update_layout(legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"))
            st.plotly_chart(style_fig(fig, 320), width="stretch", config={"displayModeBar": False})
        else:
            st.markdown('<span class="muted">Không tìm thấy khía cạnh nào trong từ điển.</span>',
                        unsafe_allow_html=True)

    st.write("")
    with st.container(border=True):
        section("Top từ khóa trong review mô hình dự đoán tiêu cực",
                "Số review chê có chứa từ; di chuột để xem tỉ lệ chê. Từ khóa giúp tìm review, không thay việc đọc.")
        # File nhỏ: hạ số review tối thiểu để vẫn có từ khóa (mặc định 5 như notebook 10)
        kw = top_negative_keywords(df, min_docs=int(np.clip((df.pred == "neg").sum() // 20, 2, 5)))
        if len(kw):
            fig = px.bar(kw.iloc[::-1], x="Số review chê", y="Từ khóa", orientation="h",
                         hover_data=["Tỉ lệ chê"], color_discrete_sequence=[COLORS["Tiêu cực"]])
            fig.update_layout(yaxis_title="")
            st.plotly_chart(style_fig(fig, 440), width="stretch", config={"displayModeBar": False})
        else:
            st.markdown('<span class="muted">Nhóm đang chọn có quá ít review chê để thống kê từ khóa.</span>',
                        unsafe_allow_html=True)

    st.write("")
    with st.container(border=True):
        section("Review tiêu cực nổi bật", "50 review có xác suất tiêu cực cao nhất trong nhóm đang chọn.")
        meta = [c for c in ("category", "rating") if c in df]
        top = df[df.pred == "neg"].sort_values("p_neg", ascending=False)[meta + ["p_neg", "text_clean"] + ASPECTS].head(50)
        for a in ASPECTS:
            top[a] = top[a].map(lambda s: LAB_VI.get(s, ""))
        top = top.rename(columns={"category": "Ngành", "rating": "Sao", "text_clean": "Nội dung", **ASP_VI})
        st.dataframe(top, hide_index=True, width="stretch",
                     column_config={"p_neg": st.column_config.ProgressColumn("P(tiêu cực)", min_value=0, max_value=1,
                                                                             format="%.2f"),
                                    "Nội dung": st.column_config.TextColumn(width="large")})

    if uploaded:
        out = df.assign(cam_xuc=df.pred.map(LAB_VI), can_nguoi_doc=df.p_max < HITL_TAU,
                        **{ASP_VI[a]: df[a].map(lambda s: LAB_VI.get(s, "")) for a in ASPECTS})
        out = (out.drop(columns=["text_prep", "pred", "p_max"] + ASPECTS)
                  .rename(columns={"text_clean": "noi_dung", "p_neg": "p_tieu_cuc"})
                  .sort_values("p_tieu_cuc", ascending=False))
        st.download_button("⬇️  Tải kết quả phân tích (CSV)", out.to_csv(index=False).encode("utf-8-sig"),
                           "ket_qua_phan_tich.csv", "text/csv")
