"""
دوال مساعدة - Smart Data Cleaner
"""

import re
from typing import Any, List, Dict, Optional
from pathlib import Path
import unicodedata

from constants import EMAIL_PATTERN, CURRENCY_SYMBOLS


class StringHelpers:
    """مساعدات معالجة النصوص"""
    
    @staticmethod
    def remove_invisible_characters(text: str) -> str:
        """
        إزالة الأحرف غير المرئية
        
        Args:
            text: النص المدخل
        
        Returns:
            النص بدون أحرف غير مرئية
        """
        if not isinstance(text, str):
            return text
        
        # إزالة أحرف التحكم
        text = ''.join(
            char for char in text 
            if unicodedata.category(char) != 'Cc'
        )
        
        # إزالة علامات الحذف
        text = text.replace('\x00', '')
        text = text.replace('\ufeff', '')  # BOM
        
        return text
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        تطبيع المسافات البيضاء
        
        Args:
            text: النص المدخل
        
        Returns:
            النص مع مسافات بيضاء منتظمة
        """
        if not isinstance(text, str):
            return text
        
        # استبدال المسافات المتعددة بمسافة واحدة
        text = re.sub(r'\s+', ' ', text)
        
        # إزالة المسافات من البداية والنهاية
        text = text.strip()
        
        return text
    
    @staticmethod
    def normalize_case(text: str, case: str = "lower") -> str:
        """
        تطبيع حالة النص
        
        Args:
            text: النص المدخل
            case: نوع التطبيع (lower, upper, title, capitalize)
        
        Returns:
            النص مع الحالة المطبعة
        """
        if not isinstance(text, str):
            return text
        
        if case == "lower":
            return text.lower()
        elif case == "upper":
            return text.upper()
        elif case == "title":
            return text.title()
        elif case == "capitalize":
            return text.capitalize()
        else:
            return text
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """التحقق من صحة البريد الإلكتروني"""
        if not isinstance(email, str):
            return False
        return bool(re.match(EMAIL_PATTERN, email))
    
    @staticmethod
    def remove_special_characters(
        text: str, 
        keep_chars: str = ""
    ) -> str:
        """
        إزالة الأحرف الخاصة
        
        Args:
            text: النص المدخل
            keep_chars: أحرف يتم الاحتفاظ بها
        
        Returns:
            النص بدون أحرف خاصة
        """
        if not isinstance(text, str):
            return text
        
        # نمط الأحرف المسموح
        pattern = f"[a-zA-Z0-9\\s{re.escape(keep_chars)}]"
        return re.sub(f"[^{pattern}]", "", text)


class NumberHelpers:
    """مساعدات معالجة الأرقام"""
    
    @staticmethod
    def remove_currency_symbols(text: str) -> str:
        """
        إزالة رموز العملات
        
        Args:
            text: النص المدخل
        
        Returns:
            النص بدون رموز عملات
        """
        if not isinstance(text, str):
            return text
        
        for symbol in CURRENCY_SYMBOLS.keys():
            text = text.replace(symbol, "")
        
        return text.strip()
    
    @staticmethod
    def remove_commas(text: str) -> str:
        """إزالة الفواصل من الأرقام"""
        if not isinstance(text, str):
            return text
        return text.replace(",", "")
    
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """استخراج الأرقام من النص"""
        if not isinstance(text, str):
            return []
        
        numbers = re.findall(r"[-+]?\d*\.?\d+", text)
        return [float(num) for num in numbers]
    
    @staticmethod
    def is_number(text: str) -> bool:
        """التحقق من أن النص رقم"""
        if not isinstance(text, str):
            return False
        
        try:
            float(text)
            return True
        except ValueError:
            return False


class FileHelpers:
    """مساعدات معالجة الملفات"""
    
    @staticmethod
    def get_file_size_mb(file_path: Path) -> float:
        """الحصول على حجم الملف بالميجابايت"""
        return file_path.stat().st_size / (1024 * 1024)
    
    @staticmethod
    def generate_output_filename(
        original_filename: str,
        suffix: str = "_cleaned"
    ) -> str:
        """
        توليد اسم ملف الإخراج
        
        Args:
            original_filename: اسم الملف الأصلي
            suffix: اللاحقة المضافة
        
        Returns:
            اسم ملف جديد
        """
        path = Path(original_filename)
        stem = path.stem
        suffix_text = suffix
        ext = path.suffix
        
        return f"{stem}{suffix_text}{ext}"
    
    @staticmethod
    def safe_path(file_path: str) -> Path:
        """
        التحقق من أمان المسار (منع path traversal)
        
        Args:
            file_path: مسار الملف
        
        Returns:
            Path آمن
        
        Raises:
            ValueError: إذا كان المسار غير آمن
        """
        path = Path(file_path).resolve()
        
        # منع الوصول خارج مجلد البرنامج
        if not str(path).startswith(str(Path.cwd())):
            raise ValueError("المسار غير آمن")
        
        return path


class ValidationHelpers:
    """مساعدات التحقق"""
    
    @staticmethod
    def is_empty(value: Any) -> bool:
        """التحقق من أن القيمة فارغة"""
        if value is None:
            return True
        
        if isinstance(value, str):
            return len(value.strip()) == 0
        
        if isinstance(value, (list, dict, tuple)):
            return len(value) == 0
        
        return False
    
    @staticmethod
    def normalize_value(value: Any) -> Any:
        """تطبيع القيمة"""
        if isinstance(value, str):
            return StringHelpers.normalize_whitespace(value)
        return value
