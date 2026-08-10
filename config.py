"""
إعدادات التطبيق العامة - Smart Data Cleaner
"""

from pathlib import Path

# إعدادات البيئة
DEBUG_MODE = False
TESTING_MODE = False

# إعدادات قاعدة البيانات (مستقبلاً)
DATABASE_PATH = Path.home() / ".smartdatacleaner" / "data.db"

# إعدادات الأداء
CHUNK_SIZE = 10000  # عدد الصفوف لمعالجة كل جزء
MAX_PREVIEW_ROWS = 1000  # الحد الأقصى للصفوف في المعاينة
THREAD_COUNT = 4  # عدد الخيوط للمعالجة المتوازية

# إعدادات الذاكرة
MAX_MEMORY_USAGE_MB = 2000  # الحد الأقصى لاستخدام الذاكرة

# إعدادات المظهر
THEME_COLORS = {
    "dark": {
        "bg": "#1e1e1e",
        "fg": "#ffffff",
        "accent": "#0084ff",
    },
    "light": {
        "bg": "#ffffff",
        "fg": "#000000",
        "accent": "#0084ff",
    }
}

# إعدادات الخطوط
FONT_FAMILY = "Segoe UI"
FONT_SIZE_NORMAL = 11
FONT_SIZE_TITLE = 16
FONT_SIZE_SMALL = 9

# إعدادات التوافق
MIN_PYTHON_VERSION = (3, 13)
