import re, unicodedata
import emoji
from underthesea import word_tokenize

TEENCODE = {"k": "không", "ko": "không", "kh": "không", "hok": "không", "khum": "không",
            "kg": "không", "hong": "không", "hông": "không", "khong": "không",
            "dc": "được", "đc": "được", "dk": "được", "đk": "được", "duoc": "được",
            "sp": "sản phẩm", "mik": "mình", "mk": "mình", "mn": "mọi người", "mng": "mọi người",
            "ok": "ổn", "oke": "ổn", "oki": "ổn", "okela": "ổn", "okie": "ổn", "s": "sao",
            "vs": "với", "nx": "nữa", "ship": "giao hàng", "shop": "cửa hàng",
            "nma": "nhưng mà", "qa": "quá", "qá": "quá", "wa": "quá", "lun": "luôn",
            "j": "gì", "z": "vậy", "v": "vậy", "r": "rồi", "ròi": "rồi", "rùi": "rồi",
            "bth": "bình thường",   # không map "bt": vừa là "bình thường" vừa là "biết" "bthg": "bình thường",
            "cx": "cũng", "cg": "cũng", "ns": "nói", "nt": "nhắn tin", "ib": "nhắn tin",
            "trc": "trước", "đt": "điện thoại", "dt": "điện thoại", "tl": "trả lời",
            "fb": "phản hồi", "feedback": "phản hồi", "rep": "trả lời", "auth": "chính hãng",
            "hsd": "hạn sử dụng", "sz": "size", "ae": "anh em", "nhìu": "nhiều",
            "đag": "đang", "dag": "đang", "ntn": "như thế nào", "thik": "thích", "iu": "yêu",
            "ng": "người", "nhg": "nhưng", "hàg": "hàng", "hag": "hàng",
            "tks": "cảm ơn", "thanks": "cảm ơn", "thank": "cảm ơn", "cám": "cảm",
            "good": "tốt", "nice": "tốt", "bad": "tệ", "fake": "giả"}
# tự bổ sung thêm khi đọc dữ liệu, mục tiêu 50–100 mục

