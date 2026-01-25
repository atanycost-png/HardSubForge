import sys
import os
import json
import functools
import platform
import re
import shutil
import subprocess
import threading
import urllib.request
from pathlib import Path
from typing import Optional, List, Dict

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QPushButton, QLineEdit,
                               QComboBox, QTextEdit, QFileDialog,
                               QProgressBar, QMessageBox, QCheckBox, QSpinBox,
                               QFrame, QDialog, QFormLayout, QDialogButtonBox,
                               QSystemTrayIcon, QMenu, QTabWidget, QScrollArea,
                               QRadioButton)
from PySide6.QtCore import Qt, QThread, Signal, QUrl, QTimer
from PySide6.QtGui import QFont, QColor, QPalette, QDesktopServices

# --- CONFIGURAÇÕES E UTILITÁRIOS ---

CONFIG_FILE = "config.json"
APP_VERSION = "2.4.1"

# Regex patterns pre-compiled for performance
TIME_PATTERN = re.compile(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})')
DURATION_PATTERN = re.compile(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})')
BITRATE_PATTERN = re.compile(r'(\d+)k')
BITRATE_STRICT_PATTERN = re.compile(r'^\d+k$')
SANITIZE_PATTERN = re.compile(r'[<>:"/\\|?*]')

LANGUAGE_NAMES = {
    "aar": "Afar", "abk": "Abkhazian", "ace": "Achinese", "ach": "Acoli", "ada": "Adangme",
    "ady": "Adyghe", "afa": "Afro-Asiatic", "afh": "Afrihili", "afr": "Africâner", "ain": "Ainu",
    "aka": "Akan", "akk": "Akkadian", "alb": "Albanês", "ale": "Aleut", "alg": "Algonquian",
    "alt": "Southern Altai", "amh": "Amárico", "ang": "Inglês Antigo", "anp": "Angika", "apa": "Apache",
    "ara": "Árabe", "arc": "Aramaico", "arg": "Aragonês", "arm": "Armênio", "arn": "Mapudungun",
    "arp": "Arapaho", "art": "Artificial", "arw": "Arawak", "asm": "Assamês", "ast": "Asturiano",
    "ath": "Athapascan", "aus": "Australian", "ava": "Avaric", "ave": "Avestan", "awa": "Awadhi",
    "aym": "Aymará", "aze": "Azerbaijano", "bad": "Banda", "bai": "Bamileke", "bak": "Bashkir",
    "bal": "Baluchi", "bam": "Bambara", "ban": "Balinese", "baq": "Basque", "bas": "Basa",
    "bat": "Baltic", "bej": "Beja", "bel": "Bielorrusso", "bem": "Bemba", "ben": "Bengali",
    "ber": "Berber", "bho": "Bhojpuri", "bih": "Bihari", "bik": "Bikol", "bin": "Bini",
    "bis": "Bislama", "bla": "Siksiká", "bnt": "Bantu", "bos": "Bósnio", "bra": "Braj",
    "bre": "Bretão", "btk": "Batak", "bua": "Buriat", "bug": "Buginese", "bul": "Búlgaro",
    "bur": "Birmanês", "byn": "Blin", "cad": "Caddo", "cai": "Central American Indian", "car": "Carib",
    "cat": "Catalão", "cau": "Caucasian", "ceb": "Cebuano", "cel": "Celtic", "ces": "Tcheco",
    "cha": "Chamorro", "chb": "Chibcha", "che": "Checheno", "chg": "Chagatai", "chi": "Chinês",
    "chk": "Chuukese", "chm": "Mari", "chn": "Chinook", "cho": "Choctaw", "chp": "Chipewyan",
    "chr": "Cherokee", "chu": "Church Slavic", "chv": "Chuvash", "chy": "Cheyenne", "cmc": "Chamic",
    "cnr": "Montenegrino", "cop": "Coptic", "cor": "Cornish", "cos": "Córsego", "cpe": "Creoles",
    "cpf": "French-based Creoles", "cpp": "Portuguese-based Creoles", "cre": "Cree", "crh": "Crimean Tatar",
    "crp": "Creoles", "csb": "Kashubian", "cus": "Cushitic", "cym": "Galês", "cze": "Tcheco",
    "dak": "Dakota", "dan": "Dinamarquês", "dar": "Dargwa", "day": "Dayak", "del": "Delaware",
    "den": "Slave", "deu": "Alemão", "dgr": "Dogrib", "din": "Dinka", "div": "Dhivehi",
    "doi": "Dogri", "dra": "Dravidian", "dsb": "Lower Sorbian", "dua": "Duala", "dum": "Middle Dutch",
    "dut": "Holandês", "dyu": "Dyula", "dzo": "Dzongkha", "efi": "Efik", "egy": "Egyptian",
    "eka": "Ekajuk", "elx": "Elamite", "eng": "Inglês", "enm": "Middle English", "epo": "Esperanto",
    "est": "Estoniano", "eus": "Basque", "ewe": "Ewe", "ewo": "Ewondo", "fan": "Fang",
    "fao": "Feroês", "fas": "Persa", "fat": "Fanti", "fij": "Fijiano", "fil": "Filipino",
    "fin": "Finlandês", "fiu": "Finno-Ugrian", "fon": "Fon", "fra": "Francês", "fre": "Francês",
    "frm": "Middle French", "fro": "Old French", "frr": "Northern Frisian", "frs": "Eastern Frisian",
    "fry": "Frisão Ocidental", "ful": "Fula", "fur": "Friulian", "gaa": "Ga", "gay": "Gayo",
    "gba": "Gbaya", "gem": "Germanic", "geo": "Georgiano", "ger": "Alemão", "gez": "Geez",
    "gil": "Gilbertês", "gla": "Gaélico Escocês", "gle": "Irlandês", "glg": "Galego", "glv": "Manx",
    "gmh": "Middle High German", "goh": "Old High German", "gon": "Gondi", "gor": "Gorontalo",
    "got": "Gothic", "grb": "Grebo", "grc": "Ancient Greek", "gre": "Grego Moderno", "grn": "Guarani",
    "gsw": "Swiss German", "guj": "Gujarati", "gwi": "Gwich'in", "hai": "Haida", "hat": "Haitiano",
    "hau": "Hausa", "haw": "Havaiano", "heb": "Hebraico", "her": "Herero", "hil": "Hiligaynon",
    "him": "Himachali", "hin": "Hindi", "hit": "Hittite", "hmn": "Hmong", "hmo": "Hiri Motu",
    "hrv": "Croata", "hsb": "Upper Sorbian", "hun": "Húngaro", "hup": "Hupa", "hye": "Armênio",
    "iba": "Iban", "ibo": "Igbo", "ice": "Islandês", "ido": "Ido", "iii": "Sichuan Yi",
    "ijo": "Ijo", "iku": "Inuktitut", "ile": "Interlingue", "ilo": "Iloko", "ina": "Interlingua",
    "inc": "Indic", "ind": "Indonésio", "ine": "Indo-European", "inh": "Ingush", "ipk": "Inupiaq",
    "ira": "Iranian", "iro": "Iroquoian", "isl": "Islandês", "ita": "Italiano", "jav": "Javanês",
    "jbo": "Lojban", "jpn": "Japonês", "jpr": "Judeo-Persian", "jrb": "Judeo-Arabic", "kaa": "Kara-Kalpak",
    "kab": "Kabyle", "kac": "Kachin", "kal": "Kalaallisut", "kam": "Kamba", "kan": "Kannada",
    "kar": "Karen", "kas": "Kashmiri", "kau": "Kanuri", "kaw": "Kawi", "kaz": "Cazaque",
    "kbd": "Kabardian", "kha": "Khasi", "khi": "Khoisan", "khm": "Khmer", "kho": "Khotanese",
    "kik": "Kikuyu", "kin": "Kinyarwanda", "kir": "Quirguiz", "kmb": "Kimbundu", "kok": "Konkani",
    "kom": "Komi", "kon": "Kongo", "kor": "Coreano", "kos": "Kosraean", "kpe": "Kpelle",
    "krc": "Karachay-Balkar", "krl": "Karelian", "kro": "Kru", "kru": "Kurukh", "kua": "Kuanyama",
    "kum": "Kumyk", "kur": "Curdo", "kut": "Kutenai", "lad": "Ladino", "lah": "Lahnda",
    "lam": "Lamba", "lao": "Laociano", "lat": "Latim", "lav": "Letão", "lez": "Lezghian",
    "lim": "Limburgan", "lin": "Lingala", "lit": "Lituano", "lol": "Mongo", "loz": "Lozi",
    "ltz": "Luxemburguês", "lua": "Luba-Lulua", "lub": "Luba-Katanga", "lug": "Ganda", "lui": "Luiseno",
    "lun": "Lunda", "luo": "Luo (Kenya and Tanzania)", "lus": "Mizo", "mac": "Macedônio",
    "mad": "Madurese", "mag": "Magahi", "mah": "Marshallese", "mai": "Maithili", "mak": "Makasar",
    "mal": "Malaio", "man": "Mandingo", "mao": "Maori", "map": "Austronesian", "mar": "Marathi",
    "mas": "Masai", "may": "Malaio", "mdf": "Moksha", "mdr": "Mandar", "men": "Mende",
    "mga": "Middle Irish", "mic": "Mi'kmaq", "min": "Minangkabau", "mis": "Miscellaneous languages", "mkh": "Mon-Khmer",
    "mlg": "Malagasy", "mlt": "Maltês", "mnc": "Manchu", "mni": "Manipuri", "mno": "Manobo",
    "moh": "Mohawk", "mon": "Mongol", "mos": "Mossi", "mul": "Multiple languages", "mun": "Munda",
    "mus": "Creek", "mwl": "Mirandese", "mwr": "Marwari", "myn": "Mayan", "myv": "Erzya",
    "nah": "Nahuatl", "nai": "North American Indian", "nap": "Neapolitan", "nau": "Nauru", "nav": "Navajo",
    "nbl": "Ndebele, South", "nde": "Ndebele, North", "ndo": "Ndonga", "nds": "Low German",
    "nep": "Nepali", "new": "Newari", "nia": "Nias", "nic": "Niger-Kordofanian", "niu": "Niuean",
    "nno": "Norwegian Nynorsk", "nob": "Norwegian Bokmål", "nog": "Nogai", "non": "Old Norse", "nor": "Norueguês",
    "nqo": "N'Ko", "nso": "Northern Sotho", "nub": "Nubian", "nya": "Chichewa", "nym": "Nyamwezi",
    "nyn": "Nyankole", "nyo": "Nyoro", "nzi": "Nzima", "oci": "Occitan (post 1500)", "oji": "Ojibwa",
    "ori": "Oriya", "orm": "Oromo", "osa": "Osage", "oss": "Ossetian", "ota": "Turkish, Ottoman",
    "oto": "Otomian", "paa": "Papuan", "pag": "Pangasinan", "pal": "Pahlavi", "pam": "Pampanga",
    "pan": "Panjabi", "pap": "Papiamento", "pau": "Palauan", "peo": "Old Persian", "per": "Persa",
    "phi": "Philippine", "phn": "Phoenician", "pli": "Pali", "pol": "Polonês", "pon": "Pohnpeian",
    "por": "Português", "pra": "Prakrit languages", "pro": "Old Provençal", "pus": "Pashto",
    "que": "Quechua", "raj": "Rajasthani", "rap": "Rapanui", "rar": "Rarotongan", "roa": "Romance",
    "roh": "Romansh", "rom": "Romani", "rum": "Romeno", "run": "Rundi", "rup": "Aromanian",
    "rus": "Russo", "sad": "Sandawe", "sag": "Sango", "sah": "Yakut", "sai": "South American Indian",
    "sal": "Salishan", "sam": "Samaritan Aramaic", "san": "Sânscrito", "sas": "Sasak", "sat": "Santali",
    "scn": "Sicilian", "sco": "Scots", "sel": "Selkup", "sem": "Semitic", "sga": "Old Irish",
    "sgn": "Sign Languages", "shn": "Shan", "sid": "Sidamo", "sin": "Sinhala", "sio": "Siouan",
    "sit": "Sino-Tibetan", "sla": "Slavic", "slk": "Eslovaco", "slv": "Esloveno", "smi": "Sami",
    "smj": "Lule Sami", "smn": "Inari Sami", "smo": "Samoan", "sms": "Skolt Sami", "sna": "Shona",
    "snd": "Sindhi", "snk": "Soninke", "sog": "Sogdian", "som": "Somali", "son": "Songhai",
    "sot": "Sotho, Southern", "spa": "Espanhol", "sqi": "Albanês", "srd": "Sardo", "srn": "Sranan Tongo",
    "srp": "Sérvio", "srr": "Serer", "ssa": "Nilo-Saharan", "ssw": "Swati", "suk": "Sukuma",
    "sun": "Sundanês", "sus": "Susu", "sux": "Sumerian", "swa": "Swahili", "swe": "Sueco",
    "syc": "Classical Syriac", "syr": "Syriac", "tah": "Tahitian", "tai": "Tai", "tam": "Tâmil",
    "tat": "Tatar", "tel": "Telugu", "tem": "Temne", "ter": "Tereno", "tet": "Tetum",
    "tgk": "Tajik", "tgl": "Tagalog", "tha": "Tailandês", "tib": "Tibetano", "tig": "Tigre",
    "tir": "Tigrinya", "tiv": "Tiv", "tkl": "Tokelau", "tlh": "Klingon", "tli": "Tlingit",
    "tmh": "Tamashek", "tog": "Tonga (Nyasa)", "ton": "Tongan", "tpi": "Tok Pisin", "tsi": "Tsimshian",
    "tsn": "Tswana", "tso": "Tsonga", "tuk": "Turcomano", "tum": "Tumbuka", "tup": "Tupi",
    "tur": "Turco", "tut": "Altaic", "tvl": "Tuvalu", "twi": "Twi", "tyv": "Tuvinian",
    "udm": "Udmurt", "uga": "Ugaritic", "uig": "Uighur", "ukr": "Ucraniano", "umb": "Umbundu",
    "und": "Undetermined", "urd": "Urdu", "uzb": "Uzbeque", "vai": "Vai", "ven": "Venda",
    "vie": "Vietnamita", "vol": "Volapük", "vot": "Votic", "wak": "Wakashan", "wal": "Wolaytta",
    "war": "Waray", "was": "Washo", "wel": "Galês", "wen": "Sorbian", "wln": "Walloon",
    "wol": "Wolof", "xal": "Kalmyk", "xho": "Xhosa", "yao": "Yao", "yap": "Yapese",
    "yid": "Yiddish", "yor": "Yoruba", "ypk": "Yupik", "zap": "Zapotec", "zbl": "Blissymbols",
    "zen": "Zenaga", "zha": "Zhuang", "zhi": "Zhi", "zho": "Chinês", "znd": "Zande",
    "zul": "Zulu", "zun": "Zuni", "zxx": "No linguistic content", "zza": "Zaza"
}

