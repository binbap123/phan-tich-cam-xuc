"""Kiểm tra bài theo checklist rubric. Chỉ đọc, không sửa file.

Chạy từ thư mục gốc dự án:  .venv/Scripts/python.exe harness/check.py
Thoát với mã 1 nếu còn mục chưa đạt.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / "report"
QMD = REP / "bao_cao.qmd"
PDF = REP / "bao_cao.pdf"
NOTEBOOKS = ["01_eda", "02_clean_split", "03_gold_labeling", "04_baseline", "05_eda_bosung", "06_tuning",
             "06b_thu_cai_tien", "07_word2vec_tien_xu_ly", "08_phobert_colab", "09_danh_gia_xai",
             "10_absa_kinh_doanh"]
results = []


def check(group, name, ok, detail=""):
    results.append(bool(ok))
    print(f"[{'ĐẠT' if ok else 'THIẾU'}] {group}: {name}" + (f" ({detail})" if detail else ""))


def pdf_pages():
    out = subprocess.run(["pdfinfo", PDF.name], cwd=REP, capture_output=True, text=True, encoding="utf-8")
    m = re.search(r"Pages:\s+(\d+)", out.stdout)
    return int(m.group(1)) if m else None


# Dữ liệu và nhãn
gold = pd.read_csv(ROOT / "labeling" / "gold_500.csv", encoding="utf-8-sig")
n_gold = gold.sentiment.isin(["pos", "neu", "neg"]).sum()
check("Dữ liệu", "300 câu vàng", n_gold >= 300, f"{n_gold} câu")
err = pd.read_csv(REP / "error_analysis.csv", encoding="utf-8-sig")
check("Dữ liệu", "phân nhóm lỗi", err.nhom_loi.notna().all(), f"{err.nhom_loi.notna().sum()}/{len(err)}")

# Notebook
for n in NOTEBOOKS:
    f = ROOT / "notebook" / f"{n}.ipynb"
    if not f.exists():
        check("Notebook", n, False, "không có file")
        continue
    cells = [c for c in json.loads(f.read_text(encoding="utf-8"))["cells"] if c["cell_type"] == "code"]
    noexec = sum(c.get("execution_count") is None and "".join(c["source"]).strip() != "" for c in cells)
    errors = sum(o.get("output_type") == "error" for c in cells for o in c.get("outputs", []))
    stale = sum("TẠM" in "".join(o.get("text", [])) for c in cells for o in c.get("outputs", []))
    check("Notebook", n, not (noexec or errors or stale), f"chưa chạy {noexec}, lỗi {errors}, nhãn tạm {stale}")

# Báo cáo
qmd = QMD.read_text(encoding="utf-8")
body = re.sub(r"<!--.*?-->", "", qmd, flags=re.S)
check("Báo cáo", "không còn [VIẾT]", "[VIẾT" not in body, f"còn {body.count('[VIẾT')} chỗ")
check("Báo cáo", "đã điền nhóm và thành viên", not re.search(r"Nhóm XX|\[Họ t[eê]n|\[MSSV\]", body))
check("Báo cáo", "có trang bìa đủ trường, khoa, giảng viên", all(k in body.lower() for k in ["trường", "khoa", "giảng viên"]))
check("Báo cáo", "tuyên bố AI nêu cả Claude và ChatGPT", "Claude" in body and ("ChatGPT" in body or "Codex" in body))
check("Báo cáo", "echo: false", re.search(r"echo:\s*false", qmd))
missing = [m for m in re.findall(r"\]\(\.\./figures/([^)]+)\)", body) if not (ROOT / "figures" / m).exists()]
check("Báo cáo", "đủ file hình", not missing, ", ".join(missing))
check("Báo cáo", "có ảnh giao diện app", "figures/app_" in body)
check("PDF", "có file PDF", PDF.exists())
if PDF.exists():
    pages = pdf_pages()
    check("PDF", "không quá 45 trang", pages and pages <= 45, f"{pages} trang")
    check("PDF", "mới hơn file .qmd", PDF.stat().st_mtime >= QMD.stat().st_mtime)

# Kết quả chính khớp bảng
main = pd.read_csv(REP / "main_results.csv", encoding="utf-8-sig", index_col=0)
check("Kết quả", "có PhoBERT trong bảng chính", "PhoBERT" in main.index)
check("Kết quả", "chi phí đã có chiến lược ghép",
      any(s.startswith("(d)") for s in pd.read_csv(REP / "cost_strategies.csv", encoding="utf-8-sig", index_col=0).index))

# Sản phẩm theo đề
app = (ROOT / "app" / "dashboard.py").read_text(encoding="utf-8")
check("Demo", "app có What-if", "What-if" in app)
check("Demo", "app có top từ khóa tiêu cực", "top_negative_keywords" in app)
demo = (ROOT / "demo" / "README.md").read_text(encoding="utf-8")
check("Demo", "có link app", "[dán link" not in demo)
check("Báo cáo", "có link app", "[dán link" not in body)
nb05 = json.loads((ROOT / "notebook" / "05_eda_bosung.ipynb").read_text(encoding="utf-8"))
wc_cells = ["".join(c["source"]) for c in nb05["cells"]
            if c["cell_type"] == "code" and "WordCloud(" in "".join(c["source"])]
du_3_lop = any(all(f'"{lab}"' in s for lab in ("neg", "neu", "pos")) for s in wc_cells)
co_hinh = (ROOT / "figures" / "eda_wordcloud.png").exists() and "eda_wordcloud.png" in body
check("Đề", "word cloud có đủ 3 lớp", du_3_lop and co_hinh,
      f"ô vẽ đủ neg/neu/pos: {du_3_lop}; hình có trong báo cáo: {co_hinh}")

# File nộp
for f in ["README.md", "requirements.txt", "report/references.bib", "report/apa.csl"]:
    check("File nộp", f, (ROOT / f).exists())

print(f"\nĐạt {sum(results)}/{len(results)} mục.")
sys.exit(0 if all(results) else 1)
