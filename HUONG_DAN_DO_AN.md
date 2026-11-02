# Hướng dẫn từng bước: Đồ án Phân tích Cảm xúc (bản theo rubric cuối khóa 23/10)

Cập nhật 02/11/2026. **Hạn chót: 23:59 ngày 11/11/2026.** Mục tiêu có file `.zip` hoàn chỉnh vào tối 10/11.

Tài liệu gốc: `huong_dan_tieu_luan_va_rubric_cuoi_khoa.pdf` (Ban Giảng huấn, 23/10/2026). Khi file này và PDF khác nhau thì **làm theo PDF**.

Mỗi ngày trong lộ trình có 5 phần: **Học gì**, **Làm gì**, **Tự kiểm tra**, **Đầu ra**, **Ghi vào phần nào** của báo cáo. Gõ lại code và giải thích được từng dòng, đừng chỉ copy cho chạy.

---

## 0. Những gì thay đổi so với kế hoạch 22/10

| Kế hoạch cũ | Rubric mới | Việc phải làm |
|---|---|---|
| Báo cáo 7 chương, ≤ 30 trang | **6 phần**, **≤ 45 trang** (không tính code) | Viết theo cấu trúc ở mục 3 |
| Không quy định công cụ | **Bắt buộc Quarto `.qmd` → PDF** (XeLaTeX) | Cài TinyTeX, dùng YAML ở mục 2 |
| Có slide, bảo vệ | **Không thuyết trình** | Bỏ slide; dồn thời gian cho demo |
| Dashboard chụp màn hình | Demo **online hoặc video 2–3 phút**, có **What-if** và **khuyến nghị hành động** | Ngày 7/11 |
| +10 điểm tự cào | Thưởng **+0,5–1,0** nếu dữ liệu thật của doanh nghiệp **hoặc người dùng thật thử nghiệm** | Nhờ 3–5 người dùng thử dashboard. Bỏ phương án cào bổ sung |
| Chương 1 giới thiệu chung | **Design Thinking:** Persona, Empathy Map, SMART, **ROI** | Ngày 9/11 viết, số liệu chi phí lấy từ ngày 5/11 |
| Tuning "thử 1–2 learning rate" | **≥ 3 thuật toán nâng cao, K-Fold CV, GridSearch/Optuna, Learning Curve** (phần III, 25%, nặng nhất) | Ngày 3–4/11 |
| Chỉ F1-macro, confusion matrix | Thêm **ROC-AUC, PR-AUC**, chi phí sai loại 1/loại 2, **SHAP**, **đạo đức AI** | Ngày 5/11 |
| Không có | **Feature engineering 2–3 đặc trưng mới**, từ điển dữ liệu, skewness, tương quan | Ngày 2/11 |
| Không có | Mục **Tuyên bố sử dụng AI** (bạn có dùng Claude); Turnitin ≤ 20% | Ghi ở Lời cảm ơn |
| Làm cá nhân | Đề cho **nhóm 3–4 người**; cá nhân cần giảng viên đồng ý | **Hỏi giảng viên ngay** nếu chưa hỏi |

### Trọng số chấm điểm (thang 10)

| Trụ cột | Trọng số | Phần báo cáo |
|---|---|---|
| I. Bài toán kinh doanh & Design Thinking | 15% | P1 |
| II. EDA & tiền xử lý | 20% | P3 |
| III. Mô hình hóa, tối ưu, chống quá khớp | **25%** | P4 |
| IV. Đánh giá, XAI, đạo đức AI | 15% | P5 |
| V. Sản phẩm mẫu (Web App / video) | 15% | P6 + `demo/` |
| VI. Trình bày & chất lượng mã nguồn | 10% | Toàn bài + notebook |
| Thưởng | +0,5–1,0 | Người dùng thật thử nghiệm |

P2 (CRISP-DM, thuật toán) không có dòng riêng trong rubric nhưng có trong cấu trúc bắt buộc; viết gọn 2–3 trang.

### Tiến độ hiện tại (02/11)

- **Đã xong trước đó:** EDA, làm sạch, chia theo sản phẩm, `src/preprocess.py`, guideline gán nhãn, baseline (`notebook/01`–`04`).
- **Chưa xong:** tập vàng (`labeling/gold_500_to_label.csv` chưa có nhãn nào). Tập vàng giảm còn **300 câu cảm xúc + 150 câu khía cạnh**; ABSA chỉ giữ cách từ điển.

### Đã chuẩn bị sẵn ngày 02/11 (Claude làm, bạn phải đọc hiểu)

Code cho các ngày 2/11 → 7/11 đã viết và chạy được. **Mọi notebook tự đọc nhãn tay** từ `labeling/gold_500.csv`, hoặc thẳng từ `gold_500_to_label.csv` nếu có ≥ 50 câu đã gán. Khi chưa đủ, chúng TẠM chấm bằng nhãn sao, nên **mọi con số "tập vàng" hiện tại chưa dùng được cho báo cáo.**

