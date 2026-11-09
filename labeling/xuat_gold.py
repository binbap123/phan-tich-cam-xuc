"""Xuất nhãn từ gold_gan_nhan.xlsx sang gold_500.csv để các notebook đọc.

Chạy từ thư mục gốc dự án:  .venv\\Scripts\\python.exe labeling\\xuat_gold.py
Không dùng Save As CSV của Excel: máy dùng dấu ";" làm phân cách sẽ cho ra file sai.
"""
import sys
from pathlib import Path

import pandas as pd

LAB = Path(__file__).parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else LAB / "gold_gan_nhan.xlsx"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else LAB / "gold_500.csv"

ASPECTS = ["giao_hang", "chat_luong", "gia_ca", "dich_vu"]
HOP_LE = {"sentiment": {"pos", "neg", "neu"}, **{a: {"pos", "neg", "neu", "none"} for a in ASPECTS}}

d = pd.read_excel(SRC, sheet_name="gan_nhan", dtype=str)
for c in HOP_LE:
    d[c] = d[c].str.strip().str.lower()

# Dừng lại nếu có giá trị sai, để không ghi đè file cũ bằng dữ liệu lỗi.
loi = [(c, int(s), v) for c in HOP_LE for s, v in zip(d.stt, d[c])
       if pd.notna(v) and v not in HOP_LE[c]]
if loi:
    sys.exit(f"Có {len(loi)} giá trị sai (cột, stt, giá trị): {loi[:10]}")

d.to_csv(OUT, index=False, encoding="utf-8-sig")

n = d.sentiment.notna().sum()
dong_kc = d[d.gan_khia_canh.notna()].head(150)
n_kc = dong_kc[ASPECTS].notna().all(axis=1).sum()
print(f"Cảm xúc: {n}/{len(d)} câu; khía cạnh: {n_kc}/150 câu")
print(d.sentiment.value_counts().to_dict())
print("Đã ghi", OUT)

# File gán lại 60 câu (tính kappa), nếu đã có.
RELABEL = SRC.parent / "gold_relabel_60.xlsx"
if RELABEL.exists():
    r = pd.read_excel(RELABEL, dtype=str)
    r["sentiment"] = r.sentiment.str.strip().str.lower()
    sai = r[r.sentiment.notna() & ~r.sentiment.isin(HOP_LE["sentiment"])]
    if len(sai):
        sys.exit(f"gold_relabel_60.xlsx có {len(sai)} giá trị sai: {sai.sentiment.tolist()[:10]}")
    r.to_csv(OUT.parent / "gold_relabel_60.csv", index=False, encoding="utf-8-sig")
    print(f"Gán lại: {r.sentiment.notna().sum()}/{len(r)} câu")
