r"""Bảng so sánh nhãn sao và nhãn gán lại cho báo cáo: report/relabel_summary.csv.

Chạy sau scripts/retrain_relabel.py:  .venv\Scripts\python.exe scripts/tong_hop_relabel.py
PhoBERT nhãn sao: report/phobert_cu/; PhoBERT nhãn mới: report/phobert/.
Số trên tập vàng là thăm dò (tập vàng đã được xem trước thí nghiệm này).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, recall_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data import LABELS, load_gold

TEN = {"AB": "Nhãn sao", "AB_relabel": "Nhãn gán lại"}


def metrics(y, p):
    return {"F1-macro": f1_score(y, p, labels=LABELS, average="macro"),
            "F1 neg": f1_score(y, p, labels=["neg"], average="macro"),
            "Recall neg": recall_score(y, p, labels=["neg"], average="macro")}


def main():
    rows = []
    r = pd.read_csv(ROOT / "report" / "relabel_retrain" / "results.csv")
    for x in r.itertuples():
        rows.append({"Mô hình": x.model, "Nhãn train": TEN[x.train],
                     "Tập": "Vàng Shopee (thăm dò)" if x.evaluation == "gold" else "ViSD4SA test",
                     "F1-macro": x.f1_macro, "F1 neg": x.f1_neg, "Recall neg": x.recall_neg})
    gold, _ = load_gold()
    for folder, ten in [("phobert_cu", "Nhãn sao"), ("phobert", "Nhãn gán lại")]:
        d = ROOT / "report" / folder
        g = pd.read_csv(d / "phobert_gold_pool_proba.csv").set_index("id").loc[gold.id]
        v = pd.read_csv(d / "phobert_visd_test_proba.csv")
        for tap, y, pr in [("Vàng Shopee (thăm dò)", gold.label.values, g), ("ViSD4SA test", v.label.values, v)]:
            p = np.array(LABELS)[pr[[f"p_{l}" for l in LABELS]].values.argmax(1)]
            rows.append({"Mô hình": "PhoBERT", "Nhãn train": ten, "Tập": tap, **metrics(y, p)})
    out = pd.DataFrame(rows).round(3)
    out.to_csv(ROOT / "report" / "relabel_summary.csv", index=False, encoding="utf-8-sig")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