| File | Nội dung | Phần báo cáo |
|---|---|---|
| `src/data.py` | Hàm nạp dữ liệu và tập vàng dùng chung | |
| `src/features.py` | 6 đặc trưng mới (phủ định, từ đối lập, độ dài, "!", chữ HOA, tỉ lệ có dấu) | P3.3 |
| `src/aspects.py` | ABSA từ điển: tách mệnh đề → khía cạnh → cảm xúc | P5 |
| `notebook/05_eda_bosung` | Từ điển dữ liệu, skewness, cảm xúc theo ngành, tương quan Spearman, word cloud | P3.1–3.2 |
| `notebook/06_tuning` | GroupKFold, GridSearch (LR, LinearSVC), TF-IDF + đặc trưng, GroupKFold vs KFold, learning curve, lưu `models/` | P4 |
| `notebook/07_word2vec_tien_xu_ly` | Word2Vec + LR, 4 mức tiền xử lý, thí nghiệm không dấu | P3.3, P4, P5 |
| `notebook/08_phobert_colab` | **Chạy trên Colab**, xuất xác suất về `report/phobert/` | P4 |
| `notebook/09_danh_gia_xai` | Bảng chỉ số đầy đủ, bootstrap, PR curve, ma trận nhầm lẫn, **chi phí + ROI**, HITL, fairness, SHAP, xuất câu sai | P1.4, P5 |
| `notebook/10_absa_kinh_doanh` | Đánh giá ABSA, chạy trên 2.548 review, heatmap ngành × khía cạnh, lời chê ẩn, ứng viên top 3 vấn đề | P5, P6 |
| `app/dashboard.py` | Streamlit 3 tab: phân tích review + khuyến nghị, **What-if** (sửa câu, ngưỡng/chi phí), tổng quan | P6, demo |
| `report/bao_cao.qmd` + `references.bib` | Khung báo cáo 6 phần, đã gắn sẵn hình và bảng; chỗ `[VIẾT]` là phần bạn viết | Toàn bài |

**Kết quả tạm (nhãn sao) để bạn hình dung:**
- CV GroupKFold: TF-IDF+LR 0,628 ± 0,108; LinearSVC 0,626; baseline NB 0,574.
- Thêm đặc trưng mới **không giúp** (0,603), và đây vẫn là kết quả phải báo.
- KFold xáo ngẫu nhiên cho 0,692, tức cao giả khoảng 0,06 vì rò rỉ sản phẩm.
- Gõ không dấu làm F1 giảm từ 0,61 xuống 0,46; thêm Aug kéo lên 0,53.

**Những ô "Nhận xét (tự viết)"** trong notebook là phần bạn phải tự làm. Đó cũng là chỗ giảng viên chấm "mỗi biểu đồ có insight".

Lịch còn lại, thay cho các mục "Làm gì" ở mục 4 khi trùng:

| Ngày | Việc của bạn |
|---|---|
| 2/11 | Gán 150 câu vàng. Đọc `src/features.py`, notebook 05 và viết các ô nhận xét. Hỏi giảng viên (làm cá nhân, mã đề tài) |
| 3/11 | Gán đủ 300 câu + 150 câu khía cạnh, gán lại 60 câu để tính kappa. Lưu thành `labeling/gold_500.csv`. Chạy lại `03` (phần 2) → `04` → `06` → `07` → `09` → `10` (*Restart & Run All*). Đọc notebook 06 và trả lời các câu tự kiểm tra |
| 4/11 | Chạy `08_phobert_colab` trên Colab, giải nén vào `report/phobert/`, chạy lại `09`. Đọc notebook 07 |
| 5/11 | Đọc notebook 09: **sửa giả định chi phí** cho hợp lý, chọn 3 câu SHAP dễ giải thích, điền `nhom_loi` trong `report/error_analysis.csv` |
| 6/11 | Notebook 10: bổ sung từ khóa ABSA (dùng câu ngoài tập vàng), chọn và viết top 3 vấn đề kèm hành động |
| 7/11 | `streamlit run app/dashboard.py`, chụp màn hình, deploy Streamlit Cloud, quay video 2–3 phút, nhờ 3–5 người dùng thử |
| 8–10/11 | Viết các chỗ `[VIẾT]` trong `report/bao_cao.qmd`, cài TinyTeX, render PDF, đóng gói |

Render báo cáo (chạy trong thư mục `report/`; lần đầu cần `quarto install tinytex`):

```powershell
$env:QUARTO_PYTHON = "E:\Phân_tích_cảm_xúc\.venv\Scripts\python.exe"; quarto render bao_cao.qmd --to pdf
```

---

## 1. Dữ liệu (số liệu đã kiểm tra)

| Nguồn | Nội dung | Vai trò |
|---|---|---|
| **A: UIT-ViSD4SA** (`ViSD4SA/`) | 11.122 review điện thoại, nhãn cụm từ, 10 khía cạnh × 3 cảm xúc. Sau làm sạch 10.510 (train 7.344 / dev 1.046 / test 2.120) | Train 3 lớp và ABSA. Với tập vàng Shopee đây là **ngoài miền** |
| **B: `data/final_train_dataset.csv`** | 2.843 review Shopee, 32 sản phẩm, sao 1–5. Sau làm sạch 2.548 | 22 sản phẩm (1.794 câu) để train với nhãn yếu từ sao; 10 sản phẩm (746 câu) làm kho **tập vàng**; toàn bộ cho phân tích kinh doanh |
| **Aug: `data/aug_unaccented_reviews.jsonl`** | 1.347 review **không dấu**, 2 lớp, có thể do AI sinh. Giữ 1.205 câu sao khớp nhãn | **Chỉ train**, không bao giờ vào test |

