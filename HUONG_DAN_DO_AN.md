Set-Content .gitignore ".venv/`n.ipynb_checkpoints/`n__pycache__/" -Encoding utf8# Hướng dẫn từng bước: Đồ án Phân tích Cảm xúc (bản điều chỉnh theo dataset đã có)

Cập nhật 22/10/2026. Hạn chót vẫn là 11/11, mục tiêu có bản nộp hoàn chỉnh vào 9/11.

Mỗi ngày trong lộ trình đều có 5 phần: **Học gì** (khái niệm cần hiểu), **Làm gì** (code, có mẫu), **Tự kiểm tra** (câu hỏi bạn phải trả lời được trước khi qua ngày sau), **Đầu ra**, và **Ghi vào báo cáo**. Đừng copy code cho chạy là xong. Gõ lại, in kết quả trung gian ra và giải thích được từng dòng thì mới học được, mà lúc bảo vệ giảng viên cũng sẽ hỏi đúng những chỗ đó.

---

## 0. Những gì thay đổi so với kế hoạch cũ

Kế hoạch cũ giả định bạn phải tự cào Tiki và tải thêm bộ B (AIVIVN). Giờ bạn đã có sẵn hai file, nên vai trò các nguồn dữ liệu đổi như sau:

| Nguồn | Nội dung thực tế | Vai trò mới |
|---|---|---|
| **A: UIT-ViSD4SA** (`ViSD4SA/`, đã tải) | 11.122 review điện thoại (train 7.785 / dev 1.112 / test 2.225), nhãn theo cụm từ, 10 khía cạnh × 3 cảm xúc | Huấn luyện 3 lớp và ABSA. Với tập vàng Shopee, đây là **ngoài miền thật** (điện thoại → đa ngành hàng) |
| **B: `data/final_train_dataset.csv`** | 2.843 review Shopee có dấu, 32 sản phẩm, sao 1–5. Sau làm sạch còn **2.548** | **Thay cho bộ B và dữ liệu cào.** Chia theo sản phẩm: 22 sản phẩm (~1.850 review) để huấn luyện với nhãn yếu từ số sao; 10 sản phẩm (~700 review) để lấy **tập vàng** gán nhãn tay. Dùng toàn bộ cho phân tích kinh doanh |
| **Aug: `data/aug_unaccented_reviews.jsonl`** | 1.348 review **không dấu**, nhãn 2 lớp, nhiều câu có vẻ do AI sinh | **Chỉ đưa vào tập huấn luyện**, không bao giờ vào test. Dùng cho thí nghiệm "mô hình có chịu được văn bản không dấu không" |

Hệ quả:
- **Bỏ 2 ngày cào dữ liệu** (23–24/10 cũ). Thời gian dư dùng để học kỹ tiền xử lý và gán nhãn tập vàng chậm mà chắc.
- **Không cần AIVIVN.** Thí nghiệm "huấn luyện trên A, B, A+B" vẫn giữ nguyên, B giờ là phần train của Shopee.
- **Điểm +10 tự cào:** nếu file CSV do bạn (hoặc nhóm) tự cào, mô tả cách cào trong Chương 3 là được tính. Nếu tải của người khác, hỏi giảng viên ngay hôm nay. Nếu giảng viên không chấp nhận, xem mục "Phương án cào bổ sung" ở cuối file.
- **Khía cạnh "giao hàng" không có trong ViSD4SA.** Khía cạnh này sẽ lấy từ từ điển khía cạnh chạy trên dữ liệu Shopee, nơi có rất nhiều câu "giao hàng nhanh, đóng gói cẩn thận". Đây là một điểm hay để viết trong báo cáo.

### Những con số đã kiểm tra trên dữ liệu của bạn

- CSV có 120 dòng là rác giao diện ("Tổng quan 4.9 (3034 đánh giá)… Trợ lý AI tổng hợp…"), 275 dòng trùng, và 93 review cực ngắn.
- Sau khi làm sạch còn 2.548 review: pos 1.709 (67%), neg 597, neu 242 (chỉ 9,5%). Lớp trung lập rất ít, nên **bắt buộc báo F1-macro**.
- Phân bố sản phẩm lệch: riêng khăn ướt Bobby đã có 518 review. Vì vậy phải **chia theo sản phẩm**, không chia ngẫu nhiên từng dòng.
- Baseline nhanh mình chạy thử (train 22 sản phẩm, test 10 sản phẩm còn lại, nhãn từ sao): BoW+LR đạt F1-macro 0,667, TF-IDF+LR 0,667, TF-IDF+NB 0,489. Đây là mốc để bạn so khi tự làm.
- JSONL: giữ được 1.206 câu có sao và nhãn khớp nhau (sao 1–2 + negative, sao 4–5 + positive). Bỏ các câu 3 sao vì nhãn ở đó lộn xộn: 118 cái gán negative, 13 cái gán positive.