@functools.lru_cache(maxsize=128) # Memoize ISO language lookups to avoid repeated string operations
def get_language_name(code: str) -> str:
    """Retorna o nome amigável do idioma baseado no código ISO."""
    if not code:
        return "Desconhecido"
    return LANGUAGE_NAMES.get(code.lower(), code)

class ConfigManager:
    """Gerencia o salvamento e carregamento de configurações."""
    def __init__(self):
        self.config_path = Path(CONFIG_FILE)
        self.data = {
            "last_video_dir": "",
            "last_quality": "Alta (4200k)",
            "last_text": "",
            "ffmpeg_path": "",
            "use_hardware_accel": True,
            "text_position": "top",
            "text_size": 22,
            "preserve_metadata": True,
            "custom_bitrate": "",
            "custom_preset": "p6",
            "custom_presets": [],
            "copy_audio": False
        }
        self.load()

    def load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except Exception as e:
                print(f"Erro ao carregar config: {e}")

    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar config: {e}")

@functools.lru_cache(maxsize=1)
def get_font_path() -> Optional[str]:
    """Retorna o caminho para uma fonte compatível (Arial ou fallback). Caching para evitar I/O repetitivo."""
    system = platform.system()
    paths = []

    if system == "Windows":
        paths = [
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/segoeui.ttf"),
            Path("C:/Windows/Fonts/calibri.ttf")
        ]
    elif system == "Darwin":  # macOS
        paths = [
            Path("/Library/Fonts/Arial.ttf"),
            Path("/System/Library/Fonts/Helvetica.ttc"),
            Path("/System/Library/Fonts/Supplemental/Arial.ttf")
        ]
    elif system == "Linux":
        paths = [
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
            Path("/usr/share/fonts/TTF/DejaVuSans.ttf")
        ]

    for p in paths:
        if p.exists():
            return str(p).replace("\\", "/")
    return None