# Bộ teencode mạng xã hội bổ sung (28/10). Đã bỏ: khóa nhiều từ (tra theo từng token nên không khớp),
# mục phiên âm/sai nghĩa (keke, plz, lol...), mục dễ nhầm trong review (a, c, e, vc, vv...)
# và từ không dấu (nguoi, biet...) để không làm hỏng thí nghiệm không dấu.
TEENCODE_MXH = {
    "ctrai": "con trai", "khôg": "không", "bme": "bố mẹ", "cta": "chúng ta", "mih": "mình",
    "mqh": "mối quan hệ", "cgai": "con gái", "nhữg": "những", "svtn": "sinh viên tình nguyện",
    "qtam": "quan tâm", "thươg": "thương", "qtâm": "quan tâm", "chug": "chung", "trườg": "trường",
    "thoy": "thôi", "đki": "đăng ký", "atsm": "ảo tưởng sức mạnh", "ạk": "ạ", "cv": "công việc",
    "cùg": "cùng", "pn": "bạn", "pjt": "biết", "thjk": "thích", "ktra": "kiểm tra", "nek": "nè",
    "cgái": "con gái", "nthe": "như thế", "chúg": "chúng", "kái": "cái", "tìh": "tình",
    "phòg": "phòng", "lòg": "lòng", "từg": "từng", "rằg": "rằng", "sốg": "sống", "thuj": "thôi",
    "thuơng": "thương", "càg": "càng", "đky": "đăng ký", "bằg": "bằng", "sviên": "sinh viên",
    "ák": "á", "đág": "đáng", "nvay": "như vậy", "nhjeu": "nhiều", "xg": "xuống", "zồi": "rồi",
    "trag": "trang", "zữ": "dữ", "atrai": "anh trai", "kte": "kinh tế", "độg": "động",
    "lmht": "liên minh huyền thoại", "gắg": "gắng", "đzai": "đẹp trai", "thgian": "thời gian",
    "đồg": "đồng", "btrai": "bạn trai", "nthê": "như thế", "hìhì": "hì hì", "vọg": "vọng",
    "hihe": "hi he", "đôg": "đông", "răg": "răng", "thườg": "thường", "tcảm": "tình cảm",
    "đứg": "đứng", "ksao": "không sao", "dz": "đẹp trai", "hjxhjx": "hix hix", "cmày": "chúng mày",
    "xuốg": "xuống", "nkư": "như", "lquan": "liên quan", "tiếg": "tiếng", "xih": "xinh",
    "hìh": "hình", "thàh": "thành", "ngke": "nghe", "dzậy": "dậy", "tnào": "thế nào",
    "tưởg": "tưởng", "ctrinh": "chương trình", "phog": "phong", "hôg": "không", "zìa": "gì",
    "kũg": "cũng", "ntnao": "như thế nào", "trọg": "trọng", "nthế": "như thế", "năg": "năng",
    "ngđó": "người đó", "lquen": "làm quen", "riêg": "riêng", "ngag": "ngang", "hêhê": "hê hê",
    "bnhiu": "bao nhiêu", "ngốk": "ngốc", "kậu": "cậu", "kqua": "kết quả", "htrc": "hôm trước",
    "địh": "định", "gđình": "gia đình", "giốg": "giống", "csống": "cuộc sống", "zùi": "rồi",
    "bnhiêu": "bao nhiêu", "cbị": "chuẩn bị", "kòn": "còn", "buôg": "buông", "csong": "cuộc sống",
    "chàg": "chàng", "chăg": "chăng", "ngàh": "ngành", "llac": "liên lạc", "nkưng": "nhưng",
    "nắg": "nắng", "tíh": "tính", "khoảg": "khoảng", "thík": "thích", "ngđo": "người đó",
    "ngkhác": "người khác", "thẳg": "thẳng", "kảm": "cảm", "dàh": "dành", "júp": "giúp",
    "lặg": "lặng", "vđê": "vấn đề", "bbè": "bạn bè", "bóg": "bóng", "dky": "đăng ký",
    "dòg": "dòng", "uốg": "uống", "tyêu": "tình yêu", "snvv": "sinh nhật vui vẻ",
    "đthoại": "điện thoại", "qhe": "quan hệ", "cviec": "công việc", "tượg": "tượng", "qà": "quà",
    "thjc": "thích", "nhưq": "nhưng", "cđời": "cuộc đời", "bthường": "bình thường", "zà": "già",
    "đáh": "đánh", "xloi": "xin lỗi", "zám": "dám", "qtrọng": "quan trọng", "bìh": "bình",
    "lzi": "làm gì", "qhệ": "quan hệ", "đhbkhn": "đại học bách khoa hà nội", "kủa": "của",
    "lz": "làm gì", "đhkhtn": "đại học khoa học tự nhiên", "đóg": "đóng", "cka": "cha",
    "lgi": "làm gì", "nvậy": "như vậy", "qả": "quả", "đkiện": "điều kiện", "nèk": "nè",
    "tlai": "tương lai", "bsĩ": "bác sĩ", "hkì": "học kỳ", "đcsvn": "đảng cộng sản việt nam",
    "vde": "vấn đề", "chta": "chúng ta", "òy": "rồi", "ltinh": "linh tinh", "ngyeu": "người yêu",
    "đthoai": "điện thoại", "snghĩ": "suy nghĩ", "nặg": "nặng", "họk": "học", "dừg": "dừng",
    "hphúc": "hạnh phúc", "hiha": "hi ha", "wtâm": "quan tâm", "thíck": "thích", "chuện": "chuyện",
    "lạh": "lạnh", "ntnày": "như thế này", "lúk": "lúc", "ngía": "nghía", "mớj": "mới",
    "hsơ": "hồ sơ", "ctraj": "con trai", "nyêu": "người yêu", "điiiiiii": "đi", "rồii": "rồi",
    "kih": "kinh", "kb": "kết bạn", "dthương": "dễ thương", "nhiềuuu": "nhiều",
    "ctrình": "chương trình", "mìnk": "mình", "mjh": "mình", "uhm": "ừm", "thỳ": "thì",
    "nyc": "người yêu cũ", "nàg": "nàng", "thôii": "thôi", "đjên": "điên", "bgái": "bạn gái",
    "vớii": "với", "xink": "xinh", "hđộng": "hành động", "đhọc": "đại học", "bn": "bạn",
    "cj": "chị", "nógn": "nóng", "bik": "biết", "cmt": "comment", "ck": "chồng", "chk": "chồng",
    "ngta": "người ta", "gđ": "gia đình", "oh": "ồ", "vk": "vợ", "ctác": "công tác",
    "sg": "sài gòn", "ah": "à", "ạh": "ạ", "rì": "gì", "ms": "mới", "vn": "việt nam",
    "nhaa": "nha", "cũg": "cũng", "ơiii": "ơi", "ace": "anh chị em", "àk": "à", "uh": "ừ",
    "ơiiii": "ơi", "hnay": "hôm nay", "ukm": "ừm", "tq": "trung quốc", "ctr": "chương trình",
    "đii": "đi", "nch": "nói chuyện", "hahah": "ha ha", "nta": "người ta", "ngèo": "nghèo",
    "kêh": "kênh", "ak": "à", "ny": "người yêu", "qc": "quảng cáo", "baoh": "bao giờ",
    "zui": "vui", "zẻ": "vẻ", "tym": "tim", "aye": "anh yêu em", "eya": "em yêu anh",
    "insta": "instagram", "acc": "account", "chs": "chẳng hiểu sao", "wá": "quá", "zậy": "vậy",
    "zô": "vô", "ytb": "youtube", "xl": "xin lỗi", "hjhj": "hi hi", "in4": "info", "zạ": "vậy",
    "oy": "rồi", "jo": "giờ", "bsvv": "buổi sáng vui vẻ", "troai": "trai", "hjx": "hix", "ik": "ý",
    "ji": "gì", "lm": "làm", "đz": "đẹp giai", "sr": "sorry", "hoy": "thôi", "vd": "ví dụ",
    "unf": "unfriend", "fen": "friend", "cty": "công ty", "kô": "không",
    "đtqg": "đội tuyển quốc gia", "hqua": "hôm qua", "xog": "xong", "uk": "ừ", "nhoé": "nhé",
    "quí": "quý", "stk": "số tài khoản", "đươc": "được", "nghành": "ngành",
    "nvqs": "nghĩa vụ quân sự", "ngừoi": "người", "trog": "trong", "tgian": "thời gian",
    "biêt": "biết", "fải": "phải", "nguời": "người", "tgdd": "thế giới di động", "khg": "không",
    "nhưg": "nhưng", "thpt": "trung học phổ thông", "thằg": "thằng", "đuợc": "được", "àh": "à",
    "ku": "cu", "thým": "thím", "onl": "online", "cmnd": "chứng minh nhân dân",
    "sđt": "số điện thoại", "klq": "không liên quan"}