Những điểm cần nhớ khi viết báo cáo:
- Shopee: pos 67%, neg 23%, neu chỉ 9,5%. Đoán "pos" hết được accuracy 0,689 nhưng F1-macro 0,272, nên **chỉ số chính là F1-macro**.
- Phải **chia theo sản phẩm** (`GroupShuffleSplit`, `random_state=42`) vì khăn ướt Bobby đã có 518 review.
- ViSD4SA chuyển nhãn cụm → nhãn câu: cùng cảm xúc thì lấy cảm xúc đó; lẫn lộn thì ưu tiên `GENERAL`, không có thì lấy đa số; hòa thì bỏ câu. 39% review có nhiều cảm xúc.
- ViSD4SA không có khía cạnh **giao hàng** (chỉ 51 review nhắc tới), nên khía cạnh này lấy bằng từ điển trên Shopee.
- Baseline hiện tại (nhãn sao): A → Shopee 0,53; B → Shopee 0,65; A+B → 0,61. F1 trong miền ViSD4SA khoảng 0,71–0,74.

Code làm sạch, chia tập, chuyển nhãn ViSD4SA nằm trong `notebook/02_clean_split.ipynb`; bảng các bước làm sạch ở `data/processed/cleaning_steps.csv`; ghi chú ở `report/notes_du_lieu.md`.

---

## 2. Quy cách nộp bài và Quarto

### Cấu trúc thư mục nộp

Nén thành `[Nhom_XX]_[MaDeTai]_[TenDeTai].zip` (hỏi giảng viên mã đề tài):

```
[Nhom_XX]_[MaDeTai]_[TenDeTai]/
├── bao_cao.qmd            # nguồn Quarto
├── bao_cao.pdf            # quarto render bao_cao.qmd --to pdf
├── references.bib
├── figures/               # ảnh do notebook xuất ra
├── code/                  # = notebook/ + src/ + app/, đã Restart & Run All
│   └── requirements.txt
├── data/                  # file nhỏ; file > 50MB thì để link Drive/Kaggle trong README
└── demo/                  # README.md chứa link Streamlit Cloud / HF Spaces và/hoặc video 2–3 phút
```

Trong repo hiện tại có thể giữ `notebook/`, chỉ đổi tên khi đóng gói.

### Cài đặt

```bash
quarto install tinytex
pip install shap optuna
```

Quarto chạy chunk Python bằng Jupyter của `.venv`. Nếu Quarto không tìm đúng Python, đặt biến `QUARTO_PYTHON` trỏ tới `.venv\Scripts\python.exe`.

### YAML (theo mẫu PDF, thêm danh mục bảng/hình và tài liệu tham khảo)

```yaml
---
title: "Phân tích cảm xúc đánh giá sản phẩm thương mại điện tử tiếng Việt theo khía cạnh"
subtitle: "Học phần Trí tuệ Nhân tạo Ứng dụng & Khoa học Dữ liệu"
author: "Nhóm XX: [Họ tên và MSSV các thành viên]"
date: "2026-11-11"
lang: vi
format:
  pdf:
    documentclass: article
    papersize: a4
    pdf-engine: xelatex
    toc: true
    toc-depth: 3
    number-sections: true
    colorlinks: true
    fontsize: 11pt
    lof: true
    lot: true
bibliography: references.bib
csl: apa.csl
execute:
  echo: false
  warning: false
---
```

### Quy tắc trình bày

- **Không chạy mô hình trong `.qmd`.** Notebook lưu hình (`figures/*.png`) và bảng (`report/*.csv`); file `.qmd` chỉ đọc lại. Render nhanh và không lỗi.
- Hình: `![Ma trận nhầm lẫn của PhoBERT trên tập vàng](figures/cm_phobert.png){#fig-cm}`, gọi bằng `@fig-cm`. Chú thích nằm **dưới** hình.
- Bảng: chunk có `#| label: tbl-main` và `#| tbl-cap: "..."`, chú thích nằm **trên** bảng.
- Mỗi hình và bảng phải có **một câu nhận xét ý nghĩa kinh doanh** ngay sau nó.
- Trích dẫn APA: `[@nguyen2020phobert]`. Cần trích ít nhất PhoBERT, ViSD4SA, scikit-learn, SHAP, CRISP-DM, nguồn dữ liệu Shopee.
- Trang đầu: trang bìa (trường, khoa, môn, đề tài, thành viên + MSSV, giảng viên, địa danh, năm học), **bảng phân công và % đóng góp**, mục lục, danh mục từ viết tắt, danh mục bảng/hình.
- **Tuyên bố sử dụng AI** (trong Lời cảm ơn): công cụ nào (Claude), dùng vào việc gì (gợi ý code, kiểm tra dữ liệu, góp ý cấu trúc), phần nào do bạn tự làm và tự kiểm chứng. Nhắc luôn bảng sản phẩm → ngành hàng do Claude gán và đã được bạn kiểm tra lại.

---

## 3. Cấu trúc 6 phần của báo cáo

Ước lượng trang để không vượt 45: P1 ~6, P2 ~3, P3 ~9, P4 ~9, P5 ~9, P6 ~6, phần đầu + tài liệu tham khảo ~3.

### P1. Giới thiệu & bài toán kinh doanh (15%), Empathize & Define