def escape_filter_text(text: str) -> str:
    """Escapa caracteres especiais para o filtro do FFmpeg."""
    text = text.replace("\\", "\\\\\\\\")
    text = text.replace(":", "\\:")
    text = text.replace("'", "\\'")
    text = text.replace("\n", " ")
    text = text.replace("%", "\\%")
    return text

def escape_path_for_filter(path: str) -> str:
    path = path.replace("\\", "/")
    path = path.replace(":", "\\:")
    path = path.replace("'", "\\'")
    return path

def parse_bitrate(bitrate_str: str) -> int:
    """Converte string de bitrate (ex: '5000k') para valor numérico em kbps."""
    if not bitrate_str:
        return 0
    match = BITRATE_PATTERN.match(bitrate_str)
    if match:
        return int(match.group(1))
    return 0

def format_bitrate(kbps: int) -> str:
    """Formata valor numérico em kbps para string (ex: 5000 -> '5000k')."""
    return f"{kbps}k"

def calculate_bitrate_values(bitrate_str: str, maxrate_str: str = "", bufsize_str: str = "") -> tuple:
    """
    Calcula valores de bitrate, maxrate e bufsize.
    Retorna tupla (bitrate, maxrate, bufsize) formatados como strings.
    """
    bitrate = parse_bitrate(bitrate_str) or 3000

    if not maxrate_str:
        maxrate = int(bitrate * 1.2)
    else:
        maxrate = parse_bitrate(maxrate_str) or bitrate

    if not bufsize_str:
        bufsize = int(bitrate * 2)
    else:
        bufsize = parse_bitrate(bufsize_str) or int(bitrate * 2)

    return format_bitrate(bitrate), format_bitrate(maxrate), format_bitrate(bufsize)

def get_ffmpeg_binary() -> Optional[str]:
    script_dir = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))

    if platform.system() == "Windows":
        local_bin = script_dir / "ffmpeg.exe"
    else:
        local_bin = script_dir / "ffmpeg"

    if local_bin.exists():
        return str(local_bin)

    system_bin = shutil.which("ffmpeg")
    if system_bin:
        return system_bin

    return None

def check_nvidia_gpu() -> bool:
    try:
        creationflags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            timeout=3,
            creationflags=creationflags
        )
        return result.returncode == 0
    except:
        return False

@functools.lru_cache(maxsize=1)
def get_ffprobe_binary(ffmpeg_bin_path: Optional[str]) -> Optional[str]:
    """Resolve o caminho do ffprobe baseando-se no binário do ffmpeg ou PATH."""
    if not ffmpeg_bin_path:
        return shutil.which("ffprobe")

    ffprobe_bin = ffmpeg_bin_path.replace("ffmpeg", "ffprobe")
    if Path(ffprobe_bin).exists():
        return ffprobe_bin

    return shutil.which("ffprobe")

# --- THREADS ---

class FFmpegWorker(QThread):
    progress_signal = Signal(int)
    log_signal = Signal(str)
    finished_signal = Signal(int, str)

    def __init__(self, cmd: List[str], output_path: str):
        super().__init__()
        self.cmd = cmd
        self.output_path = output_path
        self.process = None
        self._is_cancelled = False

    def run(self):
        try:
            total_duration = 0
            creation_flags = 0

            if platform.system() == "Windows":
                creation_flags = subprocess.CREATE_NO_WINDOW

            self.process = subprocess.Popen(
                self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', errors='replace', creationflags=creation_flags
            )

            last_percent = -1
            for line in self.process.stdout:
                if self._is_cancelled: break
                stripped = line.strip()
                if not stripped: continue

                # Optimization: Skip emitting progress updates to the log to save UI resources
                if "time=" not in stripped:
                    self.log_signal.emit(stripped)

                # Optimization: Use string membership checks before regex to reduce CPU overhead in the hot loop
                if total_duration == 0:
                    if "Duration:" in stripped:
                        d_match = DURATION_PATTERN.search(stripped)
                        if d_match:
                            h, m, s = map(float, d_match.groups())
                            total_duration = h * 3600 + m * 60 + s
                            continue # Skip time search for the same line

                else: # total_duration > 0
                    if "time=" in stripped:
                        t_match = TIME_PATTERN.search(stripped)
                        if t_match:
                            h, m, s = map(float, t_match.groups())
                            current_time = h * 3600 + m * 60 + s
                            percent = min(int((current_time / total_duration) * 100), 99)
                            # Optimization: Only emit signal when percentage changes to avoid flooding the UI thread
                            if percent != last_percent:
                                self.progress_signal.emit(percent)
                                last_percent = percent

            self.process.wait()
            if self._is_cancelled: self.finished_signal.emit(-2, "")
            else:
                self.progress_signal.emit(100)
                self.finished_signal.emit(self.process.returncode, self.output_path)
        except Exception as e:
            self.log_signal.emit(f"ERRO CRÍTICO: {str(e)}")
            self.finished_signal.emit(-1, "")

    def stop(self):
        self._is_cancelled = True
        if self.process:
            self.process.terminate()
            try: self.process.wait(timeout=5)
            except: self.process.kill()

