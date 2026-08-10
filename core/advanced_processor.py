"""
معالج البيانات المتقدم - Smart Data Cleaner
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json

from utils.logger import logger
from utils.helpers import StringHelpers, NumberHelpers
from core.data_cleaner import DataCleaner


class AdvancedDataProcessor:
    """
    معالج البيانات المتقدم
    
    يوفر عمليات معالجة متقدمة مثل:
    - معالجة التواريخ
    - تطبيع البيانات
    - التقسيم الذكي
    - الدمج والفصل
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        تهيئة معالج البيانات
        
        Args:
            df: DataFrame المراد معالجته
        """
        self.df = df.copy()
        self.logger = logger
    
    def detect_date_columns(self) -> List[str]:
        """
        كشف أعمدة التواريخ تلقائياً
        
        Returns:
            قائمة بأسماء أعمدة التواريخ
        """
        date_columns = []
        
        for col in self.df.select_dtypes(include='object').columns:
            # محاولة تحويل العمود إلى تاريخ
            try:
                pd.to_datetime(self.df[col], errors='coerce')
                # إذا نجحت التحويل، فهذا عمود تاريخ
                date_columns.append(col)
                self.logger.info(f"تم كشف عمود التاريخ: {col}")
            except:
                pass
        
        return date_columns
    
    def normalize_dates(
        self, 
        column: str, 
        date_format: str = 'auto'
    ) -> None:
        """
        تطبيع تنسيق التواريخ
        
        Args:
            column: اسم العمود
            date_format: التنسيق المطلوب (auto للكشف التلقائي)
        """
        try:
            self.df[column] = pd.to_datetime(
                self.df[column], 
                errors='coerce',
                format=None if date_format == 'auto' else date_format
            )
            self.logger.info(f"تم تطبيع تاريخ العمود: {column}")
        except Exception as e:
            self.logger.error(f"خطأ في تطبيع التاريخ: {e}")
    
    def split_column(
        self, 
        column: str, 
        delimiter: str = ' ',
        new_columns: Optional[List[str]] = None
    ) -> None:
        """
        فصل عمود واحد إلى عدة أعمدة
        
        Args:
            column: اسم العمود المراد فصله
            delimiter: الفاصل
            new_columns: أسماء الأعمدة الجديدة
        """
        try:
            split_data = self.df[column].str.split(
                delimiter, 
                expand=True
            )
            
            if new_columns:
                split_data.columns = new_columns[:split_data.shape[1]]
            
            self.df = pd.concat([self.df, split_data], axis=1)
            self.logger.info(f"تم فصل العمود: {column}")
        except Exception as e:
            self.logger.error(f"خطأ في فصل العمود: {e}")
    
    def merge_columns(
        self, 
        columns: List[str], 
        new_column: str,
        delimiter: str = ' '
    ) -> None:
        """
        دمج عدة أعمدة في عمود واحد
        
        Args:
            columns: أسماء الأعمدة المراد دمجها
            new_column: اسم العمود الجديد
            delimiter: الفاصل
        """
        try:
            self.df[new_column] = self.df[columns].astype(str).agg(
                delimiter.join, 
                axis=1
            )
            self.logger.info(f"تم دمج الأعمدة في: {new_column}")
        except Exception as e:
            self.logger.error(f"خطأ في دمج الأعمدة: {e}")
    
    def detect_data_types(self) -> Dict[str, str]:
        """
        كشف أنواع البيانات بذكاء
        
        Returns:
            قاموس بأنواع البيانات المكتشفة
        """
        data_types = {}
        
        for col in self.df.columns:
            col_data = self.df[col]
            
            # إزالة القيم الفارغة
            non_null = col_data.dropna()
            
            if len(non_null) == 0:
                data_types[col] = 'empty'
            elif col_data.dtype == 'object':
                # التحقق من نوع البيانات النصية
                sample = non_null.iloc[0]
                
                # التحقق من البريد الإلكتروني
                if StringHelpers.is_valid_email(str(sample)):
                    data_types[col] = 'email'
                
                # التحقق من الأرقام
                elif NumberHelpers.is_number(str(sample)):
                    data_types[col] = 'numeric_string'
                
                # التحقق من التواريخ
                else:
                    try:
                        pd.to_datetime(non_null)
                        data_types[col] = 'date'
                    except:
                        data_types[col] = 'text'
            
            elif col_data.dtype in ['int64', 'int32']:
                data_types[col] = 'integer'
            
            elif col_data.dtype in ['float64', 'float32']:
                data_types[col] = 'float'
            
            elif col_data.dtype == 'bool':
                data_types[col] = 'boolean'
            
            else:
                data_types[col] = str(col_data.dtype)
        
        return data_types
    
    def normalize_numbers(
        self, 
        column: str,
        remove_currency: bool = True,
        remove_commas: bool = True
    ) -> None:
        """
        تطبيع الأرقام
        
        Args:
            column: اسم العمود
            remove_currency: إزالة رموز العملات
            remove_commas: إزالة الفواصل
        """
        try:
            col = self.df[column].astype(str)
            
            if remove_currency:
                col = col.apply(NumberHelpers.remove_currency_symbols)
            
            if remove_commas:
                col = col.apply(NumberHelpers.remove_commas)
            
            # تحويل إلى رقم
            self.df[column] = pd.to_numeric(col, errors='coerce')
            self.logger.info(f"تم تطبيع الأرقام في العمود: {column}")
        except Exception as e:
            self.logger.error(f"خطأ في تطبيع الأرقام: {e}")
    
    def categorize_column(
        self, 
        column: str,
        categories: Optional[Dict[str, List[str]]] = None
    ) -> None:
        """
        تصنيف بيانات عمود
        
        Args:
            column: اسم العمود
            categories: قاموس بالتصنيفات
        """
        if categories is None:
            categories = {}
        
        def categorize(value):
            if pd.isna(value):
                return None
            
            value_str = str(value).lower()
            for category, values in categories.items():
                if value_str in [v.lower() for v in values]:
                    return category
            return 'أخرى'
        
        self.df[f'{column}_category'] = self.df[column].apply(categorize)
        self.logger.info(f"تم تصنيف العمود: {column}")
    
    def handle_categorical_data(self, column: str, max_categories: int = 10) -> None:
        """
        التعامل مع البيانات الفئوية
        
        Args:
            column: اسم العمود
            max_categories: الحد الأقصى للفئات
        """
        try:
            value_counts = self.df[column].value_counts()
            
            if len(value_counts) > max_categories:
                # دمج الفئات النادرة
                top_categories = value_counts.head(max_categories).index
                self.df[column] = self.df[column].apply(
                    lambda x: x if x in top_categories else 'أخرى'
                )
                self.logger.info(
                    f"تم دمج الفئات النادرة في العمود: {column}"
                )
        except Exception as e:
            self.logger.error(f"خطأ في معالجة البيانات الفئوية: {e}")
    
    def calculate_statistics(self, numeric_only: bool = True) -> Dict[str, Dict]:
        """
        حساب الإحصائيات الأساسية
        
        Args:
            numeric_only: حساب الإحصائيات للأعمدة الرقمية فقط
        
        Returns:
            قاموس بالإحصائيات
        """
        stats = {}
        
        if numeric_only:
            df_calc = self.df.select_dtypes(include=[np.number])
        else:
            df_calc = self.df
        
        for col in df_calc.columns:
            if pd.api.types.is_numeric_dtype(df_calc[col]):
                stats[col] = {
                    'mean': df_calc[col].mean(),
                    'median': df_calc[col].median(),
                    'std': df_calc[col].std(),
                    'min': df_calc[col].min(),
                    'max': df_calc[col].max(),
                    'q1': df_calc[col].quantile(0.25),
                    'q3': df_calc[col].quantile(0.75),
                }
        
        return stats
    
    def generate_data_profile(self) -> Dict[str, Any]:
        """
        توليد تقرير شامل عن البيانات
        
        Returns:
            قاموس يحتوي على ملف تعريف البيانات
        """
        profile = {
            'shape': self.df.shape,
            'columns': list(self.df.columns),
            'data_types': self.detect_data_types(),
            'missing_values': self.df.isnull().sum().to_dict(),
            'duplicates': self.df.duplicated().sum(),
            'memory_usage_mb': self.df.memory_usage(deep=True).sum() / 1024 ** 2,
            'statistics': self.calculate_statistics(),
            'column_info': {}
        }
        
        # إضافة معلومات مفصلة عن كل عمود
        for col in self.df.columns:
            profile['column_info'][col] = {
                'type': str(self.df[col].dtype),
                'non_null_count': self.df[col].notna().sum(),
                'null_count': self.df[col].isna().sum(),
                'unique_values': self.df[col].nunique(),
            }
        
        return profile
    
    def get_processed_data(self) -> pd.DataFrame:
        """الحصول على البيانات المعالجة"""
        return self.df.copy()
