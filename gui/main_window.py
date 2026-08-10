"""
واجهة المستخدم الرسومية - Smart Data Cleaner
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from typing import Optional
import pandas as pd
from datetime import datetime
import threading

from utils.logger import logger
from utils.file_manager import FileManager
from utils.config_manager import config_manager
from core.data_cleaner import DataCleaner
from core.advanced_processor import AdvancedDataProcessor


class DataCleanerGUI:
    """
    واجهة المستخدم الرسومية الرئيسية
    """
    
    def __init__(self, root: tk.Tk):
        """تهيئة الواجهة"""
        self.root = root
        self.root.title("Smart Data Cleaner - منظف البيانات الذكي")
        self.root.geometry("1200x800")
        
        # متغيرات الحالة
        self.current_file: Optional[Path] = None
        self.original_df: Optional[pd.DataFrame] = None
        self.cleaned_df: Optional[pd.DataFrame] = None
        self.is_processing = False
        
        # تهيئة الواجهة
        self._setup_ui()
        self._apply_theme()
        
        logger.info("تم تهيئة واجهة المستخدم")
    
    def _setup_ui(self) -> None:
        """إعداد عناصر الواجهة"""
        # شريط القوائم
        self._create_menu_bar()
        
        # الإطار العلوي (التحكم)
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            control_frame,
            text="📁 فتح ملف",
            command=self.open_file
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="🧹 تنظيف البيانات",
            command=self.clean_data
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="💾 حفظ الملف",
            command=self.save_file
        ).pack(side=tk.LEFT, padx=5)
        
        # شريط التقدم
        self.progress = ttk.Progressbar(
            control_frame,
            mode='indeterminate'
        )
        self.progress.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # الإطار الرئيسي (الأعمدة)
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # الشريط الجانبي (الخيارات)
        self._create_sidebar(main_frame)
        
        # منطقة المعاينة
        self._create_preview_area(main_frame)
        
        # شريط الحالة
        self.status_var = tk.StringVar(value="جاهز")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _create_menu_bar(self) -> None:
        """إنشاء شريط القوائم"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # قائمة ملف
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ملف", menu=file_menu)
        file_menu.add_command(label="فتح", command=self.open_file)
        file_menu.add_command(label="حفظ", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="خروج", command=self.root.quit)
        
        # قائمة تحرير
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="تحرير", menu=edit_menu)
        edit_menu.add_command(label="إعادة تعيين", command=self.reset_data)
        edit_menu.add_command(label="الإعدادات", command=self.open_settings)
        
        # قائمة تنظيف
        clean_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="تنظيف", menu=clean_menu)
        clean_menu.add_command(label="تنظيف كامل", command=self.clean_data)
        clean_menu.add_command(label="إزالة التكرارات", command=self.remove_duplicates)
        clean_menu.add_command(label="معالجة القيم الفارغة", command=self.handle_missing)
        
        # قائمة مساعدة
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="مساعدة", menu=help_menu)
        help_menu.add_command(label="حول البرنامج", command=self.show_about)
    
    def _create_sidebar(self, parent: ttk.Frame) -> None:
        """إنشاء الشريط الجانبي"""
        sidebar = ttk.LabelFrame(parent, text="الخيارات", width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # خيارات التنظيف
        ttk.Label(sidebar, text="خيارات التنظيف:", font=("Arial", 10, "bold")).pack(pady=10)
        
        self.remove_duplicates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            sidebar,
            text="إزالة التكرارات",
            variable=self.remove_duplicates_var
        ).pack(anchor=tk.W, padx=10)
        
        self.remove_null_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            sidebar,
            text="معالجة القيم الفارغة",
            variable=self.remove_null_var
        ).pack(anchor=tk.W, padx=10)
        
        self.normalize_whitespace_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            sidebar,
            text="تطبيع المسافات",
            variable=self.normalize_whitespace_var
        ).pack(anchor=tk.W, padx=10)
        
        self.remove_special_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            sidebar,
            text="إزالة أحرف خاصة",
            variable=self.remove_special_var
        ).pack(anchor=tk.W, padx=10)
        
        self.remove_invisible_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            sidebar,
            text="إزالة أحرف غير مرئية",
            variable=self.remove_invisible_var
        ).pack(anchor=tk.W, padx=10)
        
        # خيارات متقدمة
        ttk.Label(sidebar, text="خيارات متقدمة:", font=("Arial", 10, "bold")).pack(pady=10)
        
        self.handle_outliers_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            sidebar,
            text="التعامل مع القيم الشاذة",
            variable=self.handle_outliers_var
        ).pack(anchor=tk.W, padx=10)
        
        ttk.Label(sidebar, text="تطبيع الحالة:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.case_var = tk.StringVar(value="none")
        case_combo = ttk.Combobox(
            sidebar,
            textvariable=self.case_var,
            values=["none", "lower", "upper", "title"],
            state="readonly",
            width=20
        )
        case_combo.pack(padx=10, pady=5)
    
    def _create_preview_area(self, parent: ttk.Frame) -> None:
        """إنشاء منطقة المعاينة"""
        preview_frame = ttk.LabelFrame(parent, text="معاينة البيانات")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # شريط اللسان
        notebook = ttk.Notebook(preview_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # لسان المعاينة
        self.preview_frame = ttk.Frame(notebook)
        notebook.add(self.preview_frame, text="المعاينة")
        
        self.preview_text = tk.Text(
            self.preview_frame,
            height=20,
            width=60,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # شريط التمرير
        scrollbar = ttk.Scrollbar(self.preview_frame, command=self.preview_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text.config(yscrollcommand=scrollbar.set)
        
        # لسان التقرير
        self.report_frame = ttk.Frame(notebook)
        notebook.add(self.report_frame, text="التقرير")
        
        self.report_text = tk.Text(
            self.report_frame,
            height=20,
            width=60,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def open_file(self) -> None:
        """فتح ملف"""
        file_types = [
            ("ملفات CSV", "*.csv"),
            ("ملفات Excel", "*.xlsx *.xls"),
            ("ملفات JSON", "*.json"),
            ("جميع الملفات", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="اختر ملف البيانات",
            filetypes=file_types
        )
        
        if not file_path:
            return
        
        try:
            self.current_file = Path(file_path)
            self.original_df = FileManager.load_file(self.current_file)
            self.cleaned_df = None
            
            self.status_var.set(
                f"تم تحميل الملف: {self.current_file.name} "
                f"({self.original_df.shape[0]} صف، {self.original_df.shape[1]} عمود)"
            )
            
            self._update_preview(self.original_df)
            logger.info(f"تم تحميل الملف: {file_path}")
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في تحميل الملف: {e}")
            logger.error(f"خطأ في تحميل الملف: {e}")
    
    def clean_data(self) -> None:
        """تنظيف البيانات"""
        if self.original_df is None:
            messagebox.showwarning("تحذير", "يرجى تحميل ملف أولاً")
            return
        
        # تشغيل التنظيف في خيط منفصل
        thread = threading.Thread(target=self._perform_cleaning)
        thread.start()
    
    def _perform_cleaning(self) -> None:
        """تنفيذ عملية التنظيف"""
        try:
            self.is_processing = True
            self.progress.start()
            self.status_var.set("جاري تنظيف البيانات...")
            
            # إنشاء كائن التنظيف
            cleaner = DataCleaner(self.original_df)
            
            # إعداد الخيارات
            config = {
                'remove_duplicates': self.remove_duplicates_var.get(),
                'remove_null_values': self.remove_null_var.get(),
                'normalize_whitespace': self.normalize_whitespace_var.get(),
                'remove_special_characters': self.remove_special_var.get(),
                'normalize_case': self.case_var.get(),
                'remove_invisible_characters': self.remove_invisible_var.get(),
                'handle_outliers': self.handle_outliers_var.get(),
            }
            
            # تنفيذ التنظيف
            self.cleaned_df = cleaner.clean(config)
            
            # عرض النتائج
            self._update_preview(self.cleaned_df)
            self._display_report(cleaner.get_cleaning_report())
            
            self.status_var.set(f"تم التنظيف بنجاح!")
            messagebox.showinfo("نجح", "تم تنظيف البيانات بنجاح!")
            
            logger.info("تم التنظيف بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في التنظيف: {e}")
            logger.error(f"خطأ في التنظيف: {e}")
        finally:
            self.is_processing = False
            self.progress.stop()
    
    def save_file(self) -> None:
        """حفظ الملف"""
        if self.cleaned_df is None:
            messagebox.showwarning("تحذير", "لا توجد بيانات لحفظها")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("Excel Files", "*.xlsx"),
                ("JSON Files", "*.json")
            ]
        )
        
        if not file_path:
            return
        
        try:
            FileManager.save_file(self.cleaned_df, file_path)
            messagebox.showinfo("نجح", f"تم حفظ الملف: {file_path}")
            self.status_var.set(f"تم حفظ الملف: {Path(file_path).name}")
            logger.info(f"تم حفظ الملف: {file_path}")
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في حفظ الملف: {e}")
            logger.error(f"خطأ في حفظ الملف: {e}")
    
    def reset_data(self) -> None:
        """إعادة تعيين البيانات"""
        if self.original_df is None:
            messagebox.showwarning("تحذير", "لا توجد بيانات لإعادة تعيينها")
            return
        
        self.cleaned_df = None
        self._update_preview(self.original_df)
        self.status_var.set("تم إعادة تعيين البيانات")
    
    def remove_duplicates(self) -> None:
        """إزالة التكرارات"""
        if self.original_df is None:
            messagebox.showwarning("تحذير", "يرجى تحميل ملف أولاً")
            return
        
        cleaner = DataCleaner(self.original_df)
        cleaner.remove_duplicates()
        self.cleaned_df = cleaner.df
        self._update_preview(self.cleaned_df)
        self.status_var.set("تم إزالة التكرارات")
    
    def handle_missing(self) -> None:
        """معالجة القيم الفارغة"""
        if self.original_df is None:
            messagebox.showwarning("تحذير", "يرجى تحميل ملف أولاً")
            return
        
        cleaner = DataCleaner(self.original_df)
        cleaner.handle_missing_values()
        self.cleaned_df = cleaner.df
        self._update_preview(self.cleaned_df)
        self.status_var.set("تم معالجة القيم الفارغة")
    
    def open_settings(self) -> None:
        """فتح نافذة الإعدادات"""
        messagebox.showinfo("الإعدادات", "قريباً سيتم إضافة نافذة الإعدادات")
    
    def show_about(self) -> None:
        """عرض معلومات البرنامج"""
        about_text = """
Smart Data Cleaner v1.0
منظف البيانات الذكي

تطبيق قوي لتنظيف وتحضير البيانات

الميزات:
- إزالة التكرارات
- معالجة القيم الفارغة
- تطبيع النصوص
- التعامل مع القيم الشاذة
- دعم ملفات CSV و Excel و JSON

تطوير: GMGM071
        """
        messagebox.showinfo("حول البرنامج", about_text)
    
    def _update_preview(self, df: pd.DataFrame) -> None:
        """تحديث معاينة البيانات"""
        self.preview_text.delete(1.0, tk.END)
        
        preview_rows = config_manager.get('ui.preview_rows', 100)
        preview_text = df.head(preview_rows).to_string()
        
        self.preview_text.insert(tk.END, preview_text)
    
    def _display_report(self, report: dict) -> None:
        """عرض تقرير التنظيف"""
        self.report_text.delete(1.0, tk.END)
        
        report_text = f"""
تقرير التنظيف
{'='*50}

الشكل الأصلي: {report['original_shape']}
الشكل بعد التنظيف: {report['cleaned_shape']}

التغييرات:
- التكرارات المحذوفة: {report['changes'].get('duplicates_removed', 0)}
- القيم الفارغة المعالجة: {report['changes'].get('null_values_handled', 0)}
- الأحرف الخاصة المحذوفة: {report['changes'].get('special_chars_removed', 0)}
- المسافات المطبعة: {report['changes'].get('whitespace_normalized', 0)}
- القيم الشاذة المعالجة: {report['changes'].get('outliers_handled', 0)}

نسبة فقدان البيانات: {report['data_loss_percentage']:.2f}%
        """
        
        self.report_text.insert(tk.END, report_text)
    
    def _apply_theme(self) -> None:
        """تطبيق المظهر"""
        theme = config_manager.get('ui.theme', 'dark')
        # يمكن إضافة تطبيق المظهر هنا


def main():
    """الدالة الرئيسية"""
    root = tk.Tk()
    app = DataCleanerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
