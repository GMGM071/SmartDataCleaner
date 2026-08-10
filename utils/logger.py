"""
نظام التسجيل - Smart Data Cleaner
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from constants import APP_NAME, LOG_LEVEL, LOG_FORMAT, LOG_FILE


class Logger:
    """
    نظام التسجيل المركزي للتطبيق
    
    Attributes:
        name: اسم المُسجِّل
        logger: كائن Logger من مكتبة logging
    """
    
    _instance: Optional['Logger'] = None
    _loggers: dict = {}
    
    def __new__(cls, name: str = APP_NAME) -> 'Logger':
        """Singleton pattern - إنشاء instance واحد فقط"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """تهيئة نظام التسجيل"""
        # إنشاء مجلد السجلات
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # إعدادات التسجيل
        log_level = getattr(logging, LOG_LEVEL, logging.INFO)
        
        # تنسيق السجل
        formatter = logging.Formatter(LOG_FORMAT)
        
        # معالج الملف
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE,
            maxBytes=10_000_000,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        
        # معالج الكونسول
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        
        # Logger الرئيسي
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        الحصول على logger باسم معين
        
        Args:
            name: اسم المُسجِّل (عادة __name__)
        
        Returns:
            كائن Logger
        """
        if name not in Logger._loggers:
            Logger._loggers[name] = logging.getLogger(name)
        return Logger._loggers[name]
    
    @staticmethod
    def info(message: str) -> None:
        """تسجيل رسالة معلومات"""
        logging.getLogger(APP_NAME).info(message)
    
    @staticmethod
    def warning(message: str) -> None:
        """تسجيل رسالة تحذير"""
        logging.getLogger(APP_NAME).warning(message)
    
    @staticmethod
    def error(message: str, exc_info: bool = False) -> None:
        """تسجيل رسالة خطأ"""
        logging.getLogger(APP_NAME).error(message, exc_info=exc_info)
    
    @staticmethod
    def debug(message: str) -> None:
        """تسجيل رسالة تصحيح"""
        logging.getLogger(APP_NAME).debug(message)
    
    @staticmethod
    def critical(message: str) -> None:
        """تسجيل رسالة حرجة"""
        logging.getLogger(APP_NAME).critical(message)


# اختصار سهل الاستخدام
logger = Logger.get_logger(__name__)