### Kết quả kiểm tra ViSD4SA (22/10)

- **Định dạng:** mỗi dòng có dạng `{"text": ..., "labels": [[start, end, "ASPECT#POLARITY"], ...]}`, trung bình 3,2 cụm mỗi review.
- **Không trùng với Shopee:** không câu nào trùng. Giữa train và test chỉ có 2 câu trùng, giữa train và dev 1 câu, xóa đi là xong.
- **Khía cạnh (tập train):** GENERAL 5.637, PERFORMANCE 4.799, BATTERY 3.943, FEATURES 2.788, CAMERA 2.182, SER&ACC 1.875, DESIGN 1.497, PRICE 995, SCREEN 962, STORAGE 93.
  - Nhóm Chất lượng rất dày.
  - Giá cả (~1.000 cụm) và Dịch vụ (~1.900 cụm) đủ để học.
  - **Giao hàng gần như không có:** chỉ 51 review nhắc tới.
- **Cụm hỏng:** 122 cụm có `end` vượt quá độ dài câu, nhiều nhất 25 ký tự. Cách xử lý là cắt `end = min(end, len(text))`.
- **Văn bản chưa chuẩn NFC:** 227 câu. **Phải cắt cụm theo vị trí TRƯỚC khi chuẩn hóa NFC**, vì chuẩn hóa làm đổi độ dài chuỗi nên vị trí sẽ lệch.
- **Nhãn cả câu** theo quy tắc ở ngày 24/10 (tính trên cả 3 tập):

  | Nhãn | Số câu | Tỉ lệ |
  |---|---|---|
  | pos | 6.638 | 61% |
  | neg | 3.456 | 32% |
  | neu | 419 | **chỉ 3,8%** |
  | hòa (bỏ đi) | 384 | |
  | không có nhãn (bỏ đi) | 225 | |

  Khoảng 38% review có cả khen lẫn chê, nên quy tắc gộp nhãn rất quan trọng và phải ghi trong báo cáo.

- **Thí nghiệm nhanh** (TF-IDF+LR, chưa tách từ; nhãn Shopee lấy từ sao):

  | Train trên | Test ViSD4SA (trong miền) | Shopee 10 sản phẩm giữ lại |
  |---|---|---|
  | A (ViSD4SA) | 0,704 | **0,551** |
  | B (Shopee) | 0,498 | 0,667 |
  | A+B | **0,710** | **0,668** |

  F1 giảm từ 0,70 xuống 0,55 khi chuyển miền. Nguyên nhân chính là lớp neu (F1 chỉ 0,12): ViSD4SA hầu như không có câu trung lập cả bài. Gộp A+B cho kết quả tốt ở cả hai miền. Đây chính là câu chuyện cho Chương 5.

---

## 1. Chuẩn bị môi trường (làm ngay 22/10)

Máy bạn đã có Python 3.11, scikit-learn, matplotlib, seaborn, wordcloud. Còn thiếu:

```bash
pip install underthesea pyvi gensim emoji streamlit plotly jupyter
```

PhoBERT thì chạy trên **Google Colab hoặc Kaggle** (GPU miễn phí). Không cần cài torch hay transformers trên máy.

Cấu trúc thư mục nên dùng (để nguyên 2 file gốc trong `data/`, không sửa trực tiếp):

```
Phân_tích_cảm_xúc/
├── ViSD4SA/             # train/dev/test.jsonl (đã có), chỉ đọc
├── data/                 # 2 file gốc, chỉ đọc
│   └── processed/        # file đã làm sạch, do code sinh ra
├── notebooks/            # 01_eda, 02_preprocess, 03_baseline, ...
├── src/
│   ├── preprocess.py     # hàm tiền xử lý dùng chung
│   └── aspects.py        # từ điển khía cạnh
├── labeling/             # tập vàng + hướng dẫn gán nhãn
├── app/dashboard.py
└── report/
```

Tạo repo git ngay từ đầu (`git init`) và commit mỗi tối. Ghi `random_state=42` ở mọi chỗ có ngẫu nhiên.

---

## 2. Lộ trình từng ngày

### Chặng 1: Dữ liệu và tập vàng (22/10 – 27/10)

#### 22/10 (T5): Hiểu dữ liệu
**Học gì:** EDA (khám phá dữ liệu) để làm gì; nhãn yếu (weak label) khác nhãn vàng (gold label) ra sao; lệch lớp ảnh hưởng thế nào tới accuracy.

