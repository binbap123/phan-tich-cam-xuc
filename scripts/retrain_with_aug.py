r"""So sanh A+B voi A+B+Aug, giu nguyen tham so va tap danh gia.

Chay tu thu muc goc: .venv\Scripts\python.exe scripts/retrain_with_aug.py
Them --shopee-only de so sanh B voi B+Aug.
Tai su dung text_prep da luu sau khi doi chieu noi dung voi JSONL goc.
Khong chon tham so hay thay model dashboard theo ket qua test.
"""
import argparse
import hashlib
import importlib.metadata
import json
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import accuracy_score, f1_score, recall_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data import LABELS, load_gold, load_sets


def text_key(text):
    text = unicodedata.normalize("NFD", str(text)).lower().replace("đ", "d")
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "", text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shopee-only", action="store_true")
    args = parser.parse_args()
    output_name = "shopee_retrain" if args.shopee_only else "aug_retrain"
    base_name = "B" if args.shopee_only else "AB"
    aug_name = base_name + "Aug"
    report = ROOT / "report" / output_name
    model_dir = ROOT / "models" / output_name
    report.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)
    source = ROOT / "data" / "aug_unaccented_reviews.jsonl"
    raw = pd.read_json(source, lines=True, dtype={"id": str})
    counts = {"raw": len(raw)}
    raw["text"] = (raw.review.str.replace(r'[*\t"]+', " ", regex=True)
                   .str.replace(r"\s+", " ", regex=True).str.strip())
    raw = raw.drop_duplicates("text")
    counts["deduplicated"] = len(raw)
    raw = raw[raw.text.str.split().str.len() >= 2].copy()
    keep = ((raw.rating <= 2) & (raw.label == "negative")) | ((raw.rating >= 4) & (raw.label == "positive"))
    raw = raw[keep].copy()
    raw["target"] = raw.label.map({"negative": "neg", "positive": "pos"})
    counts["valid_rating_label"] = len(raw)

    sets = load_sets()
    # Rebuild the Shopee cleaning steps and check that cached splits came from
    # the exact current CSV. Hold-out product assignments stay unchanged.
    shopee_source = ROOT / "data" / "final_train_dataset.csv"
    shopee = pd.read_csv(shopee_source).rename(columns={"prod": "product", "com": "text", "rat": "rating"})
    counts["shopee_raw"] = len(shopee)
    shopee["text"] = shopee.text.astype(str).str.normalize("NFC")
    shopee["product"] = shopee["product"].str.normalize("NFC")
    shopee["rating"] = shopee.rating.astype(int)
    shopee = shopee[~shopee.text.str.match(r"^\s*Tổng quan\s*\n\s*\d")].copy()
    shopee["text_clean"] = (shopee.text.str.replace(r"(?m)^\s*[^:\n]{3,25}:\s*", "", regex=True)
                            .str.replace(r"\s+", " ", regex=True).str.strip())
    shopee = shopee.drop_duplicates("text_clean")
    shopee = shopee[shopee.text_clean.str.split().str.len() >= 2].reset_index(drop=True)
    shopee["id"] = [f"shp_{i:04d}" for i in range(len(shopee))]
    shopee["weak_label"] = shopee.rating.map({1: "neg", 2: "neg", 3: "neu", 4: "pos", 5: "pos"})
    counts["shopee_clean"] = len(shopee)
    check_cols = ["id", "product", "rating", "text_clean", "weak_label"]
    clean_cache = pd.read_csv(ROOT / "data/processed/shopee_clean_all.csv")
    pd.testing.assert_frame_equal(shopee[check_cols], clean_cache[check_cols], check_dtype=False)
    for split_file in ["shopee_train.csv", "shopee_gold_pool.csv"]:
        split = pd.read_csv(ROOT / "data/processed" / split_file)
        expected = shopee.set_index("id").loc[split.id].reset_index()
        pd.testing.assert_frame_equal(split[check_cols], expected[check_cols], check_dtype=False)
    gold, temporary = load_gold()
    assert not temporary, "Can nhan tay that de danh gia."
    assert gold.id.is_unique
    assert not set(sets["B"].group) & set(gold["product"])
    pool = pd.read_csv(ROOT / "data" / "processed" / "shopee_gold_pool.csv")
    heldout = set(pool.text_clean.map(text_key))
    for name in ["A_dev", "A_test"]:
        heldout.update(sets[name].text_raw.map(text_key))
    raw = raw[~raw.text.map(text_key).isin(heldout)].copy()
    counts["after_holdout_filter"] = len(raw)

    cache = pd.read_csv(ROOT / "data" / "processed" / "aug_train.csv", dtype={"id": str})
    aug = raw.merge(cache[["id", "text", "rating", "weak_label", "text_prep"]],
                    on=["id", "text", "rating"], how="left", validate="one_to_one")
    assert aug.text_prep.notna().all(), "Cache khong khop JSONL: can tien xu ly lai."
    assert (aug.target == aug.weak_label).all(), "Nhan cache khong khop JSONL."
    aug = aug.rename(columns={"text": "text_raw", "target": "train_label"})
    aug["label"] = aug.train_label
    cols = ["text_raw", "text_prep", "label"]
    base = sets["B"][cols].copy() if args.shopee_only else pd.concat([sets["A"][cols], sets["B"][cols]], ignore_index=True)
    configs = {base_name: base, aug_name: pd.concat([base, aug[cols]], ignore_index=True)}
    evaluations = {"gold": gold, "visd_test": sets["A_test"]}
    for config, train in configs.items():
        assert not set(train.text_raw.map(text_key)) & set(gold.text_raw.map(text_key)), config
    print("DATA", json.dumps(counts), "train", {k: len(v) for k, v in configs.items()}, flush=True)
    print("AUG LABELS", aug.label.value_counts().to_dict(), "GOLD", len(gold), flush=True)

    templates = {
        "BoW+NB": "bow_nb_AB.joblib",
        "TF-IDF+LR": "tfidf_lr_AB.joblib",
        "TF-IDF+LinearSVC": "tfidf_svc_AB.joblib",
        "TF-IDF+features+LR": "tfidf_feat_lr_AB.joblib",
    }
    rows, predictions, parameters = [], {}, {}
    for name, filename in templates.items():
        template = joblib.load(ROOT / "models" / filename)
        parameters[name] = {k: repr(v) for k, v in template.get_params().items()}
        for config, train in configs.items():
            started = time.perf_counter()
            model = clone(template)
            if "clf__random_state" in model.get_params():
                model.set_params(clf__random_state=42)
            model.fit(train[["text_prep", "text_raw"]], train.label)
            elapsed = time.perf_counter() - started
            model_path = model_dir / f"{Path(filename).stem.removesuffix('_AB')}_{config}.joblib"
            joblib.dump(model, model_path)
            for split, test in evaluations.items():
                pred = model.predict(test[["text_prep", "text_raw"]])
                predictions[(name, config, split)] = pred
                rows.append({"model": name, "train": config, "evaluation": split,
                             "n_train": len(train), "n_eval": len(test),
                             "f1_macro": f1_score(test.label, pred, labels=LABELS, average="macro"),
                             "accuracy": accuracy_score(test.label, pred),
                             "recall_neg": recall_score(test.label, pred, labels=["neg"], average="macro"),
                             "fit_seconds": elapsed})
                # Check the saved artifact gives exactly the evaluated predictions.
                restored = joblib.load(model_path)
                assert np.array_equal(pred, restored.predict(test[["text_prep", "text_raw"]]))
            print(name, config, "gold F1", round(rows[-2]["f1_macro"], 4), "seconds", round(elapsed, 2), flush=True)

    results = pd.DataFrame(rows)
    results.to_csv(report / "results.csv", index=False, encoding="utf-8-sig")
    comparison = results.pivot(index=["model", "evaluation"], columns="train", values="f1_macro")
    comparison["delta_pp"] = 100 * (comparison[aug_name] - comparison[base_name])
    comparison.to_csv(report / "comparison.csv", encoding="utf-8-sig")
    for split, test in evaluations.items():
        out = pd.DataFrame({"id": test.id.values if "id" in test else np.arange(len(test)),
                            "label": test.label.values})
        for name in templates:
            for config in configs:
                out[f"{name}_{config}"] = predictions[(name, config, split)]
        out.to_csv(report / f"predictions_{split}.csv", index=False, encoding="utf-8-sig")

    # Paired bootstrap over held-out products, keeping correlated reviews together.
    rng = np.random.default_rng(42)
    groups = gold["product"].unique()
    blocks = [np.flatnonzero(gold["product"].to_numpy() == g) for g in groups]
    samples = [np.concatenate([blocks[j] for j in rng.integers(0, len(blocks), len(blocks))])
               for _ in range(1000)]
    y = gold.label.to_numpy()
    intervals = []
    for name in templates:
        before, after = predictions[(name, base_name, "gold")], predictions[(name, aug_name, "gold")]
        delta = np.array([f1_score(y[ix], after[ix], labels=LABELS, average="macro", zero_division=0)
                          - f1_score(y[ix], before[ix], labels=LABELS, average="macro", zero_division=0)
                          for ix in samples])
        intervals.append({"model": name, "delta_pp": comparison.loc[(name, "gold"), "delta_pp"],
                          "ci95_low_pp": 100 * np.percentile(delta, 2.5),
                          "ci95_high_pp": 100 * np.percentile(delta, 97.5)})
    pd.DataFrame(intervals).to_csv(report / "paired_product_bootstrap.csv", index=False)
    inputs = [source, shopee_source, ROOT / "data/processed/aug_train.csv", ROOT / "labeling/gold_500.csv"]
    inputs += [ROOT / "data/processed" / f for f in ["visd_train.csv", "visd_test.csv", "shopee_train.csv", "shopee_gold_pool.csv"]]
    meta = {"completed_utc": datetime.now(timezone.utc).isoformat(), "seed": 42,
            "counts": counts, "aug_labels": aug.label.value_counts().to_dict(),
            "train_counts": {k: len(v) for k, v in configs.items()},
            "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
            "versions": {p: importlib.metadata.version(p) for p in ["scikit-learn", "pandas", "numpy", "joblib"]},
            "parameters_from_existing_models": parameters,
            "notes": ["Fixed existing hyperparameters; no tuning on evaluation sets.",
                      "Cached segmentation reused only after matching raw JSONL text, ID, rating and label.",
                      "No PhoBERT retraining; dashboard model unchanged.",
                      "Gold previously inspected during project development; this is a controlled ablation, not a new blind test.",
                      "Bootstrap uses products (10 groups), so uncertainty estimates are exploratory."]}
    (report / "run_metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf8")
    print(comparison.round(4).to_string(), flush=True)
    print(pd.DataFrame(intervals).round(3).to_string(index=False), flush=True)
    print("SAVED", report, flush=True)


if __name__ == "__main__":
    main()