class ProbeWorker(QThread):
    finished_signal = Signal(list)

    def __init__(self, ffmpeg_bin_path: str, video_path: str):
        super().__init__()
        self.ffprobe_bin = get_ffprobe_binary(ffmpeg_bin_path)
        self.video_path = video_path

    def run(self):
        audio_streams = []
        if not self.ffprobe_bin or not Path(self.video_path).exists():
            self.finished_signal.emit(audio_streams)
            return
        try:
            cmd = [self.ffprobe_bin, "-v", "quiet", "-print_format", "json", "-show_streams", self.video_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'audio':
                        index = stream.get('index')
                        codec = stream.get('codec_name', 'unk').upper()
                        tags = stream.get('tags', {})
                        lang_code = tags.get('language', tags.get('title', ''))
                        lang = get_language_name(lang_code)
                        audio_streams.append({'index': index, 'title': f"Track {index}: {lang} ({codec})"})
        except Exception as e:
            print(f"Erro no probe: {e}")
        self.finished_signal.emit(audio_streams)

# --- DIALOGO DE NOVO PRESET ---

class AddPresetDialog(QDialog):
    """Janela para adicionar um novo preset de qualidade."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Preset de Qualidade")
        self.setFixedSize(350, 250)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ex: YouTube 1080p")
        layout.addRow("Nome do Preset:", self.input_name)

        self.input_bitrate = QLineEdit()
        self.input_bitrate.setPlaceholderText("Ex: 5000k")
        layout.addRow("Bitrate (-b:v):", self.input_bitrate)

        self.input_maxrate = QLineEdit()
        self.input_maxrate.setPlaceholderText("Ex: 5200k")
        layout.addRow("Maxrate:", self.input_maxrate)

        self.input_bufsize = QLineEdit()
        self.input_bufsize.setPlaceholderText("Ex: 9000k")
        layout.addRow("Bufsize:", self.input_bufsize)

        self.combo_preset = QComboBox()
        self.combo_preset.addItems(["p1 (Mais Rápido)", "p4 (Equilibrado)", "p6 (Lento/Melhor)"])
        layout.addRow("Preset NVENC:", self.combo_preset)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def validate_and_accept(self):
        if not self.input_name.text() or not self.input_bitrate.text():
            QMessageBox.warning(self, "Atenção", "Preencha pelo menos o Nome e o Bitrate.")
            return

        # Valida formato do bitrate
        if not BITRATE_STRICT_PATTERN.match(self.input_bitrate.text()):
            QMessageBox.warning(self, "Atenção", "O Bitrate deve seguir o formato 'XXXXk' (ex: 5000k, 3000k, etc)")
            return

        # Valida formato do maxrate se fornecido
        if self.input_maxrate.text() and not BITRATE_STRICT_PATTERN.match(self.input_maxrate.text()):
            QMessageBox.warning(self, "Atenção", "O Maxrate deve seguir o formato 'XXXXk' (ex: 5200k)")
            return

        # Valida formato do bufsize se fornecido
        if self.input_bufsize.text() and not BITRATE_STRICT_PATTERN.match(self.input_bufsize.text()):
            QMessageBox.warning(self, "Atenção", "O Bufsize deve seguir o formato 'XXXXk' (ex: 9000k)")
            return

        # Extrai apenas o código do preset (p1, p4, etc)
        preset_code = self.combo_preset.currentText().split()[0]

        self.preset_data = {
            "name": self.input_name.text(),
            "bitrate": self.input_bitrate.text(),
            "maxrate": self.input_maxrate.text(),
            "bufsize": self.input_bufsize.text(),
            "preset": preset_code
        }
        self.accept()

    def get_preset_data(self):
        return getattr(self, 'preset_data', None)

# --- WIDGETS ---

class DropArea(QLabel):
    files_dropped = Signal(list)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setAlignment(Qt.AlignCenter)
        self.setText("Arraste arquivos de vídeo aqui\nou clique para selecionar\n(Suporta múltiplos arquivos)")
        self.setStyleSheet("""
            QLabel { background-color: #2B2B2B; border: 2px dashed #555; border-radius: 10px; color: #AAA; padding: 30px; min-height: 120px; }
            QLabel:hover { border-color: #4A90E2; color: #FFF; background-color: #333; }
        """)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            video_files = [u.toLocalFile().lower() for u in urls if u.toLocalFile().lower().endswith(('.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv'))]
            if video_files:
                event.accept()
                self.setStyleSheet(self.styleSheet().replace("#555", "#4A90E2"))
                return
        event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(self.styleSheet().replace("#4A90E2", "#555"))

    def dropEvent(self, event):
        self.setStyleSheet(self.styleSheet().replace("#4A90E2", "#555"))
        video_files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv')):
                video_files.append(file_path)
        if video_files:
            self.files_dropped.emit(video_files)

    def mousePressEvent(self, event):
        if self.parent_window and hasattr(self.parent_window, 'select_video'):
            self.parent_window.select_video()

class ModernButton(QPushButton):
    def __init__(self, text, color="#4A90E2", hover="#357ABD"):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{ background-color: {color}; color: white; border-radius: 8px; padding: 10px; font-weight: bold; font-size: 14px; border: none; }}
            QPushButton:hover {{ background-color: {hover}; }}
            QPushButton:disabled {{ background-color: #444; color: #888; }}
        """)
        self.setCursor(Qt.PointingHandCursor)

class BatchSubtitleDialog(QDialog):
    """Diálogo para selecionar legenda individual em modo de lote."""

    def __init__(self, parent=None, video_path="", detected_sub="", batch_index=0, batch_total=1):
        super().__init__(parent)
        self.video_path = video_path
        self.detected_sub = detected_sub
        self.batch_index = batch_index
        self.batch_total = batch_total
        self.selected_subtitle = ""
        self.action = "use_detected"
        self.skip_all_flag = False
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"Configurar Legenda - Vídeo {self.batch_index}/{self.batch_total}")
        self.setFixedSize(500, 320)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        video_label = QLabel(f"Vídeo: {Path(self.video_path).name}")
        video_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        video_label.setWordWrap(True)
        layout.addWidget(video_label)

        layout.addWidget(QLabel("-" * 50))

        self.radio_detected = QRadioButton("Usar legenda detectada")
        self.radio_no_sub = QRadioButton("Sem legenda")
        self.radio_custom = QRadioButton("Selecionar outra legenda...")
        self.radio_skip = QRadioButton("Pular este vídeo")

        if self.detected_sub and Path(self.detected_sub).exists():
            sub_name = Path(self.detected_sub).name
            self.lbl_detected = QLabel(f"  📄 {sub_name}")
            self.lbl_detected.setStyleSheet("color: #4CAF50; margin-left: 25px;")
            layout.addWidget(self.radio_detected)
            layout.addWidget(self.lbl_detected)
            self.radio_detected.setChecked(True)
        else:
            self.lbl_detected = QLabel("  📄 Nenhuma detectada")
            self.lbl_detected.setStyleSheet("color: #AAA; margin-left: 25px;")
            layout.addWidget(self.radio_detected)
            layout.addWidget(self.lbl_detected)

        layout.addWidget(self.radio_no_sub)
        layout.addWidget(self.radio_custom)
        layout.addWidget(self.radio_skip)

        self.btn_browse = QPushButton("📁 Selecionar...")
        self.btn_browse.setEnabled(False)
        self.btn_browse.clicked.connect(self.browse_subtitle)
        layout.addWidget(self.btn_browse)

        layout.addStretch()

        btn_layout = QHBoxLayout()

        btn_skip_all = QPushButton("Pular Todos")
        btn_skip_all.setStyleSheet("background-color: #FF9800; color: white; padding: 8px; border-radius: 5px;")
        btn_skip_all.clicked.connect(self.skip_all)

        btn_ok = QPushButton("Confirmar")
        btn_ok.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; border-radius: 5px;")
        btn_ok.clicked.connect(self.accept_selection)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("background-color: #F44336; color: white; padding: 8px; border-radius: 5px;")
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_skip_all)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

        self.radio_custom.toggled.connect(self.on_radio_toggled)

    def on_radio_toggled(self, checked):
        self.btn_browse.setEnabled(checked and self.radio_custom.isChecked())

    def browse_subtitle(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecione a Legenda",
            str(Path(self.video_path).parent),
            "Legendas (*.srt *.ass *.ssa);;Todos os arquivos (*.*)"
        )
        if path:
            self.selected_subtitle = path
            self.lbl_detected.setText(f"  📄 {Path(path).name}")
            self.lbl_detected.setStyleSheet("color: #4CAF50; margin-left: 25px;")

    def accept_selection(self):
        if self.radio_detected.isChecked():
            self.action = "use_detected"
            self.selected_subtitle = self.detected_sub
        elif self.radio_no_sub.isChecked():
            self.action = "no_subtitle"
            self.selected_subtitle = ""
        elif self.radio_custom.isChecked():
            if not self.selected_subtitle:
                QMessageBox.warning(self, "Aviso", "Selecione um arquivo de legenda.")
                return
            self.action = "select_custom"
        elif self.radio_skip.isChecked():
            self.action = "skip"

        if self.skip_all_flag:
            self.action = "skip_all"

        self.accept()

    def skip_all(self):
        self.skip_all_flag = True
        self.action = "skip_all"
        self.accept()

    def get_result(self):
        return self.action, self.selected_subtitle

class VideoConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"HardSub Converter Pro v{APP_VERSION}")
        self.resize(700, 880)
        self.apply_dark_theme()

        self.config = ConfigManager()
        self.video_path = ""
        self.subtitle_path = ""
        self.worker = None
        self.has_nvidia = check_nvidia_gpu()
        self.ffmpeg_bin = get_ffmpeg_binary()
        self.batch_queue = []
        self.batch_index = 0
        self.batch_mode = False

        # Setup system tray for notifications
        self.setup_system_tray()

        self.setup_ui()
        self.load_settings()
        if not self.ffmpeg_bin:
            self.show_ffmpeg_warning()

    def setup_system_tray(self):
        """Configura o ícone da bandeja do sistema para notificações."""
        self.tray_icon = QSystemTrayIcon(self)

        # Tenta carregar ícone do app ou usa ícone padrão
        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            from PySide6.QtGui import QIcon
            self.tray_icon.setIcon(QIcon(str(icon_path)))

        self.tray_icon.show()

    def apply_dark_theme(self):
        app = QApplication.instance()
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#1E1E1E"))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor("#252525"))
        palette.setColor(QPalette.AlternateBase, QColor("#1E1E1E"))
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor("#333333"))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Highlight, QColor("#4A90E2"))
        app.setPalette(palette)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # Header
        title = QLabel("HardSub Converter Pro")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #4A90E2;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Status
        status_layout = QHBoxLayout()
        self.lbl_ffmpeg_status = QLabel("FFmpeg: Verificando...")
        self.lbl_ffmpeg_status.setStyleSheet("color: gray; font-size: 11px;")
        status_layout.addWidget(self.lbl_ffmpeg_status)

        gpu_text = "GPU: NVIDIA Detectada" if self.has_nvidia else "GPU: Não detectada"
        self.lbl_gpu_status = QLabel(gpu_text)
        self.lbl_gpu_status.setStyleSheet(f"color: {'#4CAF50' if self.has_nvidia else '#FFA726'}; font-size: 11px;")
        status_layout.addWidget(self.lbl_gpu_status)

        self.lbl_encoder_status = QLabel("Encoder: --")
        self.lbl_encoder_status.setStyleSheet("color: #AAA; font-size: 11px;")
        status_layout.addWidget(self.lbl_encoder_status)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        self.update_ffmpeg_status_ui()

        # Drag & Drop
        self.drop_area = DropArea(self)
        self.drop_area.files_dropped.connect(self.handle_files_drop)
        layout.addWidget(self.drop_area)

        # Legenda
        subtitle_layout = QHBoxLayout()
        self.lbl_sub = QLabel("Legenda: Nenhuma detectada")
        self.lbl_sub.setStyleSheet("color: #AAA;")
        subtitle_layout.addWidget(self.lbl_sub)

        btn_sub = QPushButton("Alterar Legenda")
        btn_sub.setStyleSheet("background-color: transparent; border: 1px solid #555; color: #CCC; padding: 5px;")
        btn_sub.clicked.connect(self.select_subtitle)
        subtitle_layout.addWidget(btn_sub)

        btn_clear_sub = QPushButton("Remover")
        btn_clear_sub.setStyleSheet("background-color: transparent; border: 1px solid #555; color: #CCC; padding: 5px;")
        btn_clear_sub.clicked.connect(self.clear_subtitle)
        subtitle_layout.addWidget(btn_clear_sub)
        layout.addLayout(subtitle_layout)

        # Áudio
        audio_layout = QHBoxLayout()
        self.lbl_audio = QLabel("Áudio:")
        self.lbl_audio.setStyleSheet("color: #AAA;")
        audio_layout.addWidget(self.lbl_audio)
        self.combo_audio = QComboBox()
        self.combo_audio.setStyleSheet("background-color: #2B2B2B; color: white; padding: 5px;")
        self.combo_audio.addItem("Padrão (Todas as faixas)")
        self.combo_audio.setEnabled(False)
        audio_layout.addWidget(self.combo_audio)
        layout.addLayout(audio_layout)

        # Texto
        layout.addWidget(QLabel("Texto Superior (Watermark):"))
        text_layout = QHBoxLayout()
        self.entry_text = QLineEdit()
        self.entry_text.setPlaceholderText("Digite o texto aqui...")
        self.entry_text.setStyleSheet("background-color: #2B2B2B; color: white; padding: 8px; border-radius: 6px;")
        text_layout.addWidget(self.entry_text)

        self.spin_text_size = QSpinBox()
        self.spin_text_size.setRange(10, 72)
        self.spin_text_size.setValue(22)
        self.spin_text_size.setPrefix("Tamanho: ")
        self.spin_text_size.setStyleSheet("background-color: #2B2B2B; color: white; padding: 5px;")
        text_layout.addWidget(self.spin_text_size)
        layout.addLayout(text_layout)

        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("Posição:"))
        self.combo_text_pos = QComboBox()
        self.combo_text_pos.addItems(["Topo", "Centro", "Rodapé"])
        self.combo_text_pos.setCurrentText("Topo")
        self.combo_text_pos.setStyleSheet("background-color: #2B2B2B; color: white; padding: 5px;")
        pos_layout.addWidget(self.combo_text_pos)
        pos_layout.addStretch()
        layout.addLayout(pos_layout)

        # --- QUALIDADE COM PRESETS ---
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Qualidade:"))
        self.combo_quality = QComboBox()
        self.combo_quality.setStyleSheet("background-color: #2B2B2B; color: white; padding: 8px;")
        self.combo_quality.currentIndexChanged.connect(self.on_quality_changed)
        quality_layout.addWidget(self.combo_quality)

        btn_add_preset = QPushButton("+")
        btn_add_preset.setFixedSize(30, 30)
        btn_add_preset.setToolTip("Criar novo Preset")
        btn_add_preset.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; border-radius: 5px; border: none;")
        btn_add_preset.clicked.connect(self.open_add_preset_dialog)
        quality_layout.addWidget(btn_add_preset)

        btn_delete_preset = QPushButton("-")
        btn_delete_preset.setFixedSize(30, 30)
        btn_delete_preset.setToolTip("Deletar Preset Selecionado")
        btn_delete_preset.setStyleSheet("background-color: #D32F2F; color: white; font-weight: bold; border-radius: 5px; border: none;")
        btn_delete_preset.clicked.connect(self.delete_preset)
        quality_layout.addWidget(btn_delete_preset)

        layout.addLayout(quality_layout)

        # Frame Custom
        self.frame_custom_quality = QFrame()
        self.frame_custom_quality.setFrameShape(QFrame.StyledPanel)
        self.frame_custom_quality.setStyleSheet("background-color: #2A2A2A; border-radius: 5px; padding: 5px;")
        self.frame_custom_quality.setVisible(False)

        cq_layout = QHBoxLayout(self.frame_custom_quality)
        cq_layout.addWidget(QLabel("Bitrate:"))
        self.entry_custom_bitrate = QLineEdit()
        self.entry_custom_bitrate.setPlaceholderText("ex: 5000k")
        self.entry_custom_bitrate.setStyleSheet("background-color: #333; color: white; padding: 5px;")
        cq_layout.addWidget(self.entry_custom_bitrate)

        cq_layout.addWidget(QLabel("Preset:"))
        self.combo_preset = QComboBox()
        self.combo_preset.addItems(["p1 (Mais Rápido)", "p4 (Equilibrado)", "p6 (Lento/Melhor)"])
        self.combo_preset.setStyleSheet("background-color: #333; color: white; padding: 5px;")
        cq_layout.addWidget(self.combo_preset)

        layout.addWidget(self.frame_custom_quality)

        # Checkboxes
        self.chk_hw_accel = QCheckBox("Usar aceleração por hardware (NVIDIA)")
        self.chk_hw_accel.setChecked(self.has_nvidia)
        self.chk_hw_accel.setEnabled(self.has_nvidia)
        self.chk_hw_accel.setStyleSheet("color: #CCC;")
        layout.addWidget(self.chk_hw_accel)

        self.chk_metadata = QCheckBox("Preservar metadados do vídeo original")
        self.chk_metadata.setChecked(True)
        self.chk_metadata.setStyleSheet("color: #CCC;")
        layout.addWidget(self.chk_metadata)

        self.chk_copy_audio = QCheckBox("Copiar áudio sem reencode (mais rápido)")
        self.chk_copy_audio.setChecked(False)
        self.chk_copy_audio.setStyleSheet("color: #CCC;")
        layout.addWidget(self.chk_copy_audio)

        # Progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #444; border-radius: 5px; text-align: center; color: white; height: 25px; } QProgressBar::chunk { background-color: #4A90E2; }")
        layout.addWidget(self.progress_bar)

        # Botões
        btn_layout = QHBoxLayout()
        self.btn_convert = ModernButton("INICIAR CONVERSÃO", "#4CAF50", "#45A049")
        self.btn_convert.clicked.connect(self.start_conversion)
        self.btn_convert.setFixedHeight(45)
        btn_layout.addWidget(self.btn_convert)

        self.btn_cancel = ModernButton("CANCELAR", "#D32F2F", "#B71C1C")
        self.btn_cancel.clicked.connect(self.cancel_conversion)
        self.btn_cancel.setFixedHeight(45)
        self.btn_cancel.setEnabled(False)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.btn_open_folder = QPushButton("Abrir Pasta do Arquivo")
        self.btn_open_folder.setStyleSheet("background-color: transparent; border: 1px solid #555; color: #CCC; padding: 8px;")
        self.btn_open_folder.clicked.connect(self.open_output_folder)
        self.btn_open_folder.setEnabled(False)
        layout.addWidget(self.btn_open_folder)

        # Log
        layout.addWidget(QLabel("Log de Conversão:"))
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("background-color: #121212; color: #00FF00; font-family: Consolas, monospace; font-size: 10px;")
        self.txt_log.setMaximumHeight(200)
        # Optimization: Limit log size to prevent UI lag during long-running batch processes
        self.txt_log.document().setMaximumBlockCount(1000)
        layout.addWidget(self.txt_log)

    def update_ffmpeg_status_ui(self):
        if self.ffmpeg_bin:
            self.lbl_ffmpeg_status.setText(f"FFmpeg: OK ({Path(self.ffmpeg_bin).name})")
            self.lbl_ffmpeg_status.setStyleSheet("color: #4CAF50; font-size: 11px;")
        else:
            self.lbl_ffmpeg_status.setText("FFmpeg: NÃO ENCONTRADO")
            self.lbl_ffmpeg_status.setStyleSheet("color: #F44336; font-size: 11px; font-weight: bold;")

    # --- LÓGICA DE PRESETS ---
    def load_presets_to_combo(self):
        """Carrega os padrões e os presets do usuário no ComboBox."""
        self.combo_quality.blockSignals(True) # Evita disparar on_changed durante o carregamento
        self.combo_quality.clear()

        # Padrões Fixos
        self.combo_quality.addItem("Alta (4200k)", "high")
        self.combo_quality.addItem("Padrão (2800k)", "standard")

        # Presets do Usuário
        for p in self.config.data.get('custom_presets', []):
            self.combo_quality.addItem(f"⚙️ {p['name']}", p)

        self.combo_quality.addItem("Personalizada (Manual)", "manual")

        # Restaura seleção salva
        saved_quality = self.config.data.get("last_quality", "Alta (4200k)")
        index = self.combo_quality.findText(saved_quality)
        if index >= 0:
            self.combo_quality.setCurrentIndex(index)
        else:
            self.combo_quality.setCurrentIndex(0)

        self.combo_quality.blockSignals(False)
        self.toggle_custom_quality_ui()

    def open_add_preset_dialog(self):
        """Abre a janela para criar um novo preset."""
        dlg = AddPresetDialog(self)
        if dlg.exec():
            new_preset = dlg.get_preset_data()
            if new_preset:
                self.config.data['custom_presets'].append(new_preset)
                self.config.save()
                self.load_presets_to_combo()

                # Seleciona o novo preset criado automaticamente
                name = f"⚙️ {new_preset['name']}"
                self.combo_quality.setCurrentText(name)
                QMessageBox.information(self, "Sucesso", f"Preset '{new_preset['name']}' salvo com sucesso!")

    def on_quality_changed(self):
        """Ao mudar a qualidade, atualiza os campos customizados se for um preset salvo."""
        mode = self.combo_quality.currentText()
        data = self.combo_quality.currentData()

        # Se for um objeto de preset (dicionário), preenche os campos
        if isinstance(data, dict):
            self.frame_custom_quality.setVisible(True)
            self.entry_custom_bitrate.setText(data.get('bitrate', ''))
            preset_code = data.get('preset', 'p6')
            # Encontra o texto que corresponde ao código
            idx = self.combo_preset.findText(preset_code, Qt.MatchStartsWith)
            if idx >= 0: self.combo_preset.setCurrentIndex(idx)
        elif mode == "Personalizada (Manual)":
            self.frame_custom_quality.setVisible(True)
        else:
            # Padrão fixo (Alta ou Padrão)
            self.frame_custom_quality.setVisible(False)

    def delete_preset(self):
        """Deleta o preset customizado selecionado."""
        mode = self.combo_quality.currentText()
        data = self.combo_quality.currentData()

        # Só permite deletar presets customizados (que são objetos dict)
        if not isinstance(data, dict):
            QMessageBox.information(self, "Info", "Apenas presets customizados podem ser deletados.\nUse o botão '+' para criar novos presets.")
            return

        preset_name = data.get('name', 'Preset')
        reply = QMessageBox.question(
            self,
            "Deletar Preset",
            f"Deseja realmente deletar o preset '{preset_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Remove o preset da lista
            custom_presets = self.config.data.get('custom_presets', [])
            for i, p in enumerate(custom_presets):
                if p.get('name') == preset_name:
                    custom_presets.pop(i)
                    break

            self.config.save()
            self.load_presets_to_combo()
            self.log(f"Preset '{preset_name}' deletado com sucesso")
            QMessageBox.information(self, "Sucesso", f"Preset '{preset_name}' foi deletado!")

    # --- RESTO DAS FUNÇÕES ---

    def show_ffmpeg_warning(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("FFmpeg Não Encontrado")
        msg.setText("O FFmpeg é necessário para a conversão de vídeos.")
        msg.setInformativeText("Você pode baixá-lo automaticamente (apenas Windows) ou selecioná-lo manualmente.")
        btn_download = msg.addButton("Baixar Automaticamente", QMessageBox.ActionRole)
        btn_manual = msg.addButton("Selecionar Manualmente", QMessageBox.ActionRole)
        btn_info = msg.addButton("Mais Informações", QMessageBox.HelpRole)
        msg.addButton("Cancelar", QMessageBox.RejectRole)
        msg.exec()
        if msg.clickedButton() == btn_download:
            if platform.system() == "Windows": self.download_ffmpeg_windows()
            else: QMessageBox.information(self, "Info", "Download automático disponível apenas para Windows.\nPor favor, instale o FFmpeg manualmente.")
        elif msg.clickedButton() == btn_manual: self.select_ffmpeg_manual()
        elif msg.clickedButton() == btn_info: QDesktopServices.openUrl(QUrl("https://ffmpeg.org/download.html"))

    def download_ffmpeg_windows(self):
        self.log("Iniciando download do FFmpeg...")
        url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        dest_zip = Path("ffmpeg_temp.zip")
        temp_extract_dir = Path("ffmpeg_temp_extract")

        try:
            def report_progress(block_num, block_size, total_size):
                if total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(int(downloaded / total_size * 100), 100)
                    self.progress_bar.setValue(percent)
                    self.log(f"Baixando FFmpeg... {percent}%")

            urllib.request.urlretrieve(url, str(dest_zip), reporthook=report_progress)
            self.log("Download concluído. Extraindo arquivos...")
            import zipfile

            # Limpa diretório temporário se existir
            if temp_extract_dir.exists():
                shutil.rmtree(temp_extract_dir)
            temp_extract_dir.mkdir()

            with zipfile.ZipFile(dest_zip, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_dir)

            # Encontra e copia ffmpeg.exe e ffprobe.exe
            script_dir = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
            copied_files = []

            for exe_file in temp_extract_dir.rglob("ffmpeg.exe"):
                shutil.copy2(exe_file, script_dir / "ffmpeg.exe")
                copied_files.append("ffmpeg.exe")
                break

            for exe_file in temp_extract_dir.rglob("ffprobe.exe"):
                shutil.copy2(exe_file, script_dir / "ffprobe.exe")
                copied_files.append("ffprobe.exe")
                break

            # Limpa arquivos temporários
            dest_zip.unlink()
            shutil.rmtree(temp_extract_dir)

            if copied_files:
                self.log(f"FFmpeg instalado com sucesso! Arquivos: {', '.join(copied_files)}")
                self.ffmpeg_bin = get_ffmpeg_binary()
                self.update_ffmpeg_status_ui()
                self.progress_bar.setValue(0)
                QMessageBox.information(self, "Sucesso", "FFmpeg instalado com sucesso!")
            else:
                raise Exception("Arquivos ffmpeg.exe/ffprobe.exe não encontrados no pacote baixado")

        except Exception as e:
            self.log(f"Erro no download: {e}")
            # Limpa arquivos temporários em caso de erro
            if dest_zip.exists():
                dest_zip.unlink()
            if temp_extract_dir.exists():
                shutil.rmtree(temp_extract_dir)
            QMessageBox.critical(self, "Erro", f"Falha ao baixar FFmpeg:\n{e}\n\nPor favor, baixe manualmente em ffmpeg.org")

    def select_ffmpeg_manual(self):
        file_filter = "Executáveis (*.exe);;Todos os arquivos (*.*)" if platform.system() == "Windows" else "Todos os arquivos (*.*)"
        path, _ = QFileDialog.getOpenFileName(self, "Selecione o executável do FFmpeg", "", file_filter)
        if path and Path(path).exists():
            self.ffmpeg_bin = path
            self.config.data["ffmpeg_path"] = path
            self.config.save()
            self.update_ffmpeg_status_ui()
            self.log(f"FFmpeg configurado: {path}")

    def handle_file_drop(self, path: str):
        if not os.path.exists(path): return QMessageBox.warning(self, "Erro", "Arquivo não encontrado!")
        self.video_path = path
        base_name = Path(path).stem

        # Legenda
        found_sub = False
        for ext in ['.srt', '.ass', '.ssa']:
            possible_sub = Path(path).parent / f"{base_name}{ext}"
            if possible_sub.exists():
                self.subtitle_path = str(possible_sub)
                self.lbl_sub.setText(f"Legenda: {possible_sub.name}")
                found_sub = True
                break
        if not found_sub:
            self.subtitle_path = ""
            self.lbl_sub.setText("Legenda: Nenhuma detectada")

        self.log(f"Vídeo carregado: {Path(path).name}")
        self.drop_area.setText(f"Vídeo Selecionado:\n{Path(path).name}")
        self.btn_open_folder.setEnabled(True)

        self.analyze_audio_tracks()

    def handle_files_drop(self, files: list):
        """Lida com múltiplos arquivos dropados."""
        if len(files) == 0:
            return

        if len(files) == 1:
            # Single file mode
            self.handle_file_drop(files[0])
        else:
            # Batch mode
            reply = QMessageBox.question(
                self,
                "Conversão em Lote",
                f"Deseja converter {len(files)} arquivos em lote?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.batch_queue = files.copy()
                self.batch_mode = True
                self.batch_index = 0
                self.log(f"Modo de lote ativado: {len(files)} arquivos na fila")
                self.process_batch_queue()
            else:
                # Just load first file
                self.handle_file_drop(files[0])

    def process_batch_queue(self):
        """Processa a fila de conversão em lote."""
        if self.batch_index >= len(self.batch_queue):
            # Batch complete
            self.batch_mode = False
            self.batch_queue = []
            self.batch_index = 0
            self.log("FILA DE CONVERSÃO CONCLUÍDA!")
            self.tray_icon.showMessage(
                "HardSub Converter Pro",
                "Todas as conversões em lote foram concluídas!",
                QSystemTrayIcon.Information,
                5000
            )
            QMessageBox.information(self, "Conclusão", "Todas as conversões em lote foram concluídas com sucesso!")
            self.btn_convert.setEnabled(True)
            self.btn_cancel.setEnabled(False)
            return

        # Load next file
        video_path = self.batch_queue[self.batch_index]
        self.log(f"\n{'='*60}")
        self.log(f"Arquivo {self.batch_index + 1}/{len(self.batch_queue)}: {Path(video_path).name}")
        self.log(f"{'='*60}")

        # Auto-load file without prompt
        self.video_path = video_path
        base_name = Path(video_path).stem

        # Auto-detect subtitle
        found_sub = False
        for ext in ['.srt', '.ass', '.ssa']:
            possible_sub = Path(video_path).parent / f"{base_name}{ext}"
            if possible_sub.exists():
                self.subtitle_path = str(possible_sub)
                found_sub = True
                break

        # Dialog to confirm subtitle for this batch file
        dlg = BatchSubtitleDialog(
            self,
            video_path,
            self.subtitle_path if found_sub else "",
            self.batch_index + 1,
            len(self.batch_queue)
        )

        if dlg.exec():
            action, custom_sub = dlg.get_result()

            if action == "skip":
                self.log(f"⏭️  Vídeo pulado pelo usuário")
                self.batch_index += 1
                QTimer.singleShot(500, self.process_batch_queue)
                return
            elif action == "skip_all":
                self.log("⏭️  Lote cancelado pelo usuário (Pular Todos)")
                self.batch_mode = False
                self.batch_queue = []
                self.batch_index = 0
                self.btn_convert.setEnabled(True)
                self.btn_cancel.setEnabled(False)
                return
            elif action == "select_custom":
                self.subtitle_path = custom_sub
                self.lbl_sub.setText(f"Legenda: {Path(custom_sub).name}")
                self.log(f"Legenda customizada: {Path(custom_sub).name}")
            elif action == "no_subtitle":
                self.subtitle_path = ""
                self.lbl_sub.setText("Legenda: Sem legenda")
                self.log("Convertendo sem legenda")
            else:
                if found_sub:
                    self.lbl_sub.setText(f"Legenda: {Path(self.subtitle_path).name}")
                    self.log(f"Usando legenda detectada: {Path(self.subtitle_path).name}")
                else:
                    self.subtitle_path = ""
                    self.lbl_sub.setText("Legenda: Nenhuma detectada")
                    self.log("Nenhuma legenda detectada, convertendo sem legenda")
        else:
            self.log("❌ Lote cancelado pelo usuário")
            self.batch_mode = False
            self.batch_queue = []
            self.batch_index = 0
            self.btn_convert.setEnabled(True)
            self.btn_cancel.setEnabled(False)
            return

        self.drop_area.setText(f"Lote: {self.batch_index + 1}/{len(self.batch_queue)}\n{Path(video_path).name}")
        self.btn_open_folder.setEnabled(True)

        # Start conversion automatically
        self.start_batch_conversion()

    def start_batch_conversion(self):
        """Inicia conversão de um arquivo na fila de lote."""
        if not self.ffmpeg_bin:
            QMessageBox.critical(self, "Erro", "FFmpeg não está configurado!")
            return

        self.save_current_settings()
        self.progress_bar.setValue(0)
        self.txt_log.clear()

        cmd, output_path, encoder_type, encoder_color = self.build_command()
        self.lbl_encoder_status.setText(f"Encoder: {encoder_type}")
        self.lbl_encoder_status.setStyleSheet(f"color: {encoder_color}; font-size: 11px;")
        self.log(f"Arquivo de saída: {Path(output_path).name}")
        self.log(f"Executando FFmpeg...")

        self.worker = FFmpegWorker(cmd, output_path)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.log_signal.connect(self.log)
        self.worker.finished_signal.connect(self.batch_conversion_finished)
        self.worker.start()

    def batch_conversion_finished(self, code: int, output_path: str):
        """Callback quando uma conversão em lote termina."""
        self.log(f"{'='*60}")
        if code == 0:
            self.log(f"✓ CONVERSÃO CONCLUÍDA: {Path(output_path).name}")
            if Path(output_path).exists():
                size_mb = Path(output_path).stat().st_size / (1024 * 1024)
                self.log(f"  Tamanho: {size_mb:.2f} MB")
        else:
            self.log(f"✗ FALHA NA CONVERSÃO (Código: {code})")

        # Move to next file
        self.batch_index += 1
        QTimer.singleShot(1000, self.process_batch_queue)

    def analyze_audio_tracks(self):
        self.combo_audio.clear()
        self.combo_audio.addItem("Padrão (Todas as faixas)")
        self.combo_audio.setEnabled(False)
        self.lbl_audio.setText("Áudio: Analisando...")
        self.probe_thread = ProbeWorker(self.ffmpeg_bin, self.video_path)
        self.probe_thread.finished_signal.connect(self.populate_audio_combo)
        self.probe_thread.start()

    def populate_audio_combo(self, streams):
        self.combo_audio.clear()
        self.combo_audio.addItem("Padrão (Todas as faixas)")
        if streams:
            for s in streams: self.combo_audio.addItem(s['title'], s['index'])
            self.lbl_audio.setText("Áudio:")
            self.combo_audio.setEnabled(True)
        else:
            self.lbl_audio.setText("Áudio: Nenhuma faixa detectada")
            self.combo_audio.setEnabled(False)

    def select_video(self):
        start_dir = self.config.data.get("last_video_dir", "")
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Selecione os Vídeos", start_dir,
            "Vídeos (*.mkv *.mp4 *.avi *.mov *.wmv *.flv);;Todos os arquivos (*.*)"
        )
        if paths:
            if len(paths) == 1:
                self.handle_file_drop(paths[0])
            else:
                self.handle_files_drop(paths)
            self.config.data["last_video_dir"] = str(Path(paths[0]).parent)
            self.config.save()

    def select_subtitle(self):
        if not self.video_path: return QMessageBox.warning(self, "Aviso", "Selecione um vídeo primeiro.")
        path, _ = QFileDialog.getOpenFileName(self, "Selecione a Legenda", str(Path(self.video_path).parent), "Legendas (*.srt *.ass *.ssa);;Todos os arquivos (*.*)")
        if path:
            self.subtitle_path = path
            self.lbl_sub.setText(f"Legenda: {Path(path).name}")
            self.log(f"Legenda selecionada: {Path(path).name}")

    def clear_subtitle(self):
        self.subtitle_path = ""
        self.lbl_sub.setText("Legenda: Nenhuma")
        self.log("Legenda removida")

    def toggle_custom_quality_ui(self):
        mode = self.combo_quality.currentText()
        self.frame_custom_quality.setVisible(mode == "Personalizada (Manual)" or mode.startswith("⚙️"))

    def load_settings(self):
        self.load_presets_to_combo()
        self.entry_text.setText(self.config.data.get("last_text", ""))
        self.chk_hw_accel.setChecked(self.config.data.get("use_hardware_accel", True) and self.has_nvidia)
        self.spin_text_size.setValue(self.config.data.get("text_size", 22))
        self.chk_metadata.setChecked(self.config.data.get("preserve_metadata", True))
        self.chk_copy_audio.setChecked(self.config.data.get("copy_audio", False))

        pos = self.config.data.get("text_position", "top")
        pos_map = {"top": "Topo", "center": "Centro", "bottom": "Rodapé"}
        self.combo_text_pos.setCurrentText(pos_map.get(pos, "Topo"))

    def save_current_settings(self):
        self.config.data["last_quality"] = self.combo_quality.currentText()
        self.config.data["last_text"] = self.entry_text.text()
        self.config.data["use_hardware_accel"] = self.chk_hw_accel.isChecked()
        self.config.data["text_size"] = self.spin_text_size.value()
        self.config.data["preserve_metadata"] = self.chk_metadata.isChecked()
        self.config.data["copy_audio"] = self.chk_copy_audio.isChecked()

        pos_map = {"Topo": "top", "Centro": "center", "Rodapé": "bottom"}
        self.config.data["text_position"] = pos_map.get(self.combo_text_pos.currentText(), "top")
        self.config.save()

    def log(self, msg: str):
        self.txt_log.append(msg)
        sb = self.txt_log.verticalScrollBar()
        sb.setValue(sb.maximum())

    def start_conversion(self):
        if not self.ffmpeg_bin: return QMessageBox.critical(self, "Erro", "FFmpeg não está configurado!")
        if not self.video_path or not Path(self.video_path).exists(): return QMessageBox.warning(self, "Aviso", "Selecione um vídeo válido primeiro.")

        self.save_current_settings()
        self.btn_convert.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setValue(0)
        self.txt_log.clear()
        self.log("=" * 50)
        self.log("INICIANDO CONVERSÃO")
        self.log("=" * 50)

        cmd, output_path, encoder_type, encoder_color = self.build_command()
        self.lbl_encoder_status.setText(f"Encoder: {encoder_type}")
        self.lbl_encoder_status.setStyleSheet(f"color: {encoder_color}; font-size: 11px;")
        self.log(f"Arquivo de saída: {Path(output_path).name}")
        self.log(f"Executando FFmpeg...")

        self.worker = FFmpegWorker(cmd, output_path)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.log_signal.connect(self.log)
        self.worker.finished_signal.connect(self.conversion_finished)
        self.worker.start()

    def cancel_conversion(self):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(self, "Cancelar", "Deseja realmente cancelar a conversão?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.log("Cancelando conversão...")
                self.worker.stop()

    def build_command(self):
        # Determina os valores baseados na seleção atual
        mode = self.combo_quality.currentText()
        data = self.combo_quality.currentData()

        if isinstance(data, dict):
            # É um preset customizado carregado
            b_v = data.get('bitrate')
            maxrate = data.get('maxrate', '')
            bufsize = data.get('bufsize', '')
            preset = data.get('preset', 'p6')
            # Usa a função auxiliar para calcular valores
            b_v, maxrate, bufsize = calculate_bitrate_values(b_v, maxrate, bufsize)
        elif mode == "Personalizada (Manual)":
            # Manual no momento
            b_v = self.entry_custom_bitrate.text() if self.entry_custom_bitrate.text() else "3000k"
            # Usa a função auxiliar para calcular valores automaticamente
            b_v, maxrate, bufsize = calculate_bitrate_values(b_v)

            preset_text = self.combo_preset.currentText()
            preset = preset_text.split()[0]
        elif "Alta" in mode:
            b_v, maxrate, bufsize = "4200k", "5200k", "9000k"
            preset = "p6"
        else: # Padrão
            b_v, maxrate, bufsize = "2800k", "3500k", "6000k"
            preset = "p6"

        text = self.entry_text.text()

        # Sanitiza o nome do arquivo de saída usando regex pré-compilado
        stem = SANITIZE_PATTERN.sub('_', Path(self.video_path).stem)
        output_name = str(Path(self.video_path).parent / f"{stem}@converted.mp4")

        cmd = [self.ffmpeg_bin, "-y", "-err_detect", "ignore_err", "-fflags", "+genpts"]

        if self.chk_hw_accel.isChecked() and self.has_nvidia: cmd.extend(["-hwaccel", "cuda"])
        cmd.extend(["-i", self.video_path])

        filter_parts = []
        font = get_font_path()

        if text:
            safe_text = escape_filter_text(text)
            pos_map = {"Topo": "y=20", "Centro": "y=(h-text_h)/2", "Rodapé": "y=h-text_h-20"}
            y_pos = pos_map.get(self.combo_text_pos.currentText(), "y=20")

            if font:
                safe_font = escape_path_for_filter(font)
                drawtext = (f"drawtext=fontfile='{safe_font}':text='{safe_text}':fontcolor=white@0.9:fontsize={self.spin_text_size.value()}:box=1:boxcolor=black@0.4:boxborderw=10:x=(w-text_w)/2:{y_pos}")
            else:
                drawtext = (f"drawtext=text='{safe_text}':fontcolor=white@0.9:fontsize={self.spin_text_size.value()}:box=1:boxcolor=black@0.4:boxborderw=10:x=(w-text_w)/2:{y_pos}")
            filter_parts.append(drawtext)

        if self.subtitle_path and Path(self.subtitle_path).exists():
            safe_sub = escape_path_for_filter(self.subtitle_path)
            filter_parts.append(f"subtitles='{safe_sub}'")

        if filter_parts:
            filter_complex = f"[0:v]{','.join(filter_parts)}[vout]"
            cmd.extend(["-filter_complex", filter_complex, "-map", "[vout]"])
        else:
            cmd.extend(["-map", "0:v"])

        selected_audio_index = self.combo_audio.currentData()
        if selected_audio_index is not None: cmd.extend(["-map", f"0:{selected_audio_index}"])
        else: cmd.extend(["-map", "0:a?"])

        if self.chk_hw_accel.isChecked() and self.has_nvidia:
            cmd.extend(["-c:v", "h264_nvenc", "-preset", preset])
            encoder_type = "NVENC"
            encoder_color = "#4CAF50"
        else:
            cmd.extend(["-c:v", "libx264", "-preset", "medium"])
            encoder_type = "CPU"
            encoder_color = "#AAA"

        if self.chk_copy_audio.isChecked():
            cmd.extend(["-c:a", "copy"])
        else:
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])

        cmd.extend(["-rc", "vbr", "-b:v", b_v, "-maxrate", maxrate, "-bufsize", bufsize, "-profile:v", "high", "-pix_fmt", "yuv420p"])

        if self.chk_metadata.isChecked(): cmd.extend(["-map_metadata", "0"])
        cmd.extend(["-movflags", "+faststart", output_name])

        return cmd, output_name, encoder_type, encoder_color

    def conversion_finished(self, code: int, output_path: str):
        self.btn_convert.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.lbl_encoder_status.setText("Encoder: --")
        self.lbl_encoder_status.setStyleSheet("color: #AAA; font-size: 11px;")
        self.log("=" * 50)
        if code == 0:
            self.log("CONVERSÃO CONCLUÍDA COM SUCESSO!")
            self.log(f"Arquivo salvo: {Path(output_path).name}")
            if Path(output_path).exists():
                size_mb = Path(output_path).stat().st_size / (1024 * 1024)
                self.log(f"Tamanho do arquivo: {size_mb:.2f} MB")

            # System tray notification
            self.tray_icon.showMessage(
                "HardSub Converter Pro",
                f"Conversão finalizada!\n\n{Path(output_path).name}",
                QSystemTrayIcon.Information,
                5000
            )

            QMessageBox.information(self, "Sucesso", f"Conversão finalizada!\n\nArquivo: {Path(output_path).name}")
        elif code == -2:
            self.log("CONVERSÃO CANCELADA PELO USUÁRIO")
            self.tray_icon.showMessage(
                "HardSub Converter Pro",
                "Conversão cancelada",
                QSystemTrayIcon.Warning,
                3000
            )
        else:
            self.log(f"FALHA NA CONVERSÃO (Código de erro: {code})")
            self.tray_icon.showMessage(
                "HardSub Converter Pro",
                f"Falha na conversão (Código: {code})",
                QSystemTrayIcon.Critical,
                5000
            )
            QMessageBox.warning(self, "Erro na Conversão", f"A conversão falhou com código {code}.\nVerifique o log para mais detalhes.")

    def open_output_folder(self):
        if self.video_path: QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(self.video_path).parent.absolute())))

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(self, "Fechar", "Há uma conversão em andamento. Deseja realmente sair?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.worker.stop()
                self.worker.wait()
                event.accept()
            else: event.ignore()
        else: event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = Path(__file__).parent / "icon.ico"
    if icon_path.exists():
        from PySide6.QtGui import QIcon
        app.setWindowIcon(QIcon(str(icon_path)))
    window = VideoConverterApp()
    window.show()
    sys.exit(app.exec())