**Làm gì:**
1. Hỏi giảng viên hai việc: dataset tải về có được tính điểm tự cào không, và phụ lục có tính vào giới hạn 30 trang không.
2. ViSD4SA đã có trong `ViSD4SA/`. Tự mở 10 dòng đầu, dùng `text[start:end]` in ra từng cụm cùng nhãn của nó để hiểu cách gán nhãn. Đối chiếu số liệu của bạn với mục "Kết quả kiểm tra ViSD4SA" ở trên.
3. Notebook `01_eda.ipynb` cho cả 3 nguồn: số dòng, phân bố nhãn, độ dài (số từ), số trùng, 10 sản phẩm nhiều review nhất.

```python
import pandas as pd
df = pd.read_csv("data/final_train_dataset.csv").rename(
    columns={"prod": "product", "com": "text", "rat": "rating"})
print(df.rating.value_counts().sort_index())
print(df.groupby("product").rating.agg(["size", "mean"]).sort_values("size"))
df["n_words"] = df.text.str.split().str.len()
df.n_words.hist(bins=50)
```

4. Tự làm bảng `product → ngành hàng` cho 32 sản phẩm (mỹ phẩm, mẹ & bé, thời trang, điện tử, thể thao, sách – văn phòng phẩm, đồ ăn) và lưu thành `data/processed/product_category.csv`. Phần kinh doanh sẽ cần bảng này.

**Tự kiểm tra:** Nếu mô hình đoán "pos" cho mọi câu thì accuracy bao nhiêu, F1-macro bao nhiêu? (Gợi ý: accuracy ~67%, F1-macro chỉ ~0,27.) Vì sao số sao không phải là nhãn cảm xúc chuẩn? Hãy tìm 3 ví dụ 4–5 sao mà nội dung lại chê.

**Đầu ra:** `notes_du_lieu.md`, gồm bảng nhãn của 3 nguồn và câu trả lời của giảng viên.

#### 23/10 (T6): Tiền xử lý tiếng Việt
**Học gì:** Unicode NFC và NFD (cùng chữ "ố" nhưng có thể là 1 hay 2 ký tự); teencode; emoji mang cảm xúc; vì sao tiếng Việt cần **tách từ** ("hài_lòng" là một từ, không phải hai); stopword và **vì sao không được xóa từ phủ định** ("không", "chưa", "chẳng").

**Làm gì:** viết `src/preprocess.py`.

```python
import re, unicodedata
import emoji
from underthesea import word_tokenize

TEENCODE = {"k": "không", "ko": "không", "kh": "không", "hok": "không",
            "dc": "được", "đc": "được", "sp": "sản phẩm", "mik": "mình",
            "mn": "mọi người", "ok": "ổn", "oke": "ổn", "s": "sao",
            "vs": "với", "nx": "nữa", "ship": "giao hàng", "shop": "cửa hàng"}
# tự bổ sung thêm khi đọc dữ liệu, mục tiêu 50–100 mục

def normalize_text(s: str) -> str:
    s = unicodedata.normalize("NFC", str(s)).lower()
    s = emoji.demojize(s, delimiters=(" EMO_", " "))   # 😂 -> EMO_face_with_tears_of_joy
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"(.)\1{2,}", r"\1", s)                  # "thommm" -> "thom"
    tokens = [TEENCODE.get(t, t) for t in re.findall(r"\w+|[^\w\s]", s)]
    return " ".join(tokens)

def preprocess(s: str, segment=True) -> str:
    s = normalize_text(s)
    return word_tokenize(s, format="text") if segment else s
```

Chạy thử trên 20 câu thật trong CSV, in ra trước/sau rồi tự sửa từ điển teencode.

**Tự kiểm tra:** Vì sao phải chuẩn hóa NFC trước khi so khớp từ điển? Nếu xóa "không" thì câu "không đẹp" thành gì? Thay emoji bằng chữ thì được gì so với xóa emoji?

**Đầu ra:** `src/preprocess.py` cùng bảng 5 ví dụ trước/sau (dùng cho Chương 4, mục Preprocessing được 15 điểm).

#### 24/10 (T7): Làm sạch và chia tập
**Học gì:** **rò rỉ dữ liệu** (data leakage); vì sao khử trùng lặp **trước** khi chia; vì sao chia **theo sản phẩm** (`GroupShuffleSplit`).

**Làm gì:** notebook `02_clean_split.ipynb`. Đoạn code dưới đây mình đã chạy thử trên file của bạn, ra đúng 2.548 dòng.

