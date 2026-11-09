"""ABSA bằng từ điển: tìm khía cạnh theo từ khóa, rồi chạy mô hình cảm xúc trên mệnh đề chứa nó.

So khớp trên văn bản đã chuẩn hóa nhưng CHƯA tách từ (preprocess(s, segment=False)).
Lưu ý preprocess đã đổi "ship" -> "giao hàng" và "shop" -> "cửa hàng".
"""
import re
from collections import Counter
import pandas as pd
from .preprocess import preprocess, remove_stopwords

ASPECT_KEYWORDS = {
    "giao_hang": ["giao hàng", "giao nhanh", "giao chậm", "giao đến", "giao tới", "shipper", "vận chuyển",
                  "đóng gói", "gói hàng", "nhận hàng", "nhận được hàng", "hộp", "móp", "bọc", "chống sốc",
                  "giao lâu", "giao quá lâu", "giao hơi lâu", "giao trễ", "thời gian giao", "vỡ", "bể"],
    "chat_luong": ["chất lượng", "chất liệu", "vải", "đường may", "bền", "hỏng", "hư", "lỗi", "mùi",
                   "pin", "đúng mô tả", "giống mô tả", "giống hình", "size", "form", "màu", "thơm",
                   "dùng", "xài", "mặc", "ăn", "vị", "hàng tốt", "hàng đẹp", "sản phẩm tốt", "sản phẩm đẹp",
                   "rách", "bung chỉ", "chỉ thừa", "phai màu", "xước", "trầy"],
    "gia_ca": ["giá", "rẻ", "đắt", "mắc", "tiền", "đáng tiền", "sale", "voucher", "khuyến mãi", "xứng đáng"],
    "dich_vu": ["cửa hàng", "tư vấn", "nhắn tin", "trả lời", "đổi trả", "bảo hành", "thái độ",
                "hỗ trợ", "nhiệt tình", "phản hồi", "chăm sóc", "tặng", "quà",
                "giao sai", "giao nhầm", "giao thiếu", "giao không đúng", "giao thiếu hàng"],
}

# Mô hình cảm xúc hay đoán sai mệnh đề ngắn ("giao hàng chậm" ra pos vì "giao hàng" gắn với lời khen).
# Mệnh đề chứa một trong các cụm dưới đây được gán neg cho khía cạnh đó, không hỏi mô hình.
# Danh sách lấy từ review trong tập train, không dùng tập vàng.
NEG_CUES = {
    "giao_hang": ["chậm", "lâu", "trễ", "móp", "móp méo", "méo", "bẹp", "vỡ", "bể", "ướt"],
    "chat_luong": ["hỏng", "hư", "lỗi", "kém", "tệ", "rách", "xước", "trầy", "trày", "bung chỉ", "phai màu",
                   "giặt ra màu", "dễ hỏng", "dễ hư", "dễ rách", "dễ bung", "không bền", "chỉ thừa"],
    "gia_ca": ["đắt", "mắc", "không đáng", "không xứng đáng"],
    "dich_vu": ["giao sai", "giao nhầm", "giao thiếu", "giao không đúng", "không trả lời", "không phản hồi",
                "không hỗ trợ", "không nhiệt tình", "chậm", "lâu", "thái độ kém", "thái độ tệ"],
}
_CUE_PATTERNS = {a: re.compile(r"(?<!\w)(" + "|".join(map(re.escape, sorted(kws, key=len, reverse=True))) + r")(?!\w)")
                 for a, kws in NEG_CUES.items()}
_NEGATORS = {"không", "chưa", "chẳng", "chả", "sợ", "lo", "tưởng"}   # xét 2 từ ngay trước cụm chê
_NOT_CUE_PREFIX = {"dễ", "chống", "bán", "thắc", "khăn", "hết", "đỡ"}   # "chống xước", "bán đắt", "thắc mắc", "khăn ướt"
_NOT_COMPLAINT_AFTER = re.compile(r"\s+(dài|nay|năm|rồi mới)(?!\w)")
_PATTERNS = {a: re.compile(r"(?<!\w)(" + "|".join(map(re.escape, kws)) + r")(?!\w)")
             for a, kws in ASPECT_KEYWORDS.items()}
_SPLIT = re.compile(r"\s*[.,!?;\n]+\s*|\s+(?=nhưng\s|mà\s|tuy\s|song\s)")


