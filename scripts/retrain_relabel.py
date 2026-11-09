r"""Train lai voi 250 nhan tay thay nhan sao trong Shopee train, so voi model hien tai.

Chay tu thu muc goc: .venv\Scripts\python.exe scripts/retrain_relabel.py
- Nhan: Claude de xuat, nguoi dung duyet trong labeling/train_250_duyet.xlsx
  (nhan_cuoi trong = dong y voi claude_nhan). Cau "rac" bi bo khoi train.
- Giu nguyen tham so cua model da luu, khong tune.
- Tap vang da duoc xem truoc khi lam thi nghiem nay: so lieu tren vang la tham do.
"""
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support, recall_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.aspects import absa
from src.data import ASPECTS, LABELS, load_gold, load_sets

# Nguoi dung ghi chu thich vao cot nhan_cuoi thay vi nhan; doc la neg, can nguoi dung xac nhan.
DIEN_GIAI = {"chủ yếu chê dịch vụ": "neg"}


def final_labels():
    d = pd.read_excel(ROOT / "labeling" / "train_250_duyet.xlsx", dtype=str)
    cuoi = d.nhan_cuoi.str.strip().str.lower()
    cuoi = cuoi.map(lambda v: DIEN_GIAI.get(v, v) if isinstance(v, str) else v)
    d["label_cuoi"] = cuoi.fillna(d.claude_nhan)
    d["nguon"] = np.where(d.nhan_cuoi.isna(), "dong_y_claude", "nguoi_dung_sua")
    d.loc[d.nhan_cuoi.str.strip().str.lower().isin(DIEN_GIAI), "nguon"] = "dien_giai_ghi_chu"
    d["bo"] = d.ghi_chu_claude.eq("rac") & d.nhan_cuoi.isna()
    assert d.label_cuoi.isin(LABELS).all(), d.label_cuoi.unique()
    out = d[["id", "claude_nhan", "nhan_cuoi", "label_cuoi", "nguon", "bo", "ghi_chu"]]
    out.to_csv(ROOT / "labeling" / "train_250_nhan.csv", index=False, encoding="utf-8-sig")
    return out