```python
import re, unicodedata, pandas as pd
from sklearn.model_selection import GroupShuffleSplit

df = pd.read_csv("data/final_train_dataset.csv").rename(
    columns={"prod": "product", "com": "text", "rat": "rating"})
df["text"] = df["text"].astype(str).map(lambda s: unicodedata.normalize("NFC", s))

# 1) bỏ rác giao diện "Tổng quan\n4.9\n(3034 đánh giá)..."
df = df[~df["text"].str.match(r"^\s*Tổng quan\s*\n\s*\d")]
# 2) bỏ nhãn mục template "Chất lượng sản phẩm:", "Đúng với mô tả:", ... ở đầu dòng
LABEL_RE = re.compile(r"(?m)^\s*[^:\n]{3,25}:\s*")
df["text_clean"] = (df["text"].str.replace(LABEL_RE, "", regex=True)
                    .str.replace(r"\s+", " ", regex=True).str.strip())
# 3) khử trùng lặp TRƯỚC khi chia, bỏ câu < 2 từ
df = df.drop_duplicates(subset=["text_clean"])
df = df[df["text_clean"].str.split().str.len() >= 2]
# 4) nhãn yếu từ số sao
df["weak_label"] = df["rating"].map({1: "neg", 2: "neg", 3: "neu", 4: "pos", 5: "pos"})

# 5) chia theo sản phẩm: 70% sản phẩm để train, 30% làm kho tập vàng
gss = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=42)
tr_idx, gold_idx = next(gss.split(df, groups=df["product"]))
df.iloc[tr_idx].to_csv("data/processed/shopee_train.csv", index=False)
df.iloc[gold_idx].to_csv("data/processed/shopee_gold_pool.csv", index=False)
```

JSONL (không dấu): giữ những câu có sao và nhãn khớp nhau, bỏ câu 3 sao:

```python
j = pd.read_json("data/aug_unaccented_reviews.jsonl", lines=True)
keep = ((j.rating <= 2) & (j.label == "negative")) | ((j.rating >= 4) & (j.label == "positive"))
aug = j[keep].assign(weak_label=j.label.map({"negative": "neg", "positive": "pos"}))
aug.to_csv("data/processed/aug_train.csv", index=False)   # 1.206 câu, chỉ có pos/neg
```

ViSD4SA: chuyển nhãn cụm từ thành nhãn cả câu. Ghi rõ quy tắc này trong báo cáo:
- Mọi cụm cùng một cảm xúc thì nhận cảm xúc đó.
- Nếu lẫn lộn: có khía cạnh `GENERAL` thì lấy cảm xúc của `GENERAL`, không thì lấy cảm xúc chiếm đa số.
- Hòa thì **bỏ câu**. Không gán `neu`, vì "khen pin, chê camera" không phải là trung lập.

```python
import json, collections, unicodedata
import pandas as pd

MAP4 = {"PRICE": "gia_ca", "SER&ACC": "dich_vu"}          # 8 khía cạnh còn lại -> chat_luong
POL = {"POSITIVE": "pos", "NEGATIVE": "neg", "NEUTRAL": "neu"}

def sentence_label(spans):
    pols = [t.split("#")[1] for _, _, t in spans]
    if not pols:
        return None
    if len(set(pols)) == 1:
        return POL[pols[0]]
    gen = [t.split("#")[1] for _, _, t in spans if t.startswith("GENERAL#")]
    if gen:
        return POL[collections.Counter(gen).most_common(1)[0][0]]
    (p1, c1), (p2, c2) = collections.Counter(pols).most_common(2)
    return None if c1 == c2 else POL[p1]

def load_visd(split):
    rows = []
    for line in open(f"ViSD4SA/{split}.jsonl", encoding="utf-8"):
        r = json.loads(line)
        text = r["text"]
        aspects = {}
        for st, en, tag in r["labels"]:
            en = min(en, len(text))                        # sửa 122 cụm có end vượt độ dài câu
            asp, pol = tag.split("#")
            aspects.setdefault(MAP4.get(asp, "chat_luong"), []).append(POL[pol])
        rows.append({"text": unicodedata.normalize("NFC", text),   # NFC SAU khi đã dùng offset
                     "label": sentence_label(r["labels"]),
                     **{a: collections.Counter(v).most_common(1)[0][0] for a, v in aspects.items()}})
    return pd.DataFrame(rows).dropna(subset=["label"])

visd = {sp: load_visd(sp) for sp in ["train", "dev", "test"]}
```

Bảng kết quả có thêm các cột `chat_luong`, `gia_ca`, `dich_vu`, mỗi cột nhận pos/neg/neu hoặc trống. Đây là **dữ liệu ABSA có nhãn để huấn luyện** cho 3 trong 4 khía cạnh. Khía cạnh giao hàng thì không có nhãn trong ViSD4SA.

Ánh xạ 10 khía cạnh của ViSD4SA về 4 nhóm:

| ViSD4SA | Nhóm của đề |
|---|---|
| SCREEN, CAMERA, FEATURES, BATTERY, PERFORMANCE, STORAGE, DESIGN, GENERAL | Chất lượng |
| PRICE | Giá cả |
| SER&ACC | Dịch vụ |
| *(không có)* | Giao hàng: lấy từ từ điển khía cạnh, xem ngày 1/11 |

