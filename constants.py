"""
ثوابت التطبيق - Smart Data Cleaner
"""

from enum import Enum
from pathlib import Path

# معلومات التطبيق
APP_NAME = "Smart Data Cleaner"
APP_VERSION = "1.0.0"
APP_AUTHOR = "GMGM071"
APP_DESCRIPTION = "أسهل برنامج لتنظيف بيانات Excel"

# المسارات
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
REPORTS_DIR = BASE_DIR / "reports" / "output"
CONFIG_DIR = BASE_DIR / "config"
THEMES_DIR = BASE_DIR / "themes"

# إعدادات الملفات
SUPPORTED_FORMATS = [".xlsx", ".xls", ".csv"]
EXCEL_EXTENSIONS = [".xlsx", ".xls"]
CSV_EXTENSION = ".csv"
MAX_FILE_SIZE_MB = 500
MAX_ROWS = 1_000_000

# إعدادات الواجهة الرسومية
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600

# الألوان (Dark Mode)
COLOR_DARK_BG = "#1e1e1e"
COLOR_DARK_FG = "#ffffff"
COLOR_DARK_ACCENT = "#0084ff"
COLOR_DARK_SUCCESS = "#00c853"
COLOR_DARK_WARNING = "#ff9800"
COLOR_DARK_ERROR = "#f44336"

# الألوان (Light Mode)
COLOR_LIGHT_BG = "#ffffff"
COLOR_LIGHT_FG = "#000000"
COLOR_LIGHT_ACCENT = "#0084ff"
COLOR_LIGHT_SUCCESS = "#00c853"
COLOR_LIGHT_WARNING = "#ff9800"
COLOR_LIGHT_ERROR = "#f44336"

# إعدادات اللغات
SUPPORTED_LANGUAGES = {
    "ar": "العربية",
    "en": "English",
    "fr": "Français",
    "de": "Deutsch",
    "es": "Español",
    "ja": "日本語",
    "zh": "中文",
    "ko": "한국어",
}

DEFAULT_LANGUAGE = "ar"

# إعدادات التسجيل
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = BASE_DIR / "logs" / "app.log"

# إعدادات التقارير
REPORT_FORMATS = ["txt", "json", "pdf"]
DEFAULT_REPORT_FORMAT = "json"

# أنماط البيانات
class DataType(Enum):
    """أنواع البيانات"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    PHONE = "phone"
    EMAIL = "email"
    CURRENCY = "currency"
    UNKNOWN = "unknown"

# حالات التنظيف
class CleaningOperation(Enum):
    """عمليات التنظيف"""
    REMOVE_DUPLICATES = "remove_duplicates"
    REMOVE_EMPTY_ROWS = "remove_empty_rows"
    REMOVE_EMPTY_COLUMNS = "remove_empty_columns"
    TRIM_WHITESPACE = "trim_whitespace"
    NORMALIZE_WHITESPACE = "normalize_whitespace"
    CLEAN_PHONE = "clean_phone"
    CLEAN_EMAIL = "clean_email"
    CLEAN_DATE = "clean_date"
    CLEAN_NUMBER = "clean_number"
    CLEAN_CURRENCY = "clean_currency"
    NORMALIZE_CASE = "normalize_case"

# رموز العملات الشائعة
CURRENCY_SYMBOLS = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
    "﷼": "IRR",
    "₹": "INR",
    "₽": "RUB",
    "¢": "CNY",
}

# تنسيقات التاريخ المدعومة
DATE_FORMATS = [
    "%Y-%m-%d",      # ISO Format
    "%d-%m-%Y",      # DD-MM-YYYY
    "%m-%d-%Y",      # MM-DD-YYYY
    "%Y/%m/%d",      # YYYY/MM/DD
    "%d/%m/%Y",      # DD/MM/YYYY
    "%m/%d/%Y",      # MM/DD/YYYY
    "%d.%m.%Y",      # DD.MM.YYYY (German)
    "%Y.%m.%d",      # YYYY.MM.DD
    "%d-%b-%Y",      # DD-Mon-YYYY
    "%b-%d-%Y",      # Mon-DD-YYYY
]

# أنماط البريد الإلكتروني
EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# أنماط أرقام الهواتف
PHONE_PATTERNS = {
    "international": r"^\+?[1-9]\d{1,14}$",  # E.164
    "us": r"^(\+1)?[\s.-]?\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}$",
    "ar": r"^(\+966|0)[0-9]{8,9}$",  # Saudi Arabia
}

# قيم افتراضية
DEFAULT_SHEET_NAME = "Sheet1"
DEFAULT_OUTPUT_FILENAME = "cleaned_data.xlsx"
DEFAULT_REPORT_FILENAME = "cleaning_report.json"

# رسائل الخطأ
ERROR_MESSAGES = {
    "file_not_found": "الملف غير موجود",
    "invalid_file": "صيغة الملف غير مدعومة",
    "file_too_large": "حجم الملف كبير جداً",
    "permission_denied": "لا توجد صلاحيات كافية",
    "corrupted_file": "الملف تالف",
    "unknown_error": "خطأ غير معروف",
}

# رسائل النجاح
SUCCESS_MESSAGES = {
    "file_loaded": "تم تحميل الملف بنجاح",
    "file_saved": "تم حفظ الملف بنجاح",
    "cleaning_completed": "تم التنظيف بنجاح",
    "report_generated": "تم توليد التقرير بنجاح",
}