- **1.1 Bối cảnh và pain point:** một shop trên Shopee nhận hàng trăm review mỗi tháng; đọc tay tốn thời gian; review chê không được phản hồi kịp thì mất khách; số sao không phản ánh đúng nội dung (dẫn bảng chéo nhãn tay × số sao ở P3).
- **1.2 Persona + Empathy Map:** chọn 1–2 persona, ví dụ "chủ shop mỹ phẩm nhỏ, tự làm CSKH" và "chuyên viên quản lý ngành hàng của sàn". Empathy Map 4 ô (Nghĩ/Cảm, Thấy, Nói/Làm, Nghe) + Pain/Gain. Vẽ bằng bảng 2×2 hoặc hình.
- **1.3 Loại bài toán và mục tiêu SMART:** thuộc nhóm **Insight** (và một phần **Solution** – tự động phân loại). Ví dụ SMART: "Trong 1 tháng thử nghiệm, tự động gắn nhãn cảm xúc với F1-macro ≥ 0,70 trên review thật, phát hiện ≥ 85% review tiêu cực (Recall lớp neg), giảm 70% thời gian đọc review." KPI: F1-macro, Recall-neg, thời gian phản hồi review chê.
- **1.4 ROI:** công thức ở ngày 5/11. **Ghi rõ đâu là giả định** (lương, số review, giá trị một khách hàng).

### P2. Cơ sở lý thuyết & quy trình (10%)

- Sơ đồ CRISP-DM 6 bước, mỗi bước ghi notebook/ngày tương ứng của đồ án.
- Mỗi thuật toán 1 đoạn: nguyên lý + **vì sao chọn**. BoW/TF-IDF + NB (baseline nhanh), LR, LinearSVC (mạnh với văn bản thưa), Word2Vec (ngữ nghĩa từ), PhoBERT (ngữ cảnh, phủ định), ABSA từ điển, SHAP.

### P3. Khám phá & tiền xử lý dữ liệu (20%)

- **3.1 Từ điển dữ liệu:** bảng cho từng nguồn: tên cột, kiểu, ý nghĩa, ý nghĩa kinh doanh. Ví dụ `rating`: số sao 1–5, đại diện mức hài lòng tổng quát nhưng là nhãn yếu.
- **3.2 EDA + insight:** phân bố nhãn và độ lệch, độ dài review theo số sao, review theo ngành hàng, tương quan giữa các đặc trưng mới và số sao, bảng chéo nhãn tay × sao, word cloud pos/neg.
- **3.3 Tiền xử lý:** bảng 2.843 → 2.548, 5 ví dụ trước/sau, lý do chia theo sản phẩm, thí nghiệm có/không tiền xử lý, **feature engineering**, chống rò rỉ (khử trùng trước khi chia, kiểm tra trùng chéo, Aug chỉ train).

### P4. Thiết kế, huấn luyện & tối ưu mô hình (20%; rubric III 25%)

- Baseline: BoW+NB.
- Mô hình nâng cao (≥ 3): TF-IDF+LR, TF-IDF+LinearSVC, TF-IDF+đặc trưng mới+LR, Word2Vec+LR, PhoBERT.
- Thí nghiệm nguồn train: A, B, A+B, A+B+Aug.
- GroupKFold CV, GridSearch/Optuna, Learning Curve, đường loss PhoBERT.

### P5. Đánh giá chuyên sâu, XAI & đạo đức AI (20%; rubric IV 15%)

- Bảng chính, ROC-AUC/PR-AUC, khoảng tin cậy bootstrap, ma trận nhầm lẫn + chi phí, phân tích lỗi.
- SHAP summary + giải thích 3 câu cụ thể (1 đúng, 1 sai, 1 có phủ định).
- Fairness: F1 theo ngành hàng, F1 trên văn bản không dấu; quyền riêng tư; dữ liệu do AI sinh; Human-in-the-loop.
- Kết quả ABSA.

### P6. Sản phẩm mẫu, ứng dụng & hướng phát triển (15%)

- Kiến trúc và ảnh giao diện app; kịch bản sử dụng: nhập review → dự đoán → khuyến nghị.
- Top 3 vấn đề kinh doanh (số liệu + câu trích + hành động).
- Kế hoạch triển khai: tích hợp vào quy trình CSKH, theo dõi drift.
- Phản hồi người dùng thật (điểm thưởng).
- Hạn chế và hướng mở rộng.

---

## 4. Lộ trình 02/11 – 11/11

Mỗi tối dành 1–1,5 giờ gán nhãn cho tới khi đủ 300 câu (gán 150 câu buổi đầu, nghỉ giữa chừng để đỡ mỏi). Thứ tự trong `gold_500_to_label.csv` đã xáo ngẫu nhiên, nên **300 dòng đầu vẫn giữ tỉ lệ các mức sao** (sao 1–5: 59 / 38 / 31 / 60 / 112). Gán khía cạnh cho **150 dòng đầu** trong số có `gan_khia_canh = có`.

### 02/11 (T2): Tập vàng + EDA bổ sung + Feature engineering

**Học gì:** skewness (độ lệch), tương quan Spearman với biến thứ bậc (số sao), feature engineering cho văn bản.

**Làm gì:**
1. Gán 150 câu vàng (cảm xúc + khía cạnh). Che cột sao.
2. Trong `01_eda.ipynb` thêm:
   - Bảng từ điển dữ liệu cho 3 nguồn.
   - `scipy.stats.skew` cho số từ mỗi review; histogram có log-scale.
   - Biểu đồ phân bố nhãn theo ngành hàng (`product_category.csv`; nhớ kiểm tra lại ngành hàng).
