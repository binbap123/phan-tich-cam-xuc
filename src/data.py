"""Nạp dữ liệu dùng chung cho các notebook 05 trở đi.

Mọi bảng trả về có cùng các cột: text_raw (văn bản gốc, còn hoa/thường và dấu câu),
text_prep (đã chuẩn hóa + tách từ), label (pos/neg/neu), group (sản phẩm, nếu có).
"""
import unicodedata
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
LAB = ROOT / "labeling"
ASPECTS = ["giao_hang", "chat_luong", "gia_ca", "dich_vu"]
LABELS = ["neg", "neu", "pos"]          # đúng thứ tự classes_ của sklearn


def _visd(split):
    d = pd.read_csv(P / f"visd_{split}.csv")
    return d.rename(columns={"text": "text_raw"}).assign(group="visd")


def load_sets():
    """Trả về dict: A, A_dev, A_test (ViSD4SA), B (Shopee train, nhãn sao), Aug (không dấu)."""
    B = (pd.read_csv(P / "shopee_train.csv")
         .rename(columns={"text_clean": "text_raw", "weak_label": "label", "product": "group"}))
    Aug = (pd.read_csv(P / "aug_train.csv")
           .drop(columns="label").rename(columns={"text": "text_raw", "weak_label": "label"})
           .assign(group="aug"))
    cols = ["text_raw", "text_prep", "label", "group"]
    return {"A": _visd("train")[cols + ASPECTS[1:]], "A_dev": _visd("dev")[cols + ASPECTS[1:]],
            "A_test": _visd("test")[cols + ASPECTS[1:]], "B": B[cols + ["rating"]], "Aug": Aug[cols]}


def _nfc(s):
    return s.map(lambda x: unicodedata.normalize("NFC", x))


def load_category():
    c = pd.read_csv(P / "product_category.csv", encoding="utf-8-sig")
    return c.assign(product=_nfc(c["product"]))     # file có 2 tên lưu dạng NFD


def load_gold(min_rows=50):
    """Tập vàng Shopee.

    Ưu tiên labeling/gold_500.csv; nếu chưa có thì đọc thẳng gold_500_to_label.csv.
    Nếu số câu đã gán < min_rows thì TẠM dùng cả kho vàng (746 câu) với nhãn sao.
    Trả về (DataFrame, is_temp).
    """
    pool = pd.read_csv(P / "shopee_gold_pool.csv")
    pool = pool.assign(product=_nfc(pool["product"])).merge(load_category(), on="product", how="left")
    meta = pool[["id", "product", "category", "rating", "text_clean", "text_prep", "weak_label"]]

    g = None
    for f in [LAB / "gold_500.csv", LAB / "gold_500_to_label.csv"]:
        if f.exists():
            g = pd.read_csv(f, encoding="utf-8-sig")
            g["sentiment"] = g.sentiment.astype("string").str.strip().str.lower()
            g = g[g.sentiment.isin(LABELS)]
            if len(g) >= min_rows:
                break
    if g is not None and len(g) >= min_rows:
        for a in ASPECTS:
            g[a] = g[a].astype("string").str.strip().str.lower()
        gold = g.drop(columns=["text"]).merge(meta, on="id")
        return gold.rename(columns={"text_clean": "text_raw", "sentiment": "label"}), False

    gold = meta.rename(columns={"text_clean": "text_raw", "weak_label": "label"})
    return gold, True