Cuối cùng, kiểm tra trùng chéo: chuẩn hóa (bỏ dấu, viết thường) rồi xem câu nào trong tập vàng xuất hiện trong ViSD4SA, `shopee_train` hoặc `aug`. Nếu có thì xóa khỏi tập train.

**Tự kiểm tra:** Nếu chia ngẫu nhiên từng dòng thay vì theo sản phẩm, F1 sẽ cao lên hay thấp xuống, vì sao? (Gợi ý: mô hình học thuộc tên và đặc điểm sản phẩm.) Vì sao JSONL chỉ được dùng để huấn luyện?

**Đầu ra:** các file trong `data/processed/` và bảng "số dòng sau từng bước làm sạch" (đưa vào Chương 3).

#### 25/10 (CN): Hướng dẫn gán nhãn và 150 mẫu đầu
**Học gì:** vì sao cần **hướng dẫn gán nhãn** (annotation guideline) viết trước khi gán; độ đồng thuận giữa người gán (Cohen's kappa).

**Làm gì:**
1. Từ `shopee_gold_pool.csv` (~700 câu), lấy 500 câu **phân tầng theo sao** (`df.groupby("rating").sample(...)`) và lấy dư lớp 1–3 sao để lớp neg/neu đủ mẫu.
2. Viết `labeling/guideline.md` (1–2 trang):
   - Định nghĩa pos/neg/neu.
   - Câu khen một ý chê một ý thì xử lý thế nào (ví dụ: theo ý chính hoặc theo kết luận cuối câu).
   - Câu mỉa mai.
   - Câu chỉ mô tả mà không đánh giá (gán neu).
   - Mỗi trường hợp kèm 2–3 ví dụ lấy từ chính dữ liệu.
3. Gán nhãn trong Excel/Google Sheets với các cột `id, text, sentiment, giao_hang, chat_luong, gia_ca, dich_vu, ghi_chu`. **Che cột sao đi** khi gán để khỏi bị ảnh hưởng. Mỗi khía cạnh nhận một trong các giá trị `pos/neg/neu/none`. 200 câu đầu gán cả khía cạnh, các câu còn lại chỉ gán cảm xúc.
4. Gán 150 câu. **Bắt đầu viết Chương 3.**

**Tự kiểm tra:** Đọc lại 20 câu khó nhất. Guideline đã đủ rõ để người khác gán ra cùng nhãn chưa?

#### 26/10 (T2) và 27/10 (T3): Hoàn tất tập vàng
- Gán tiếp tới **500 câu cảm xúc** và **200 câu khía cạnh**, chia buổi 150 câu mỗi lần để đỡ mỏi.
- **Độ đồng thuận:**
  - Nếu làm nhóm: hai người cùng gán 100 câu rồi tính `sklearn.metrics.cohen_kappa_score`.
  - Nếu làm một mình: gán lại 60 câu đã gán từ hôm 25/10 mà không xem nhãn cũ, rồi tính kappa giữa hai lần gán (intra-annotator agreement).
- **Phân tích thú vị cho báo cáo:** lập bảng chéo giữa nhãn tay và số sao. Bao nhiêu % câu 4 sao thật ra là neg hoặc neu? Con số này chứng minh vì sao cần tập vàng.

**Đầu ra:** `labeling/gold_500.csv`, `guideline.md`, giá trị kappa.

---

### Chặng 2: Mô hình (28/10 – 31/10)

**Quy tắc chung:**
- Mọi mô hình đều báo cáo **hai con số**: F1-macro **trong miền** (test của chính nguồn huấn luyện) và F1-macro **trên tập vàng Shopee** (gold_500).
- Các cấu hình huấn luyện: **A** (ViSD4SA), **B** (shopee_train), **A+B**, **A+B+Aug**.
- Aug và các câu của A không có lớp neu nên làm lệch lớp neu. Đây là chỗ cần nhận xét trong báo cáo.

#### 28/10 (T4): BoW, TF-IDF với Naive Bayes và Logistic Regression. Mốc 1
**Học gì:**
- BoW đếm tần suất từ, TF-IDF giảm trọng số các từ xuất hiện ở mọi câu.
- n-gram: bigram "không tốt" mang nghĩa ngược với "tốt".
- Naive Bayes giả định các từ độc lập; Logistic Regression học trọng số cho từng từ.
- `class_weight="balanced"` giúp mô hình không bỏ qua lớp ít mẫu.

```python
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import f1_score, classification_report

vecs = {"BoW": CountVectorizer(ngram_range=(1, 2), min_df=2),
        "TF-IDF": TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)}
clfs = {"NB": MultinomialNB(),
        "LR": LogisticRegression(max_iter=2000, class_weight="balanced")}
rows = []
for cfg, (Xtr, ytr) in train_sets.items():        # {"A": (...), "B": (...), "A+B": (...), ...}
    for vn, v in vecs.items():
        for cn, c in clfs.items():
            m = make_pipeline(v, c).fit(Xtr, ytr)
            rows.append({"train": cfg, "model": f"{vn}+{cn}",
                         "F1_gold": f1_score(gold.sentiment, m.predict(gold.text_prep), average="macro")})
pd.DataFrame(rows).pivot(index="model", columns="train", values="F1_gold")
```

Mốc so sánh (đã chạy thử, nhãn sao, chưa tách từ): TF-IDF+LR đạt ~0,67. Sau tiền xử lý và trên nhãn tay, kết quả có thể khác. Ghi lại cả hai.

**Tự kiểm tra:** In 20 từ có trọng số dương và âm lớn nhất của LR (`coef_`). Có từ nào là tên sản phẩm không? Nếu có thì đó là dấu hiệu mô hình học "lối tắt".

**Đầu ra:** bảng baseline. **Bắt đầu viết Chương 4.**

#### 29/10 (T5): Word2Vec và thí nghiệm có/không tiền xử lý
**Học gì:**
- Word2Vec biểu diễn mỗi từ bằng vector dày; từ gần nghĩa thì gần nhau.
- Một câu = trung bình các vector từ (mean pooling). Nhược điểm của cách này: mất trật tự từ.

```python
from gensim.models import Word2Vec
corpus = [s.split() for s in all_train_texts_prep]          # A + B + Aug, đã tách từ
w2v = Word2Vec(corpus, vector_size=200, window=5, min_count=2, sg=1, epochs=20, seed=42)
print(w2v.wv.most_similar("tệ"))                             # kiểm tra vector có hợp lý không
def sent_vec(s):
    vs = [w2v.wv[t] for t in s.split() if t in w2v.wv]
    return np.mean(vs, axis=0) if vs else np.zeros(200)
```

Rồi chạy Logistic Regression trên các vector câu.

**Thí nghiệm tiền xử lý** (cần cho mục 15 điểm): với TF-IDF+LR, so sánh bốn biến thể trên tập vàng:
1. Văn bản thô.
2. Chỉ chuẩn hóa (NFC, viết thường, teencode, emoji).
3. Chuẩn hóa + tách từ.
4. Biến thể 3 + bỏ stopword nhưng giữ từ phủ định.

**Thí nghiệm không dấu:** bỏ dấu tập vàng (dùng `unicodedata` như đoạn kiểm tra trùng), đánh giá mô hình train trên A+B và trên A+B+Aug. Aug có giúp mô hình chịu được câu không dấu không?

**Đầu ra:** bảng Word2Vec, bảng ảnh hưởng tiền xử lý, bảng thí nghiệm không dấu.

#### 30/10 (T6): Fine-tune PhoBERT (Colab/Kaggle)
**Học gì:**
- Transformer và fine-tune là gì: lấy mô hình đã học tiếng Việt sẵn, huấn luyện thêm một lớp phân loại lên trên.
- PhoBERT **yêu cầu văn bản đã tách từ** (dùng VnCoreNLP hoặc underthesea, ra dạng "hài_lòng").
- `max_len`, learning rate, số epoch có ý nghĩa gì; dùng tập dev để chọn checkpoint.

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
tok = AutoTokenizer.from_pretrained("vinai/phobert-base")
model = AutoModelForSequenceClassification.from_pretrained("vinai/phobert-base", num_labels=3)
args = TrainingArguments("out", learning_rate=2e-5, num_train_epochs=4,
                         per_device_train_batch_size=32, eval_strategy="epoch",
                         save_strategy="epoch", load_best_model_at_end=True,
                         metric_for_best_model="f1_macro", seed=42, fp16=True)
# tokenize với max_length=128, truncation=True; compute_metrics trả f1_macro
```

Nếu ít thời gian, chạy trước cấu hình **A+B**, rồi mới tới A và B.

**Tự kiểm tra:** Vì sao PhoBERT thường hơn TF-IDF ở các câu phủ định và câu dài? Kiểm chứng bằng ví dụ ở ngày 31/10.

#### 31/10 (T7): Tinh chỉnh, mốc so sánh, đánh giá ngoài miền. Mốc 2
1. Thử class weight hoặc oversampling cho lớp neu; thử thêm 1–2 giá trị learning rate.
2. So với mô hình fine-tune sẵn `wonrax/phobert-base-vietnamese-sentiment`, chạy thẳng trên tập vàng. Lưu ý mô hình này cũng được huấn luyện trên review TMĐT nên chỉ dùng để tham khảo.
3. **Bảng kết quả chính**: các hàng là mô hình, các cột là F1 trong miền và F1 trên tập vàng cho từng cấu hình train.
4. Vẽ confusion matrix của mô hình tốt nhất trên tập vàng.
5. **Phân tích lỗi:** lấy 20–30 câu đoán sai, xếp vào các nhóm: phủ định, mỉa mai, nhiều khía cạnh trái chiều, teencode/không dấu, câu chỉ mô tả.
6. **Bootstrap khoảng tin cậy cho F1** (tập vàng chỉ có 500 câu): lấy mẫu lại 1.000 lần rồi báo khoảng 2,5%–97,5%.

**Nếu tới tối 31/10 vẫn chưa có PhoBERT tự fine-tune:** dùng mô hình của wonrax làm đại diện PhoBERT và ghi vào phần hạn chế.

---

### Chặng 3: ABSA, phân tích kinh doanh, dashboard (1/11 – 4/11)

#### 1/11 (CN): ABSA 4 khía cạnh
**Học gì:** ABSA gồm hai bước: (1) câu nói về khía cạnh nào, (2) cảm xúc với khía cạnh đó là gì.

**Cách 1: Từ điển + mô hình cảm xúc** (`src/aspects.py`):

```python
ASPECTS = {
    "giao_hang": ["giao hàng", "giao", "ship", "shipper", "vận chuyển", "đóng gói", "gói hàng", "nhận hàng", "hộp", "móp"],
    "chat_luong": ["chất lượng", "chất liệu", "vải", "đường may", "bền", "hỏng", "hư", "lỗi", "mùi", "pin", "đúng mô tả", "size"],
    "gia_ca": ["giá", "rẻ", "đắt", "mắc", "tiền", "đáng tiền", "sale", "voucher"],
    "dich_vu": ["shop", "cửa hàng", "tư vấn", "nhắn tin", "trả lời", "đổi trả", "bảo hành", "thái độ", "hỗ trợ"],
}
```

So khớp từ khóa trên văn bản **đã chuẩn hóa nhưng chưa tách từ** (`preprocess(s, segment=False)`), vì sau khi tách từ "giao hàng" sẽ thành "giao_hàng". Tách câu thành các mệnh đề (theo dấu chấm, dấu phẩy, "nhưng", "mà"). Mệnh đề nào chứa từ khóa của khía cạnh thì chạy mô hình cảm xúc tốt nhất trên mệnh đề đó. Mở rộng từ điển bằng `w2v.wv.most_similar("giao_hàng")`.

**Cách 2 (tùy chọn): Few-shot prompting** với một LLM. Đưa vào prompt 5–8 ví dụ đã gán nhãn, yêu cầu trả về JSON gồm 4 khía cạnh. Ghi rõ mô hình đã dùng, prompt và chi phí.

**Cách 3 (khuyến nghị nếu kịp, vì ViSD4SA có nhãn khía cạnh):**
- Với mỗi khía cạnh `chat_luong`, `gia_ca`, `dich_vu`, huấn luyện một bộ phân loại 4 lớp (pos/neg/neu/none) trên các cột vừa tạo từ ViSD4SA. Có thể dùng TF-IDF+LR trước, rồi PhoBERT.
- Khía cạnh `giao_hang` vẫn dùng từ điển.
- Đánh giá trên cả ViSD4SA test (trong miền) và 200 câu Shopee gán tay (ngoài miền).

**Đánh giá** trên 200 câu đã gán khía cạnh: F1 phát hiện khía cạnh (có/không) cho từng khía cạnh, và accuracy cảm xúc trên những khía cạnh phát hiện đúng.

#### 2/11 (T2): Chạy mô hình trên toàn bộ dữ liệu Shopee
- Chạy mô hình cảm xúc và ABSA tốt nhất trên cả 2.548 review.
- Thống kê:
  - Tỉ lệ pos/neu/neg theo ngành hàng và theo sản phẩm.
  - Tỉ lệ tiêu cực theo từng khía cạnh.
  - Khía cạnh nào bị nhắc nhiều nhất trong các review 1–2 sao.
- Lưu `data/processed/shopee_predicted.csv`.

#### 3/11 (T3): Word cloud và dashboard
- Vẽ word cloud riêng cho pos và cho neg, dùng văn bản đã tách từ và bỏ stopword. Nên làm thêm word cloud theo cặp khía cạnh × neg (ví dụ "giao hàng – tiêu cực").
- Dashboard Streamlit (`app/dashboard.py`):
  - Bộ lọc theo ngành hàng hoặc sản phẩm.
  - Biểu đồ tỉ lệ cảm xúc.
  - Biểu đồ cột chồng theo khía cạnh.
  - Bảng câu trích tiêu cực.
  - Ô nhập câu để dự đoán trực tiếp.
- Chạy bằng `streamlit run app/dashboard.py` rồi chụp màn hình cho báo cáo.

#### 4/11 (T4): Top 3 vấn đề cần cải thiện. Mốc 3
Mỗi vấn đề cần có ba thứ:
- **Số liệu**, ví dụ "38% review tiêu cực của nhóm thời trang nhắc tới size/chất liệu".
- **2–3 câu trích thật**, đã ẩn danh.
- **Một đề xuất hành động cụ thể**, ví dụ "thêm bảng size theo chiều cao/cân nặng vào trang sản phẩm".

Nếu còn thời gian, làm thêm điểm nhấn: TextCNN bằng PyTorch, hoặc ABSA bằng PhoBERT.

---

### Chặng 4: Báo cáo (5/11 – 11/11), giữ nguyên lịch cũ

| Ngày | Việc |
|---|---|
| 5/11 | Viết hoàn chỉnh Chương 5 (kết quả) và Chương 6 (kinh doanh) |
| 6/11 | Chương 1, 2, 7 và Tóm tắt |
| 7/11 | Ghép báo cáo, đánh số hình/bảng, tài liệu tham khảo, kiểm tra ≤ 30 trang |
| 8/11 | Đọc lại; **chạy lại toàn bộ notebook từ đầu** để chắc chắn tái lập được |
| 9/11 | Slide; đóng gói bài nộp (báo cáo, notebook, dashboard, slide) |
| 10/11 | Dự phòng |
| 11/11 | Nộp sớm trong ngày |

**Chỉnh nội dung báo cáo cho khớp dữ liệu mới:**
- **Chương 3:**
  - Đổi "Tiki" thành "Shopee".
  - Mô tả 3 nguồn theo bảng ở mục 0 và bảng số dòng sau từng bước làm sạch (2.843 → 2.548).
  - Nêu lý do chia theo sản phẩm.
  - Nêu rằng JSONL là dữ liệu tăng cường không dấu, chỉ dùng để huấn luyện.
  - Đưa bảng chéo nhãn tay với số sao.
- **Chương 5:** tách rõ ba loại đánh giá:
  - (a) Trong miền.
  - (b) Ngoài miền thật: train A, test trên tập vàng Shopee.
  - (c) Khác sản phẩm, cùng nền tảng: train B, test trên tập vàng.
- **Chương 7, hạn chế:**
  - Tập vàng nhỏ (500 câu) và chỉ có một người gán, nếu bạn làm một mình.
  - Nhãn sao là nhãn yếu.
  - Dữ liệu Shopee chỉ gồm 32 sản phẩm.
  - Dữ liệu Aug có thể do AI sinh.

---

## 3. Nếu chậm tiến độ, cắt theo thứ tự

1. Điểm nhấn (TextCNN, ABSA bằng PhoBERT).
2. Few-shot prompting ABSA, chỉ giữ cách từ điển.
3. Thí nghiệm không dấu.
4. Word2Vec (vẫn còn BoW, TF-IDF, PhoBERT là đủ 3 phương pháp).

**Không cắt:** tập vàng 500 câu, đánh giá trên tập vàng, phân tích lỗi, chia theo sản phẩm.

## 4. Phương án cào bổ sung (chỉ khi giảng viên yêu cầu tự cào)

Dành 1–2 ngày, đặt vào 23–24/10 và dời phần tiền xử lý sang các buổi tối:
- Cào 1.000–2.000 review Tiki của 2 ngành hàng **khác** với 32 sản phẩm hiện có, tối đa 200 review mỗi sản phẩm.
- Dùng `requests`, nghỉ 1–2 giây giữa các request, tôn trọng robots.txt, ẩn danh tên người dùng.
- Dữ liệu này bổ sung cho phân tích kinh doanh và làm tập đánh giá ngoài miền thứ hai. Bạn có thể lấy 100–200 câu để gán nhãn nhanh.

## 5. Lỗi thường gặp (bản cho dataset này)

- Quên bỏ dòng rác "Tổng quan… Trợ lý AI tổng hợp": đó là văn bản do AI của sàn viết, không phải review của người mua.
- Chia ngẫu nhiên từng dòng, khiến cùng một sản phẩm khăn ướt có mặt cả trong train lẫn test.
- Đưa câu JSONL vào tập test, hoặc gộp JSONL 2 lớp với dữ liệu 3 lớp mà không nói rõ.
- Dùng số sao làm nhãn test, rồi lại báo đó là "độ chính xác".
- Xóa từ "không" khi bỏ stopword.
- Quên tách từ trước khi đưa văn bản vào PhoBERT.
- Chỉ báo accuracy. Lớp neu chỉ chiếm ~10%, nên accuracy che mất lỗi.