3. Tạo `src/features.py`:

```python
import re
import numpy as np, pandas as pd

NEG_WORDS = ["không", "chẳng", "chả", "chưa", "đừng", "kém", "tệ"]
VN_ACCENT = re.compile(r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]")

def text_features(s: str) -> dict:
    words = s.lower().split()
    return {
        "n_words": len(words),
        "n_negation": sum(w in NEG_WORDS for w in words),
        "n_exclaim": s.count("!"),
        "upper_ratio": sum(c.isupper() for c in s) / max(len(s), 1),   # viết HOA khi bực
        "accent_ratio": len(VN_ACCENT.findall(s.lower())) / max(len(s), 1),  # gần 0 = không dấu
    }

def feature_frame(texts) -> pd.DataFrame:
    return pd.DataFrame([text_features(t) for t in texts])
```

4. Vẽ heatmap tương quan Spearman giữa các đặc trưng này và `rating` trên 2.548 câu Shopee, kèm nhận xét (ví dụ: review càng dài càng ít sao? viết hoa nhiều đi với 1 sao?).

**Tự kiểm tra:** Vì sao dùng Spearman chứ không phải Pearson với số sao? Đặc trưng nào có thể gây rò rỉ (ví dụ chứa thông tin lấy từ nhãn)?

**Đầu ra:** `src/features.py`, hình `figures/eda_*.png`, 150 câu vàng.
**Ghi vào:** P3.1, P3.2, P3.3.

### 03/11 (T3): CV + tuning + learning curve cho các mô hình cổ điển

**Học gì:** K-Fold vs **GroupKFold** (cùng sản phẩm không được nằm ở cả fold train lẫn fold val); GridSearchCV; learning curve cho biết thiếu dữ liệu hay mô hình quá phức tạp.

**Làm gì:** gán thêm 150 câu (đủ 300). Notebook `05_tuning.ipynb`:

```python
from sklearn.model_selection import GroupKFold, GridSearchCV, learning_curve
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

tr = pd.read_csv("data/processed/shopee_train.csv")       # B, có cột product
X, y, groups = tr.text_prep, tr.weak_label, tr["product"]
cv = GroupKFold(n_splits=5)

pipe = Pipeline([("vec", TfidfVectorizer(sublinear_tf=True)),
                 ("clf", LogisticRegression(max_iter=3000, class_weight="balanced"))])
grid = [
    {"vec__ngram_range": [(1, 1), (1, 2)], "vec__min_df": [1, 2, 3],
     "clf": [LogisticRegression(max_iter=3000, class_weight="balanced")], "clf__C": [0.3, 1, 3, 10]},
    {"vec__ngram_range": [(1, 1), (1, 2)], "vec__min_df": [1, 2, 3],
     "clf": [LinearSVC(class_weight="balanced")], "clf__C": [0.1, 0.3, 1, 3]},
]
gs = GridSearchCV(pipe, grid, cv=cv, scoring="f1_macro", n_jobs=-1)
gs.fit(X, y, groups=groups)
res = pd.DataFrame(gs.cv_results_)[["params", "mean_test_score", "std_test_score"]]
```

- Báo cáo **mean ± std F1-macro qua 5 fold**, không chỉ một con số.
- Lấy tham số tốt nhất, **huấn luyện lại trên A+B** rồi đánh giá trên ViSD4SA test và tập vàng. Lý do: ViSD4SA không có cột sản phẩm nên CV theo nhóm chỉ làm được trên B; ghi rõ điều này.
- Thêm mô hình **TF-IDF + đặc trưng mới**: `ColumnTransformer` ghép `TfidfVectorizer` với `StandardScaler` của `feature_frame`, rồi so với TF-IDF thuần. Đây là bằng chứng feature engineering "giúp mô hình chính xác hơn" (hoặc không, cũng phải báo).
- Learning curve:

```python
sizes, tr_sc, va_sc = learning_curve(gs.best_estimator_, X, y, groups=groups, cv=cv,
                                     scoring="f1_macro", train_sizes=np.linspace(0.1, 1, 6))
```

Vẽ 2 đường train/validation. Khoảng cách lớn → overfitting; cả hai thấp và sát nhau → underfitting; đường val còn đi lên → thêm dữ liệu sẽ có ích.

**Tự kiểm tra:** Nếu dùng `KFold` thường thì điểm CV cao hơn hay thấp hơn, vì sao? Chạy thử để kiểm chứng (một dòng trong báo cáo).

**Đầu ra:** bảng CV, tham số tốt nhất, `figures/learning_curve_*.png`, 300 câu vàng.
**Ghi vào:** P4.

### 04/11 (T4): Word2Vec, PhoBERT, thí nghiệm tiền xử lý. Mốc 1

**Học gì:** Word2Vec + mean pooling (mất trật tự từ); fine-tune PhoBERT (phải tách từ, `max_len`, learning rate, epoch, chọn checkpoint bằng dev).

**Làm gì:**
1. **Sáng: bật PhoBERT trên Colab/Kaggle trước** (chạy nền trong lúc làm việc khác). Cấu hình A+B trước.

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
tok = AutoTokenizer.from_pretrained("vinai/phobert-base")
model = AutoModelForSequenceClassification.from_pretrained("vinai/phobert-base", num_labels=3)
args = TrainingArguments("out", learning_rate=2e-5, num_train_epochs=4,
                         per_device_train_batch_size=32, eval_strategy="epoch",
                         save_strategy="epoch", logging_strategy="epoch",
                         load_best_model_at_end=True, metric_for_best_model="f1_macro",
                         seed=42, fp16=True)
