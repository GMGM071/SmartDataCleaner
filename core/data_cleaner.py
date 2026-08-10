"""
محرك التنظيف الرئيسي - Smart Data Cleaner
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from utils.logger import logger
from utils.helpers import (
    StringHelpers, 
    NumberHelpers, 
    ValidationHelpers
)
from utils.config_manager import config_manager


class CleaningStrategy(Enum):
    """استراتيجيات التنظيف المختلفة"""
    REMOVE = "remove"
    REPLACE = "replace"
    INTERPOLATE = "interpolate"


@dataclass
class CleaningReport:
    """تقرير عملية التنظيف"""
    total_rows: int
    total_columns: int
    duplicates_removed: int
    null_values_handled: int
    special_chars_removed: int
    whitespace_normalized: int
    outliers_handled: int
    processing_time: float
    issues: List[str]


class DataCleaner:
    """
    محرك التنظيف الرئيسي
    
    يقوم بتنفيذ جميع عمليات التنظيف على البيانات
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        تهيئة محرك التنظيف
        
        Args:
            df: DataFrame المراد تنظيفه
        """
        self.original_df = df.copy()
        self.df = df.copy()
        self.report = {
            'duplicates_removed': 0,
            'null_values_handled': 0,
            'special_chars_removed': 0,
            'whitespace_normalized': 0,
            'outliers_handled': 0,
            'issues': []
        }
    
    def clean(self, config: Optional[Dict] = None) -> pd.DataFrame:
        """
        تنفيذ عملية التنظيف الكاملة
        
        Args:
            config: إعدادات التنظيف المخصصة
        
        Returns:
            DataFrame المنظف
        """
        if config is None:
            config = {
                'remove_duplicates': config_manager.get('cleaning.remove_duplicates', True),
                'remove_null_values': config_manager.get('cleaning.remove_null_values', True),
                'normalize_whitespace': config_manager.get('cleaning.normalize_whitespace', True),
                'remove_special_characters': config_manager.get('cleaning.remove_special_characters', False),
                'normalize_case': config_manager.get('cleaning.normalize_case', 'none'),
                'remove_invisible_characters': config_manager.get('cleaning.remove_invisible_characters', True),
                'handle_outliers': config_manager.get('cleaning.handle_outliers', False),
                'outlier_method': config_manager.get('cleaning.outlier_method', 'iqr'),
            }
        
        logger.info("جاري بدء عملية التنظيف...")
        
        # تنفيذ عمليات التنظيف بالترتيب
        if config.get('remove_invisible_characters', True):
            self.remove_invisible_characters()
        
        if config.get('normalize_whitespace', True):
            self.normalize_whitespace()
        
        if config.get('remove_special_characters', False):
            self.remove_special_characters()
        
        if config.get('normalize_case', 'none') != 'none':
            self.normalize_case(config['normalize_case'])
        
        if config.get('remove_duplicates', True):
            self.remove_duplicates()
        
        if config.get('remove_null_values', True):
            self.handle_missing_values()
        
        if config.get('handle_outliers', False):
            self.handle_outliers(config.get('outlier_method', 'iqr'))
        
        logger.info("تم إنهاء عملية التنظيف بنجاح")
        return self.df
    
    def remove_duplicates(self) -> None:
        """إزالة الصفوف المكررة"""
        initial_rows = len(self.df)
        self.df = self.df.drop_duplicates()
        removed = initial_rows - len(self.df)
        self.report['duplicates_removed'] = removed
        logger.info(f"تم إزالة {removed} صفوف مكررة")
    
    def handle_missing_values(
        self, 
        strategy: CleaningStrategy = CleaningStrategy.REMOVE
    ) -> None:
        """
        التعامل مع القيم المفقودة
        
        Args:
            strategy: استراتيجية التعامل
        """
        initial_nulls = self.df.isnull().sum().sum()
        
        if strategy == CleaningStrategy.REMOVE:
            self.df = self.df.dropna()
        elif strategy == CleaningStrategy.REPLACE:
            # استبدال بالقيمة الافتراضية
            for col in self.df.columns:
                if self.df[col].dtype == 'object':
                    self.df[col].fillna('غير متوفر', inplace=True)
                else:
                    self.df[col].fillna(self.df[col].mean(), inplace=True)
        elif strategy == CleaningStrategy.INTERPOLATE:
            # استيفاء القيم
            self.df = self.df.interpolate()
        
        self.report['null_values_handled'] = initial_nulls
        logger.info(f"تم التعامل مع {initial_nulls} قيمة مفقودة")
    
    def remove_invisible_characters(self) -> None:
        """إزالة الأحرف غير المرئية"""
        count = 0
        
        for col in self.df.select_dtypes(include='object').columns:
            self.df[col] = self.df[col].apply(
                lambda x: StringHelpers.remove_invisible_characters(str(x)) 
                if pd.notna(x) else x
            )
            # عد الأحرف التي تم إزالتها
            count += len(str(self.df[col])) - len(
                self.df[col].apply(
                    lambda x: StringHelpers.remove_invisible_characters(str(x))
                    if pd.notna(x) else x
                )
            )
        
        self.report['invisible_chars_removed'] = count
        logger.info(f"تم إزالة {count} حرف غير مرئي")
    
    def normalize_whitespace(self) -> None:
        """تطبيع المسافات البيضاء"""
        count = 0
        
        for col in self.df.select_dtypes(include='object').columns:
            self.df[col] = self.df[col].apply(
                lambda x: StringHelpers.normalize_whitespace(str(x))
                if pd.notna(x) else x
            )
            count += 1
        
        self.report['whitespace_normalized'] = count
        logger.info(f"تم تطبيع المسافات البيضاء في {count} عمود")
    
    def remove_special_characters(self, keep_chars: str = "") -> None:
        """إزالة الأحرف الخاصة"""
        count = 0
        
        for col in self.df.select_dtypes(include='object').columns:
            self.df[col] = self.df[col].apply(
                lambda x: StringHelpers.remove_special_characters(str(x), keep_chars)
                if pd.notna(x) else x
            )
            count += 1
        
        self.report['special_chars_removed'] = count
        logger.info(f"تم إزالة الأحرف الخاصة من {count} عمود")
    
    def normalize_case(self, case: str = "lower") -> None:
        """
        تطبيع حالة النصوص
        
        Args:
            case: نوع التطبيع (lower, upper, title, capitalize)
        """
        count = 0
        
        for col in self.df.select_dtypes(include='object').columns:
            self.df[col] = self.df[col].apply(
                lambda x: StringHelpers.normalize_case(str(x), case)
                if pd.notna(x) else x
            )
            count += 1
        
        logger.info(f"تم تطبيع الحالة إلى {case} في {count} عمود")
    
    def handle_outliers(
        self, 
        method: str = "iqr",
        threshold: float = 1.5
    ) -> None:
        """
        التعامل مع القيم الشاذة
        
        Args:
            method: الطريقة (iqr أو zscore)
            threshold: عتبة الانحراف
        """
        count = 0
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if method == "iqr":
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outliers = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
                count += outliers.sum()
                self.df = self.df[~outliers]
            
            elif method == "zscore":
                z_scores = np.abs((self.df[col] - self.df[col].mean()) / self.df[col].std())
                outliers = z_scores > threshold
                count += outliers.sum()
                self.df = self.df[~outliers]
        
        self.report['outliers_handled'] = count
        logger.info(f"تم التعامل مع {count} قيمة شاذة باستخدام طريقة {method}")
    
    def get_cleaning_report(self) -> Dict[str, Any]:
        """الحصول على تقرير عملية التنظيف"""
        return {
            'original_shape': self.original_df.shape,
            'cleaned_shape': self.df.shape,
            'changes': self.report,
            'data_loss_percentage': (
                (self.original_df.shape[0] - self.df.shape[0]) / 
                self.original_df.shape[0] * 100
            )
        }
    
    def validate_data_quality(self) -> Dict[str, float]:
        """
        التحقق من جودة البيانات
        
        Returns:
            قاموس يحتوي على مقاييس الجودة
        """
        total_cells = self.df.shape[0] * self.df.shape[1]
        null_cells = self.df.isnull().sum().sum()
        duplicate_rows = self.df.duplicated().sum()
        
        return {
            'completeness': ((total_cells - null_cells) / total_cells) * 100,
            'uniqueness': ((self.df.shape[0] - duplicate_rows) / self.df.shape[0]) * 100,
            'null_percentage': (null_cells / total_cells) * 100,
            'duplicate_percentage': (duplicate_rows / self.df.shape[0]) * 100,
        }