def split_clauses(text_norm: str) -> list[str]:
    return [c.strip() for c in _SPLIT.split(text_norm) if c and len(c.strip().split()) >= 1]


def detect_aspects(text_norm: str) -> dict[str, list[str]]:
    """{khía cạnh: [các mệnh đề nhắc tới nó]} trên văn bản đã chuẩn hóa."""
    found = {}
    for clause in split_clauses(text_norm):
        for a, pat in _PATTERNS.items():
            if pat.search(clause):
                found.setdefault(a, []).append(clause)
    return found


def neg_cue(aspect: str, clause: str) -> bool | None:
    """True: có lời chê rõ. False: chỉ có dạng phủ định như "không bị móp". None: không có cụm nào."""
    result = None
    for m in _CUE_PATTERNS[aspect].finditer(clause):
        before = clause[:m.start()].split()[-2:]
        if (_NEGATORS & set(before) or (before and before[-1] in _NOT_CUE_PREFIX)
                or _NOT_COMPLAINT_AFTER.match(clause, m.end())):
            result = False
            continue
        return True
    return result


def _clause_label(aspect: str, clause: str, pred: str) -> str:
    cue = neg_cue(aspect, clause)
    if cue:
        return "neg"
    # Mô hình dễ thấy từ chê rồi đoán neg dù câu đang phủ định nó.
    return "neu" if cue is False and pred == "neg" else pred


def absa(text: str, model) -> dict[str, str]:
    """Cảm xúc từng khía cạnh.

    model: pipeline trong models/ (nhận DataFrame có cột text_prep, text_raw).
    Mệnh đề có lời chê rõ (NEG_CUES) được gán neg, dạng phủ định không bị gán neg,
    các mệnh đề còn lại do mô hình quyết định.
    Nhiều mệnh đề cùng khía cạnh: lấy nhãn xuất hiện nhiều nhất, hòa thì ưu tiên neg
    (với chủ shop, bỏ sót lời chê tốn kém hơn).
    """
    found = detect_aspects(preprocess(text, segment=False))
    out = {}
    for a, clauses in found.items():
        X = pd.DataFrame({"text_prep": [preprocess(c, segment=True) for c in clauses], "text_raw": clauses})
        preds = [_clause_label(a, c, p) for c, p in zip(clauses, model.predict(X))]
        out[a] = max(["neg", "pos", "neu"], key=preds.count)
    return out


def top_negative_keywords(df, n=15, min_docs=5, min_neg_rate=0.5):
    """Top từ khóa tiêu cực: từ có trong nhiều review chê và nghiêng rõ về phía chê.

    df cần cột text_prep và pred. Mỗi từ đếm tối đa 1 lần trong 1 review.
    """
    all_c, neg_c = Counter(), Counter()
    for text, lab in zip(df.text_prep, df.pred):
        words = {w for w in remove_stopwords(text).split() if any(c.isalpha() for c in w)}
        all_c.update(words)
        if lab == "neg":
            neg_c.update(words)
    rows = [{"Từ khóa": w.replace("_", " "), "Số review chê": c, "Tỉ lệ chê": round(c / all_c[w], 3)}
            for w, c in neg_c.items() if c >= min_docs and c / all_c[w] >= min_neg_rate]
    cols = ["Từ khóa", "Số review chê", "Tỉ lệ chê"]
    return pd.DataFrame(rows, columns=cols).sort_values("Số review chê", ascending=False).head(n)


# Từ xuất hiện dày ở cả 3 lớp, giữ lại thì che mất các từ mang thông tin trong word cloud
WORDCLOUD_BO = {"không", "hàng", "cửa_hàng", "sản_phẩm", "mua", "giao", "giao_hàng", "rất", "quá", "lắm",
                "nhưng", "nhiều", "như", "còn", "đã", "để", "thì", "mà", "và", "có", "là", "của", "cho"}


def word_freq(texts):
    """Tần suất từ cho word cloud: bỏ từ dừng, dấu câu, từ chung; đổi "_" thành khoảng trắng."""
    c = Counter()
    for text in texts:
        c.update(w.replace("_", " ") for w in remove_stopwords(text).split()
                 if w not in WORDCLOUD_BO and any(ch.isalpha() for ch in w))
    return c
