"""ABSA bằng từ điển: tìm khía cạnh theo từ khóa, rồi chạy mô hình cảm xúc trên mệnh đề chứa nó.

So khớp trên văn bản đã chuẩn hóa nhưng CHƯA tách từ (preprocess(s, segment=False)).
Lưu ý preprocess đã đổi "ship" -> "giao hàng" và "shop" -> "cửa hàng".
"""
import re
import pandas as pd
from .preprocess import preprocess

ASPECT_KEYWORDS = {
    "giao_hang": ["giao hàng", "giao nhanh", "giao chậm", "giao đến", "giao tới", "shipper", "vận chuyển",
                  "đóng gói", "gói hàng", "nhận hàng", "nhận được hàng", "hộp", "móp", "bọc", "chống sốc"],
    "chat_luong": ["chất lượng", "chất liệu", "vải", "đường may", "bền", "hỏng", "hư", "lỗi", "mùi",
                   "pin", "đúng mô tả", "giống mô tả", "giống hình", "size", "form", "màu", "thơm",
                   "dùng", "xài", "mặc", "ăn", "vị", "hàng tốt", "hàng đẹp", "sản phẩm tốt", "sản phẩm đẹp"],
    "gia_ca": ["giá", "rẻ", "đắt", "mắc", "tiền", "đáng tiền", "sale", "voucher", "khuyến mãi", "xứng đáng"],
    "dich_vu": ["cửa hàng", "tư vấn", "nhắn tin", "trả lời", "đổi trả", "bảo hành", "thái độ",
                "hỗ trợ", "nhiệt tình", "phản hồi", "chăm sóc", "tặng", "quà"],
}
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


def absa(text: str, model) -> dict[str, str]:
    """Cảm xúc từng khía cạnh.

    model: pipeline trong models/ (nhận DataFrame có cột text_prep, text_raw).
    Nhiều mệnh đề cùng khía cạnh: lấy nhãn xuất hiện nhiều nhất, hòa thì ưu tiên neg
    (với chủ shop, bỏ sót lời chê tốn kém hơn).
    """
    found = detect_aspects(preprocess(text, segment=False))
    out = {}
    for a, clauses in found.items():
        X = pd.DataFrame({"text_prep": [preprocess(c, segment=True) for c in clauses], "text_raw": clauses})
        preds = list(model.predict(X))
        out[a] = max(["neg", "pos", "neu"], key=preds.count)
    return out
