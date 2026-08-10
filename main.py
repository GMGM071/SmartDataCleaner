"""
ملف الإدخال الرئيسي - Smart Data Cleaner
"""

import sys
from pathlib import Path

# إضافة المسار الرئيسي
sys.path.insert(0, str(Path(__file__).parent))

from gui.main_window import main
from utils.logger import logger
from utils.config_manager import config_manager


def initialize_app():
    """تهيئة التطبيق"""
    try:
        # التحقق من المجلدات
        config_manager.validate_directories()
        
        # تسجيل بدء التطبيق
        logger.info("=" * 50)
        logger.info("تم بدء تطبيق Smart Data Cleaner")
        logger.info("=" * 50)
        
        return True
    except Exception as e:
        logger.error(f"خطأ في تهيئة التطبيق: {e}")
        return False


if __name__ == "__main__":
    if initialize_app():
        main()
    else:
        print("خطأ في تهيئة التطبيق")
        sys.exit(1)
