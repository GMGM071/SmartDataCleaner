"""
مدير الإعدادات - Smart Data Cleaner
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field
import os

from constants import CONFIG_FILE, APP_NAME
from utils.logger import logger


@dataclass
class CleaningConfig:
    """إعدادات التنظيف الافتراضية"""
    remove_duplicates: bool = True
    remove_null_values: bool = True
    normalize_whitespace: bool = True
    remove_special_characters: bool = False
    normalize_case: str = "none"  # none, lower, upper, title
    remove_invisible_characters: bool = True
    handle_outliers: bool = False
    outlier_method: str = "iqr"  # iqr, zscore
    outlier_threshold: float = 1.5


@dataclass
class UIConfig:
    """إعدادات واجهة المستخدم"""
    theme: str = "dark"
    window_width: int = 1200
    window_height: int = 800
    auto_save: bool = True
    save_interval: int = 300  # بالثواني
    show_preview: bool = True
    preview_rows: int = 100


@dataclass
class ApplicationConfig:
    """إعدادات التطبيق الرئيسية"""
    language: str = "ar"
    log_level: str = "INFO"
    max_file_size_mb: int = 500
    temp_directory: Path = field(default_factory=lambda: Path("./temp"))
    output_directory: Path = field(default_factory=lambda: Path("./output"))
    cleaning: CleaningConfig = field(default_factory=CleaningConfig)
    ui: UIConfig = field(default_factory=UIConfig)


class ConfigManager:
    """
    مدير الإعدادات المركزي
    
    يدير تحميل وحفظ الإعدادات من ملف JSON
    """
    
    _instance: Optional['ConfigManager'] = None
    
    def __new__(cls) -> 'ConfigManager':
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """تهيئة مدير الإعدادات"""
        self.config_file = CONFIG_FILE
        self.config = self._load_config()
        logger.info(f"تم تحميل الإعدادات من {self.config_file}")
    
    def _load_config(self) -> ApplicationConfig:
        """
        تحميل الإعدادات من الملف
        
        Returns:
            ApplicationConfig: كائن الإعدادات
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return self._dict_to_config(data)
            except Exception as e:
                logger.warning(f"خطأ في تحميل الإعدادات: {e}. استخدام الإعدادات الافتراضية.")
                return ApplicationConfig()
        else:
            # إنشاء الإعدادات الافتراضية
            config = ApplicationConfig()
            self._save_config(config)
            return config
    
    def _save_config(self, config: ApplicationConfig) -> None:
        """
        حفظ الإعدادات إلى الملف
        
        Args:
            config: كائن الإعدادات
        """
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config_dict = asdict(config)
            # تحويل Path إلى str للـ JSON
            config_dict['temp_directory'] = str(config_dict['temp_directory'])
            config_dict['output_directory'] = str(config_dict['output_directory'])
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=4, ensure_ascii=False)
            
            logger.info(f"تم حفظ الإعدادات في {self.config_file}")
        except Exception as e:
            logger.error(f"خطأ في حفظ الإعدادات: {e}")
    
    def _dict_to_config(self, data: Dict[str, Any]) -> ApplicationConfig:
        """تحويل قاموس إلى كائن ApplicationConfig"""
        try:
            cleaning_data = data.get('cleaning', {})
            ui_data = data.get('ui', {})
            
            return ApplicationConfig(
                language=data.get('language', 'ar'),
                log_level=data.get('log_level', 'INFO'),
                max_file_size_mb=data.get('max_file_size_mb', 500),
                temp_directory=Path(data.get('temp_directory', './temp')),
                output_directory=Path(data.get('output_directory', './output')),
                cleaning=CleaningConfig(
                    remove_duplicates=cleaning_data.get('remove_duplicates', True),
                    remove_null_values=cleaning_data.get('remove_null_values', True),
                    normalize_whitespace=cleaning_data.get('normalize_whitespace', True),
                    remove_special_characters=cleaning_data.get('remove_special_characters', False),
                    normalize_case=cleaning_data.get('normalize_case', 'none'),
                    remove_invisible_characters=cleaning_data.get('remove_invisible_characters', True),
                    handle_outliers=cleaning_data.get('handle_outliers', False),
                    outlier_method=cleaning_data.get('outlier_method', 'iqr'),
                    outlier_threshold=cleaning_data.get('outlier_threshold', 1.5),
                ),
                ui=UIConfig(
                    theme=ui_data.get('theme', 'dark'),
                    window_width=ui_data.get('window_width', 1200),
                    window_height=ui_data.get('window_height', 800),
                    auto_save=ui_data.get('auto_save', True),
                    save_interval=ui_data.get('save_interval', 300),
                    show_preview=ui_data.get('show_preview', True),
                    preview_rows=ui_data.get('preview_rows', 100),
                )
            )
        except Exception as e:
            logger.error(f"خطأ في تحويل الإعدادات: {e}")
            return ApplicationConfig()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        الحصول على قيمة إعداد معين
        
        Args:
            key: مفتاح الإعداد (يدعم النقاط: "cleaning.remove_duplicates")
            default: القيمة الافتراضية
        
        Returns:
            قيمة الإعداد
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                if isinstance(value, dict):
                    value = value[k]
                else:
                    value = getattr(value, k)
            return value
        except (KeyError, AttributeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        تعيين قيمة إعداد معين
        
        Args:
            key: مفتاح الإعداد
            value: القيمة الجديدة
        """
        keys = key.split('.')
        obj = self.config
        
        try:
            for k in keys[:-1]:
                obj = getattr(obj, k)
            
            setattr(obj, keys[-1], value)
            self._save_config(self.config)
        except Exception as e:
            logger.error(f"خطأ في تعيين الإعداد {key}: {e}")
    
    def reset_to_defaults(self) -> None:
        """إعادة تعيين الإعدادات إلى الافتراضية"""
        self.config = ApplicationConfig()
        self._save_config(self.config)
        logger.info("تم إعادة تعيين الإعدادات إلى الافتراضية")
    
    def validate_directories(self) -> None:
        """التحقق من المجلدات وإنشاؤها إذا لزم الأمر"""
        self.config.temp_directory.mkdir(parents=True, exist_ok=True)
        self.config.output_directory.mkdir(parents=True, exist_ok=True)
        logger.info("تم التحقق من المجلدات")


# اختصار سهل الاستخدام
config_manager = ConfigManager()