# tokenize max_length=128, truncation=True; compute_metrics trả f1_macro
```

   - Thử 2 learning rate (`2e-5`, `3e-5`) trên dev = "tuning" cho PhoBERT. Ghi rõ vì sao không làm 5-fold (mỗi lần fine-tune mất nhiều GPU).
   - Lưu `trainer.state.log_history` để vẽ **đường loss train/val theo epoch** (learning curve của PhoBERT).
   - Lưu **xác suất dự đoán** (`softmax` của logits) trên tập vàng ra CSV để tính ROC/PR-AUC ngày 5/11.
2. Word2Vec + LR (code mẫu cũ: `Word2Vec(vector_size=200, window=5, min_count=2, sg=1, epochs=20, seed=42)`), kiểm tra `most_similar("tệ")`.
3. **Thí nghiệm tiền xử lý** với mô hình TF-IDF tốt nhất: (1) văn bản thô, (2) chuẩn hóa, (3) chuẩn hóa + tách từ, (4) = (3) + bỏ stopword nhưng giữ phủ định.
4. **Thí nghiệm không dấu:** bỏ dấu tập vàng, so mô hình train A+B với A+B+Aug.
5. Chạy lại `04_baseline.ipynb` với **nhãn tay** của 300 câu vàng.

**Nếu tới tối 4/11 PhoBERT chưa chạy được:** dùng `wonrax/phobert-base-vietnamese-sentiment` chạy thẳng trên tập vàng làm đại diện, và ghi vào hạn chế.

**Đầu ra:** bảng chính (hàng: mô hình; cột: F1 trong miền, F1 tập vàng, cho từng cấu hình train), bảng tiền xử lý, bảng không dấu.
**Ghi vào:** P3.3 (tiền xử lý), P4, P5.

### 05/11 (T5): Đánh giá chuyên sâu, XAI, đạo đức, ROI

**Học gì:** ROC-AUC vs PR-AUC (PR-AUC đáng tin hơn khi lớp hiếm như neu/neg); one-vs-rest cho bài 3 lớp; SHAP (đóng góp của từng từ vào dự đoán); chi phí sai loại 1/loại 2.

**Làm gì:** notebook `06_evaluation.ipynb`.

1. Chỉ số đầy đủ cho mô hình tốt nhất trên tập vàng:

```python
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score
from sklearn.preprocessing import label_binarize
classes = ["neg", "neu", "pos"]
Y = label_binarize(gold.sentiment, classes=classes)
print(classification_report(gold.sentiment, pred, digits=3))
print("ROC-AUC (OvR, macro):", roc_auc_score(Y, proba, average="macro"))
print("PR-AUC per class:", average_precision_score(Y, proba, average=None))
```

   Với LinearSVC dùng `decision_function` hoặc bọc `CalibratedClassifierCV` để có xác suất.

2. **Bootstrap 1.000 lần** cho F1-macro, báo khoảng 2,5%–97,5%. Tập vàng chỉ 300 câu nên khoảng này sẽ rộng; nói rõ khi so hai mô hình chênh nhau ít.
3. **Ma trận nhầm lẫn + chi phí.** Bài toán ưu tiên **Recall lớp neg**: bỏ sót một review chê (FN) = khách không được xử lý, có thể mất khách; báo nhầm (FP) = nhân viên mất 1 phút đọc. Đặt giả định, ví dụ `C_FN = 200.000đ` (giá trị đơn hàng tương lai bị mất), `C_FP = 2.000đ` (1 phút lương CSKH). Tính tổng chi phí của từng mô hình và của phương án "đọc tay toàn bộ".
4. **ROI** (đưa lên P1.4):

```
Tiết kiệm/tháng = (thời gian đọc tay − thời gian chỉ đọc review bị gắn neg) × lương/giờ
                  + (số review chê bắt được thêm × tỉ lệ giữ chân × giá trị khách hàng)
                  − chi phí do FN, FP