def main():
    report = ROOT / "report" / "relabel_retrain"
    model_dir = ROOT / "models" / "relabel_retrain"
    report.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)

    lab = final_labels()
    sets = load_sets()
    gold, temp = load_gold()
    assert not temp
    shp = pd.read_csv(ROOT / "data" / "processed" / "shopee_train.csv")
    # load_sets() nay đã trả B nhãn mới; dựng lại B nhãn sao gốc để so sánh.
    sets["B"] = shp.rename(columns={"text_clean": "text_raw", "weak_label": "label", "product": "group"})
    assert lab.id.isin(shp.id).all() and len(shp) == len(sets["B"])
    # Nhãn được gán theo vị trí sang sets["B"]: bảo đảm hai bảng cùng thứ tự dòng.
    assert shp.id.is_unique and (sets["B"].text_raw.values == shp.text_clean.values).all()
    m = shp[["id"]].merge(lab, on="id", how="left")
    B_new = sets["B"].copy()
    B_new["label"] = m.label_cuoi.fillna(B_new.label).values
    B_new = B_new[~m.bo.fillna(False).astype(bool).values]
    # Ban Shopee train moi cho PhoBERT tren Colab (cung dinh dang shopee_train.csv).
    shp_new = shp.assign(weak_label=m.label_cuoi.fillna(shp.weak_label).values)[~m.bo.fillna(False).astype(bool).values]
    shp_new.to_csv(ROOT / "data" / "processed" / "shopee_train_relabel.csv", index=False, encoding="utf-8-sig")

    cols = ["text_raw", "text_prep", "label"]
    configs = {"AB": pd.concat([sets["A"][cols], sets["B"][cols]], ignore_index=True),
               "AB_relabel": pd.concat([sets["A"][cols], B_new[cols]], ignore_index=True)}
    evaluations = {"gold": gold, "visd_test": sets["A_test"]}
    meta = {"n_relabel": int((~lab.bo).sum()), "n_drop_rac": int(lab.bo.sum()),
            "label_changed_vs_weak": int((m.label_cuoi.notna() & (m.label_cuoi != shp.weak_label)).sum()),
            "nguon": lab.nguon.value_counts().to_dict(), "dien_giai": DIEN_GIAI,
            "B_labels_old": sets["B"].label.value_counts().to_dict(), "B_labels_new": B_new.label.value_counts().to_dict(),
            "notes": ["Gold labels were seen before this experiment; gold numbers are exploratory.",
                      "Parameters are copied from the saved AB models; nothing was tuned."]}
    print(json.dumps(meta, ensure_ascii=False), flush=True)

    templates = {"BoW+NB": "bow_nb_AB.joblib", "TF-IDF+LR": "tfidf_lr_AB.joblib",
                 "TF-IDF+LinearSVC": "tfidf_svc_AB.joblib", "TF-IDF+features+LR": "tfidf_feat_lr_AB.joblib"}
    rows, preds, fitted = [], {}, {}
    for name, filename in templates.items():
        template = joblib.load(ROOT / "models" / filename)
        for config, train in configs.items():
            model = clone(template)
            if "clf__random_state" in model.get_params():
                model.set_params(clf__random_state=42)
            model.fit(train[["text_prep", "text_raw"]], train.label)
            fitted[(name, config)] = model
            if config == "AB_relabel":
                joblib.dump(model, model_dir / filename.replace("_AB", "_AB_relabel"))
            for split, test in evaluations.items():
                p = model.predict(test[["text_prep", "text_raw"]])
                preds[(name, config, split)] = p
                f1s = f1_score(test.label, p, labels=LABELS, average=None)
                rows.append({"model": name, "train": config, "evaluation": split, "n_train": len(train),
                             "f1_macro": f1s.mean(), "f1_neg": f1s[0], "f1_neu": f1s[1], "f1_pos": f1s[2],
                             "accuracy": accuracy_score(test.label, p),
                             "recall_neg": recall_score(test.label, p, labels=["neg"], average="macro")})
        print(name, "done", flush=True)
    res = pd.DataFrame(rows)
    res.to_csv(report / "results.csv", index=False, encoding="utf-8-sig")
    comp = res.pivot(index=["model", "evaluation"], columns="train", values="f1_macro")
    comp["delta_pp"] = 100 * (comp["AB_relabel"] - comp["AB"])
    comp.to_csv(report / "comparison.csv", encoding="utf-8-sig")

    # Bootstrap theo san pham (10 nhom) tren vang: tham do.
    rng = np.random.default_rng(42)
    blocks = [np.flatnonzero(gold["product"].to_numpy() == g) for g in gold["product"].unique()]
    y = gold.label.to_numpy()
    ci = []
    for name in templates:
        a, b = preds[(name, "AB", "gold")], preds[(name, "AB_relabel", "gold")]
        ds = []
        for _ in range(2000):
            idx = np.concatenate([blocks[i] for i in rng.integers(0, len(blocks), len(blocks))])
            ds.append(f1_score(y[idx], b[idx], labels=LABELS, average="macro")
                      - f1_score(y[idx], a[idx], labels=LABELS, average="macro"))
        ci.append({"model": name, "delta_pp": 100 * comp.loc[(name, "gold"), "AB_relabel"] - 100 * comp.loc[(name, "gold"), "AB"],
                   "ci95_low_pp": 100 * np.percentile(ds, 2.5), "ci95_high_pp": 100 * np.percentile(ds, 97.5)})
    pd.DataFrame(ci).to_csv(report / "paired_product_bootstrap.csv", index=False, encoding="utf-8-sig")

    # ABSA (code hien tai, gom luat R3) tren 150 cau vang co nhan khia canh: tham do.
    ga = gold[(gold.gan_khia_canh == "có") & gold[ASPECTS].notna().all(axis=1)].copy()
    absa_rows = []
    for config in configs:
        model = fitted[("TF-IDF+LR", config)]
        pr = ga.text_raw.map(lambda s: absa(s, model))
        for a in ASPECTS:
            true_has = ga[a] != "none"
            lab_a = pr.map(lambda d: d.get(a, "none"))
            p, r, f, _ = precision_recall_fscore_support(true_has, lab_a != "none", average="binary", zero_division=0)
            both = true_has & (lab_a != "none")
            absa_rows.append({"model": f"TF-IDF+LR {config}", "aspect": a, "n_true": int(true_has.sum()),
                              "precision": p, "recall": r, "f1_detect": f,
                              "acc_sentiment": (ga[a][both] == lab_a[both]).mean() if both.any() else np.nan})
    pd.DataFrame(absa_rows).round(3).to_csv(report / "absa_eval_rule.csv", index=False, encoding="utf-8-sig")
    json.dump(meta, open(report / "run_metadata.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(comp.round(4).to_string())


if __name__ == "__main__":
    main()
