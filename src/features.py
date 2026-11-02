"""Đặc trưng thủ công (feature engineering) tính trên văn bản GỐC.

Phải dùng văn bản gốc vì preprocess() đã viết thường và đổi teencode,
nên không còn đo được chữ HOA hay tỉ lệ có dấu.
"""
import re
import numpy as np
import pandas as pd

NEG_WORDS = {"không", "chẳng", "chả", "chưa", "đừng", "kém", "tệ", "ko", "k", "kh", "hông",
             "khong", "chang", "chua"}     # không dấu; bỏ "kem", "dung" vì trùng "kem", "dùng"
CONTRAST = {"nhưng", "mà", "tuy", "song", "nhma"}
VN_ACCENT = re.compile(r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]")
LETTER = re.compile(r"[^\W\d_]")

FEATURE_NAMES = ["n_words", "n_negation", "n_contrast", "n_exclaim", "upper_ratio", "accent_ratio"]


def text_features(s: str) -> dict:
    s = str(s)
    words = re.findall(r"\w+", s.lower())
    letters = LETTER.findall(s)
    n_let = max(len(letters), 1)
    return {
        "n_words": len(words),
        "n_negation": sum(w in NEG_WORDS for w in words),
        "n_contrast": sum(w in CONTRAST for w in words),            # câu có ý trái chiều
        "n_exclaim": s.count("!"),
        "upper_ratio": sum(c.isupper() for c in letters) / n_let,  # viết HOA khi bực
        "accent_ratio": len(VN_ACCENT.findall(s.lower())) / n_let, # gần 0 = gõ không dấu
    }


def feature_frame(texts) -> pd.DataFrame:
    return pd.DataFrame([text_features(t) for t in texts], columns=FEATURE_NAMES)


def features_array(texts) -> np.ndarray:
    """Dùng trong FunctionTransformer (phải là hàm có tên để joblib lưu được)."""
    f = feature_frame(texts)
    f["n_words"] = np.log1p(f["n_words"])       # độ dài lệch phải nặng -> lấy log
    return f.values