Chi phí        = triển khai ban đầu + vận hành (máy chủ, bảo trì)/tháng
ROI            = (Tiết kiệm − Chi phí) / Chi phí
```

   Dùng số FN/FP thật từ ma trận nhầm lẫn, phóng theo 1.000 review/tháng. Làm bảng **phân tích độ nhạy** (lương, giá trị khách hàng ±50%).

5. **SHAP** cho TF-IDF+LR:

```python
import shap
vec, clf = best.named_steps["vec"], best.named_steps["clf"]
Xg = vec.transform(gold.text_prep)
explainer = shap.LinearExplainer(clf, vec.transform(train_texts), feature_names=vec.get_feature_names_out())
sv = explainer(Xg)
shap.plots.beeswarm(sv[:, :, 0], max_display=20)    # lớp neg
shap.plots.waterfall(sv[i, :, 0])                    # giải thích 1 câu
```

   - Có từ nào là tên sản phẩm/thương hiệu lọt vào top không? Nếu có, đó là "lối tắt".
   - Chọn 3 câu: một câu đúng, một câu sai, một câu có phủ định ("không đẹp lắm"). Có thể thêm `shap.Explainer` với pipeline của PhoBERT nếu kịp.

6. **Đạo đức AI và fairness:**
   - F1-macro **theo ngành hàng** trên tập vàng; ngành nào bị đoán kém?
   - F1 trên văn bản **không dấu** (lấy từ thí nghiệm 4/11): người gõ không dấu, thường dùng điện thoại cũ hoặc lớn tuổi, có bị mô hình bất lợi không?
   - Quyền riêng tư: dữ liệu không có tên người dùng; câu trích trong báo cáo đã ẩn danh; không lưu review mà người dùng nhập vào app.
   - Dữ liệu Aug có thể do AI sinh: rủi ro mô hình học văn phong máy.
   - **Human-in-the-loop:** câu có xác suất cao nhất < 0,6 hoặc dự đoán neu → chuyển nhân viên đọc. Báo bao nhiêu % câu vàng rơi vào nhóm này và F1 của phần còn lại.
7. **Phân tích lỗi:** 20–30 câu sai, xếp nhóm: phủ định, mỉa mai, khía cạnh trái chiều, teencode/không dấu, câu chỉ mô tả.

**Tự kiểm tra:** Vì sao ROC-AUC có thể cao trong khi F1 lớp neu thấp? Nếu giảm ngưỡng cho lớp neg thì Recall và chi phí thay đổi ra sao?

**Đầu ra:** `figures/cm_*.png`, `figures/pr_curve.png`, `figures/shap_*.png`, bảng chi phí/ROI.
**Ghi vào:** P1.4, P5.

### 06/11 (T6): ABSA + phân tích kinh doanh. Mốc 2

1. **ABSA bằng từ điển** (`src/aspects.py`), so khớp trên văn bản đã chuẩn hóa **chưa tách từ**:

```python
ASPECTS = {
    "giao_hang": ["giao hàng", "giao", "shipper", "vận chuyển", "đóng gói", "gói hàng", "nhận hàng", "hộp", "móp"],
    "chat_luong": ["chất lượng", "chất liệu", "vải", "đường may", "bền", "hỏng", "hư", "lỗi", "mùi", "pin", "đúng mô tả", "size"],
    "gia_ca": ["giá", "rẻ", "đắt", "mắc", "tiền", "đáng tiền", "sale", "voucher"],
    "dich_vu": ["cửa hàng", "tư vấn", "nhắn tin", "trả lời", "đổi trả", "bảo hành", "thái độ", "hỗ trợ"],
}
```

   Lưu ý `preprocess` đã đổi "ship" → "giao hàng" và "shop" → "cửa hàng", nên từ điển dùng dạng đã đổi. Tách mệnh đề theo `.`, `,`, "nhưng", "mà"; mệnh đề chứa từ khóa thì chạy mô hình cảm xúc tốt nhất. Đánh giá trên 150 câu khía cạnh: F1 phát hiện khía cạnh, accuracy cảm xúc trên khía cạnh phát hiện đúng.
2. Chạy mô hình cảm xúc + ABSA trên cả 2.548 review → `data/processed/shopee_predicted.csv`.
3. Thống kê: tỉ lệ pos/neu/neg theo ngành hàng và sản phẩm; tỉ lệ tiêu cực theo khía cạnh; khía cạnh bị nhắc nhiều nhất trong review 1–2 sao; word cloud pos/neg và theo khía cạnh × neg.
4. **Top 3 vấn đề**, mỗi vấn đề có số liệu, 2–3 câu trích ẩn danh, một hành động cụ thể.

**Đầu ra:** `src/aspects.py`, `shopee_predicted.csv`, hình kinh doanh.
**Ghi vào:** P5 (kết quả ABSA), P6 (top 3 vấn đề).

### 07/11 (T7): Sản phẩm mẫu + demo + người dùng thật

Mức xuất sắc phần V yêu cầu: app chạy trơn tru, **người dùng nhập dữ liệu mới, chạy What-if, nhận kết quả tức thì kèm khuyến nghị**, có link online hoặc video 2–3 phút.

1. `app/dashboard.py` (Streamlit), 2 trang:
   - **Phân tích review:** ô nhập 1 review hoặc tải CSV nhiều review → nhãn cảm xúc + xác suất + khía cạnh + các từ đóng góp nhiều nhất (SHAP/hệ số LR) + **khuyến nghị**. Ví dụ: neg + giao hàng → "Liên hệ đơn vị vận chuyển, gửi xin lỗi kèm voucher"; độ tin cậy thấp → "Chuyển nhân viên kiểm tra".
   - **What-if:** sửa câu (thêm "không", bỏ dấu, đổi "giao nhanh" thành "giao chậm") và xem dự đoán đổi thế nào; thanh trượt ngưỡng neg → số review cần đọc tay và chi phí ước tính thay đổi theo.
   - **Tổng quan:** lọc theo ngành hàng/sản phẩm, tỉ lệ cảm xúc, cột chồng theo khía cạnh, bảng câu trích tiêu cực.
2. Dùng **TF-IDF+LR** trong app (nhẹ, chạy được trên Streamlit Community Cloud), lưu bằng `joblib`. PhoBERT nặng; nếu muốn đưa lên thì dùng Hugging Face Spaces.
3. Deploy lên Streamlit Community Cloud (cần repo GitHub; **không đẩy dữ liệu có thông tin cá nhân**). Quay video 2–3 phút: nhập review → kết quả → What-if → tổng quan.
4. **Điểm thưởng:** nhờ 3–5 người (ưu tiên người bán hàng online) dùng thử 10 phút, ghi phản hồi theo mẫu: dễ dùng (1–5), kết quả có đúng không, có dùng thật không, muốn thêm gì. Đưa bảng phản hồi vào P6.

**Đầu ra:** `app/`, link app, video, bảng phản hồi người dùng, ảnh chụp giao diện.
**Ghi vào:** P6.

### 08/11 (CN): Viết báo cáo P1, P2, P3

- Tạo `bao_cao.qmd` với YAML ở mục 2, render thử ngay một trang để chắc XeLaTeX và tiếng Việt chạy được.
- Viết trang bìa, bảng phân công, danh mục từ viết tắt.
- Viết P1 (Persona, Empathy Map, SMART, ROI), P2 (CRISP-DM), P3.
- Tạo `references.bib`, tải `apa.csl`.

### 09/11 (T2): Viết P4, P5, P6

- Mỗi hình/bảng có số, chú thích, câu nhận xét kinh doanh.
- Chương kết luận gộp vào P6.3: hạn chế (tập vàng 300 câu, một người gán, nhãn sao là nhãn yếu, 32 sản phẩm, Aug có thể do AI sinh, PhoBERT không CV) và hướng phát triển.

### 10/11 (T3): Hoàn thiện và đóng gói

1. **Restart & Run All** từng notebook theo thứ tự, sửa cell lỗi, xóa cell nháp, thêm markdown giải thích mục đích từng đoạn.
2. `quarto render bao_cao.qmd --to pdf`; kiểm tra **≤ 45 trang** không tính phụ lục code.
3. Đọc lại chính tả; kiểm tra chú thích bảng ở trên, hình ở dưới; mọi tài liệu đều được trích.
4. Viết Tuyên bố sử dụng AI.
5. `pip freeze > code/requirements.txt`; viết `README.md` gốc (cách chạy, thứ tự notebook, link dữ liệu, link demo).
6. Đóng gói `.zip` theo cấu trúc mục 2 và tick checklist mục 6.

### 11/11 (T4): Dự phòng. **Nộp trước 23:59**, nên nộp trước trưa.

---

## 5. Nếu chậm tiến độ, cắt theo thứ tự

1. SHAP cho PhoBERT (giữ SHAP cho LR).
2. Word2Vec (vẫn còn LR, LinearSVC, TF-IDF+đặc trưng, PhoBERT là đủ ≥ 3 mô hình nâng cao).
3. Trang Tổng quan của dashboard (giữ trang Phân tích review + What-if).
4. Thí nghiệm tiền xử lý 4 biến thể (giữ 2: thô và đầy đủ).
5. ABSA đánh giá trên 150 câu (giữ chạy trên toàn bộ để phân tích kinh doanh, ghi rõ chưa đánh giá định lượng).

**Không cắt:** tập vàng 300 câu, chia theo sản phẩm, GroupKFold + GridSearch, learning curve, ROC/PR-AUC + chi phí ma trận nhầm lẫn, SHAP cho LR, mục đạo đức, demo có What-if, video/link, Quarto PDF.

---

## 6. Checklist trước khi nộp (theo PDF)

- [ ] Báo cáo viết bằng `.qmd`, render thành công sang PDF
- [ ] ≤ 45 trang (không tính code); `echo: false`
- [ ] Trang bìa, bảng phân công + % đóng góp, mục lục, danh mục từ viết tắt, bảng, hình
- [ ] Mọi hình/bảng có số, tiêu đề và nhận xét kinh doanh
- [ ] Có cả `.qmd` và `.pdf`
- [ ] Notebook đã Restart & Run All, lưu cả output
- [ ] Link web app online hoặc video demo 2–3 phút
- [ ] Trích dẫn nguồn dữ liệu và tài liệu tham khảo (APA)
- [ ] Tuyên bố sử dụng AI
- [ ] File `.zip` đúng tên `[Nhom_XX]_[MaDeTai]_[TenDeTai].zip`
- [ ] Nộp trước 23:59 ngày 11/11/2026

---

## 7. Lỗi thường gặp

- Quên bỏ dòng rác "Tổng quan… Trợ lý AI tổng hợp" (văn bản do AI của sàn viết, không phải review).
- Chia ngẫu nhiên từng dòng, hoặc dùng `KFold` thường, khiến cùng một sản phẩm nằm ở cả train lẫn test/val.
- Đưa câu Aug vào tập test, hoặc gộp Aug 2 lớp với dữ liệu 3 lớp mà không nói rõ.
- Dùng số sao làm nhãn test rồi gọi đó là "độ chính xác".
- Xóa "không" khi bỏ stopword; quên tách từ trước khi đưa vào PhoBERT.
- Chỉ báo accuracy; chỉ báo ROC-AUC mà không có PR-AUC khi lớp lệch.
- Tuning trên chính tập vàng (tập vàng **chỉ dùng để đánh giá cuối cùng**; chọn tham số bằng CV trên train hoặc ViSD4SA dev).
- Biểu đồ không có nhận xét kinh doanh; bảng/hình không đánh số.
- ROI đưa số mà không ghi đâu là giả định.
- Chạy mô hình trong `.qmd` khiến render lâu và dễ lỗi.
- Đẩy dữ liệu hoặc khóa API lên GitHub công khai khi deploy app.
