"""
مدير الملفات - Smart Data Cleaner
"""

import csv
import pandas as pd
from pathlib import Path
from typing import List, Optional, Union, Tuple
import shutil
from datetime import datetime

from constants import SUPPORTED_FORMATS
from utils.logger import logger
from utils.config_manager import config_manager


class FileManager:
    """
    مدير الملفات - يتعامل مع تحميل وحفظ البيانات
    """
    
    @staticmethod
    def is_supported_format(file_path: Union[str, Path]) -> bool:
        """
        التحقق من أن نوع الملف مدعوم
        
        Args:
            file_path: مسار الملف
        
        Returns:
            True إذا كان النوع مدعوماً
        """
        ext = Path(file_path).suffix.lower()
        return ext in SUPPORTED_FORMATS
    
    @staticmethod
    def get_file_info(file_path: Union[str, Path]) -> dict:
        """
        الحصول على معلومات الملف
        
        Args:
            file_path: مسار الملف
        
        Returns:
            قاموس يحتوي على معلومات الملف
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"الملف غير موجود: {file_path}")
        
        stat = path.stat()
        
        return {
            'name': path.name,
            'path': str(path.absolute()),
            'size_bytes': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'format': path.suffix.lower(),
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
        }
    
    @staticmethod
    def load_csv(
        file_path: Union[str, Path],
        encoding: str = 'utf-8',
        delimiter: str = ','
    ) -> pd.DataFrame:
        """
        تحميل ملف CSV
        
        Args:
            file_path: مسار الملف
            encoding: ترميز الملف
            delimiter: الفاصل بين الأعمدة
        
        Returns:
            DataFrame
        """
        try:
            logger.info(f"جاري تحميل ملف CSV: {file_path}")
            df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter)
            logger.info(f"تم تحميل الملف بنجاح. الأبعاد: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"خطأ في تحميل CSV: {e}")
            raise
    
    @staticmethod
    def load_excel(
        file_path: Union[str, Path],
        sheet_name: Union[str, int] = 0
    ) -> pd.DataFrame:
        """
        تحميل ملف Excel
        
        Args:
            file_path: مسار الملف
            sheet_name: اسم أو رقم الورقة
        
        Returns:
            DataFrame
        """
        try:
            logger.info(f"جاري تحميل ملف Excel: {file_path}")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"تم تحميل الملف بنجاح. الأبعاد: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"خطأ في تحميل Excel: {e}")
            raise
    
    @staticmethod
    def load_json(file_path: Union[str, Path]) -> Union[pd.DataFrame, dict]:
        """
        تحميل ملف JSON
        
        Args:
            file_path: مسار الملف
        
        Returns:
            DataFrame أو dict
        """
        try:
            logger.info(f"جاري تحميل ملف JSON: {file_path}")
            df = pd.read_json(file_path)
            logger.info(f"تم تحميل الملف بنجاح. الأبعاد: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"خطأ في تحميل JSON: {e}")
            raise
    
    @staticmethod
    def load_file(
        file_path: Union[str, Path],
        **kwargs
    ) -> pd.DataFrame:
        """
        تحميل ملف تلقائياً حسب النوع
        
        Args:
            file_path: مسار الملف
            **kwargs: معاملات إضافية
        
        Returns:
            DataFrame
        """
        path = Path(file_path)
        
        # التحقق من حجم الملف
        size_mb = path.stat().st_size / (1024 * 1024)
        max_size = config_manager.get('max_file_size_mb', 500)
        
        if size_mb > max_size:
            raise ValueError(f"حجم الملف ({size_mb:.2f}MB) يتجاوز الحد الأقصى ({max_size}MB)")
        
        # التحقق من صيغة الملف
        if not FileManager.is_supported_format(path):
            raise ValueError(f"نوع الملف غير مدعوم: {path.suffix}")
        
        ext = path.suffix.lower()
        
        if ext == '.csv':
            return FileManager.load_csv(path, **kwargs)
        elif ext in ['.xls', '.xlsx']:
            return FileManager.load_excel(path, **kwargs)
        elif ext == '.json':
            return FileManager.load_json(path, **kwargs)
        else:
            raise ValueError(f"نوع الملف غير مدعوم: {ext}")
    
    @staticmethod
    def save_csv(
        df: pd.DataFrame,
        file_path: Union[str, Path],
        index: bool = False,
        encoding: str = 'utf-8'
    ) -> None:
        """
        حفظ البيانات كملف CSV
        
        Args:
            df: DataFrame المراد حفظه
            file_path: مسار الملف
            index: هل يتم حفظ الفهرس
            encoding: ترميز الملف
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_csv(path, index=index, encoding=encoding)
            logger.info(f"تم حفظ الملف بنجاح: {file_path}")
        except Exception as e:
            logger.error(f"خطأ في حفظ CSV: {e}")
            raise
    
    @staticmethod
    def save_excel(
        df: pd.DataFrame,
        file_path: Union[str, Path],
        sheet_name: str = 'Sheet1',
        index: bool = False
    ) -> None:
        """
        حفظ البيانات كملف Excel
        
        Args:
            df: DataFrame المراد حفظه
            file_path: مسار الملف
            sheet_name: اسم الورقة
            index: هل يتم حفظ الفهرس
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_excel(path, sheet_name=sheet_name, index=index)
            logger.info(f"تم حفظ الملف بنجاح: {file_path}")
        except Exception as e:
            logger.error(f"خطأ في حفظ Excel: {e}")
            raise
    
    @staticmethod
    def save_file(
        df: pd.DataFrame,
        file_path: Union[str, Path],
        **kwargs
    ) -> None:
        """
        حفظ البيانات تلقائياً حسب نوع الملف
        
        Args:
            df: DataFrame المراد حفظه
            file_path: مسار الملف
            **kwargs: معاملات إضافية
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext == '.csv':
            FileManager.save_csv(df, path, **kwargs)
        elif ext in ['.xls', '.xlsx']:
            FileManager.save_excel(df, path, **kwargs)
        elif ext == '.json':
            df.to_json(path)
            logger.info(f"تم حفظ الملف بنجاح: {file_path}")
        else:
            raise ValueError(f"نوع الملف غير مدعوم: {ext}")
    
    @staticmethod
    def backup_file(file_path: Union[str, Path]) -> Path:
        """
        إنشاء نسخة احتياطية من الملف
        
        Args:
            file_path: مسار الملف الأصلي
        
        Returns:
            مسار الملف النسخة الاحتياطية
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"الملف غير موجود: {file_path}")
        
        # إنشاء اسم للنسخة الاحتياطية
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{path.stem}_backup_{timestamp}{path.suffix}"
        backup_path = path.parent / backup_name
        
        shutil.copy2(path, backup_path)
        logger.info(f"تم إنشاء نسخة احتياطية: {backup_path}")
        
        return backup_path
    
    @staticmethod
    def delete_file(file_path: Union[str, Path]) -> None:
        """
        حذف ملف
        
        Args:
            file_path: مسار الملف
        """
        path = Path(file_path)
        
        if path.exists():
            path.unlink()
            logger.info(f"تم حذف الملف: {file_path}")
        else:
            logger.warning(f"الملف غير موجود: {file_path}")
    
    @staticmethod
    def get_sheet_names(file_path: Union[str, Path]) -> List[str]:
        """
        الحصول على أسماء الأوراق في ملف Excel
        
        Args:
            file_path: مسار ملف Excel
        
        Returns:
            قائمة بأسماء الأوراق
        """
        try:
            xl_file = pd.ExcelFile(file_path)
            return xl_file.sheet_names
        except Exception as e:
            logger.error(f"خطأ في قراءة أسماء الأوراق: {e}")
            return []