TEENCODE = {**TEENCODE_MXH, **TEENCODE}   # trùng khóa thì giữ bản ở trên

# Từ phủ định: KHÔNG bao giờ được xóa khi bỏ stopword
NEGATIONS = {"không", "chẳng", "chả", "chưa", "đừng", "chớ", "không_hề", "chẳng_hề", "chưa_hề"}

STOPWORDS = {"thì", "là", "mà", "và", "của", "cho", "với", "các", "những", "này", "đó",
             "thế", "nhé", "nha", "nhá", "ạ", "à", "ơi", "ấy", "cái", "chiếc", "con",
             "được", "đã", "đang", "sẽ", "bị", "có", "một", "mình", "em", "anh", "chị",
             "bạn", "tôi", "nó", "ở", "trong", "khi", "lại", "rồi", "cũng", "nên", "vì"}
STOPWORDS -= NEGATIONS


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


def remove_stopwords(s: str) -> str:
    """Bỏ stopword trên văn bản đã tách từ, giữ nguyên từ phủ định."""
    return " ".join(t for t in s.split() if t not in STOPWORDS)


def strip_accents(s: str) -> str:
    """'Hàng đẹp' -> 'Hang dep'. Dùng cho thí nghiệm không dấu và kiểm tra trùng."""
    s = unicodedata.normalize("NFD", str(s)).replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in s if unicodedata.category(c) != "Mn")
