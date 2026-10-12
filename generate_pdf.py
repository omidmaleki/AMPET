from fpdf import FPDF
import os
import arabic_reshaper
from bidi.algorithm import get_display

# Font paths
FONT_DIR = r"C:\Windows\Fonts"
FONT_REGULAR = os.path.join(FONT_DIR, "Vazirmatn-Regular.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "Vazirmatn-Bold.ttf")

# Colors
NAVY = (27, 42, 74)
CREAM = (245, 240, 232)
GOLD = (201, 169, 110)
BLACK = (44, 44, 44)
LIGHT_GRAY = (232, 232, 232)
WHITE = (255, 255, 255)

def fa(text):
    """Reshape and reorder Persian/Arabic text for correct PDF rendering."""
    # Replace Persian question mark with English one (font support)
    text = text.replace("؟", "?")
    # Split by newlines, reshape each line separately, then rejoin
    lines = text.split("\n")
    reshaped_lines = [get_display(arabic_reshaper.reshape(line)) for line in lines]
    return "\n".join(reshaped_lines)

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.add_font("Vazirmatn", "", FONT_REGULAR)
        self.add_font("Vazirmatn", "B", FONT_BOLD)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 15, "F")
        self.set_text_color(*WHITE)
        self.set_font("Vazirmatn", "B", 8)
        self.set_xy(10, 5)
        self.cell(0, 5, fa("سناتور | سرویس خواب لوکس"), align="C")
        self.set_text_color(*BLACK)
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_fill_color(*CREAM)
        self.rect(0, self.get_y(), 210, 15, "F")
        self.set_text_color(*NAVY)
        self.set_font("Vazirmatn", "", 7)
        self.set_x(10)
        self.cell(0, 5, fa(f"صفحه {self.page_no()}"), align="C")
        self.set_text_color(*BLACK)

    def chapter_title(self, title):
        self.set_fill_color(*NAVY)
        self.rect(10, self.get_y(), 190, 12, "F")
        self.set_text_color(*WHITE)
        self.set_font("Vazirmatn", "B", 12)
        self.set_xy(15, self.get_y() + 2)
        self.cell(0, 8, fa(title), align="R")
        self.set_text_color(*BLACK)
        self.ln(16)

    def sub_title(self, title):
        self.set_fill_color(*GOLD)
        self.rect(10, self.get_y(), 190, 8, "F")
        self.set_text_color(*WHITE)
        self.set_font("Vazirmatn", "B", 10)
        self.set_xy(15, self.get_y() + 1)
        self.cell(0, 6, fa(title), align="R")
        self.set_text_color(*BLACK)
        self.ln(12)

    def body_text(self, text):
        self.set_font("Vazirmatn", "", 9)
        self.set_text_color(*BLACK)
        self.multi_cell(0, 6, fa(text), align="R")
        self.ln(2)

    def bullet_point(self, text):
        self.set_font("Vazirmatn", "", 9)
        self.set_text_color(*BLACK)
        self.set_x(15)
        self.cell(5, 6, "-", align="R")
        self.multi_cell(0, 6, fa(text), align="R")
        self.ln(1)

    def add_table(self, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)
        self.set_fill_color(*NAVY)
        self.set_text_color(*WHITE)
        self.set_font("Vazirmatn", "B", 8)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, fa(header), align="C", border=1, fill=True)
        self.ln()
        self.set_text_color(*BLACK)
        self.set_font("Vazirmatn", "", 8)
        fill = False
        for row in rows:
            if fill:
                self.set_fill_color(*CREAM)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 7, fa(str(cell)), align="C", border=1, fill=fill)
            self.ln()
            fill = not fill
        self.ln(4)

    def add_color_box(self, rgb, text, x, y, w, h):
        self.set_fill_color(*rgb)
        self.rect(x, y, w, h, "F")
        self.set_text_color(*WHITE)
        self.set_font("Vazirmatn", "B", 7)
        self.set_xy(x, y + 1)
        self.cell(w, h, fa(text), align="C")
        self.set_text_color(*BLACK)

    def add_info_box(self, title, content):
        self.set_fill_color(*CREAM)
        self.rect(10, self.get_y(), 190, 20, "F")
        self.set_text_color(*NAVY)
        self.set_font("Vazirmatn", "B", 9)
        self.set_xy(15, self.get_y() + 2)
        self.cell(0, 5, fa(title), align="R")
        self.set_text_color(*BLACK)
        self.set_font("Vazirmatn", "", 8)
        self.set_xy(15, self.get_y() + 8)
        self.multi_cell(180, 5, fa(content), align="R")
        self.ln(24)


def create_pdf():
    pdf = PDF()
    pdf.add_page()

    # === COVER PAGE ===
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 297, "F")
    pdf.set_text_color(*GOLD)
    pdf.set_font("Vazirmatn", "B", 30)
    pdf.set_y(60)
    pdf.cell(0, 15, fa("سناتور"), align="C")
    pdf.set_text_color(*WHITE)
    pdf.set_font("Vazirmatn", "B", 16)
    pdf.cell(0, 10, fa("سرویس خواب لوکس"), align="C")
    pdf.set_text_color(*GOLD)
    pdf.set_font("Vazirmatn", "", 10)
    pdf.cell(0, 8, fa("کلاسیک  -  نئوکلاسیک  -  مینیمال"), align="C")
    pdf.set_text_color(*WHITE)
    pdf.set_font("Vazirmatn", "", 9)
    pdf.set_y(120)
    pdf.cell(0, 8, fa("استراتژی کامل محتوا و طراحی پیج اینستاگرام"), align="C")
    pdf.set_text_color(*GOLD)
    pdf.set_font("Vazirmatn", "B", 11)
    pdf.set_y(150)
    pdf.cell(0, 8, fa("تحلیل رقبا:"), align="C")
    pdf.set_text_color(*WHITE)
    pdf.set_font("Vazirmatn", "", 10)
    pdf.cell(0, 8, fa("هیواهوم (۶۵.۶K)  |  کاناپو (۶۲.۴K)"), align="C")
    pdf.set_text_color(*LIGHT_GRAY)
    pdf.set_font("Vazirmatn", "", 8)
    pdf.set_y(250)
    pdf.cell(0, 6, fa("۱۴۰۵/۰۷/۱۲"), align="C")

    # === PAGE 2: BRAND IDENTITY ===
    pdf.add_page()
    pdf.chapter_title("هویت برند")
    pdf.sub_title("اطلاعات پایه")
    pdf.add_info_box("برند", "سناتور (Senator)")
    pdf.add_info_box("حوزه فعالیت", "سرویس خواب (Bed Sets)")
    pdf.add_info_box("مخاطب هدف", "خریداران سبک کلاسیک و نئوکلاسیک")
    pdf.add_info_box("سبک بصری", "ترکیبی از لوکس و مینیمال (لوکس مینیمال)")
    pdf.sub_title("الت رنگی")
    colors = [(NAVY, "سرمهای تیره\n#1B2A4A"), (CREAM, "کرم طلایی\n#F5F0E8"), (GOLD, "طلایی ملایم\n#C9A96E"), (BLACK, "مشکی مات\n#2C2C2C"), (LIGHT_GRAY, "خاکستری روشن\n#E8E8E8")]
    x_start = 15
    for rgb, label in colors:
        pdf.add_color_box(rgb, label, x_start, pdf.get_y(), 35, 18)
        x_start += 37
    pdf.ln(22)
    pdf.sub_title("فونت")
    pdf.bullet_point("عنوانها: وزیرمتن (Bold)")
    pdf.bullet_point("متن اصلی: وزیرمتن (Regular)")
    pdf.bullet_point("اعداد و قیمت: وزیرمتن (Medium)")
    pdf.sub_title("لوگو")
    pdf.bullet_point("لوگو باید ساده و مینیمال باشه")
    pdf.bullet_point("ترکیب حرف S با یه المان خواب/تخت")
    pdf.bullet_point("رنگ لوگو: سرمهای یا طلایی")

    # === PAGE 3: BIO & HIGHLIGHTS ===
    pdf.add_page()
    pdf.chapter_title("بیو پیج و هایلایت‌ها")
    pdf.sub_title("بیو پیج پیشنهادی")
    pdf.set_fill_color(*CREAM)
    pdf.rect(10, pdf.get_y(), 190, 30, "F")
    pdf.set_text_color(*NAVY)
    pdf.set_font("Vazirmatn", "B", 9)
    pdf.set_xy(15, pdf.get_y() + 3)
    pdf.multi_cell(180, 6, fa("سناتور | سرویس خواب لوکس\nکلاسیک  -  نئوکلاسیک  -  مینیمال\nارسال سراسری\nسفارش دایرکت\n021-XXXXXXX"), align="R")
    pdf.set_text_color(*BLACK)
    pdf.ln(34)
    pdf.sub_title("هایلایت‌های پیشنهادی")
    highlights = [("درباره ما", "معرفی برند و تاریخچه"), ("محصولات", "انواع سرویس خواب"), ("نظرات مشتریان", "رضایت‌نامه‌ها و نظرات"), ("پشت صحنه", "کارگاه تولید"), ("سوالات متداول", "پاسخ به سوالات رایج"), ("تماس با ما", "اطلاعات تماس"), ("ارسالی شما", "عکس‌های مشتریان")]
    pdf.add_table(["هایلایت", "محتوا"], highlights, [60, 130])

    # === PAGE 4: COMPETITOR ANALYSIS ===
    pdf.add_page()
    pdf.chapter_title("تحلیل رقبا")
    pdf.sub_title("هیواهوم (@hivahome)")
    pdf.add_info_box("اطلاعات کلی", "۶۵,۶۰۰+ فالوئر | ۳۱ فالوئینگ | مبلمان و صنایع چوبی")
    pdf.set_font("Vazirmatn", "B", 9)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 6, fa("نقاط قوت:"), align="R")
    pdf.ln()
    pdf.set_text_color(*BLACK)
    pdf.set_font("Vazirmatn", "", 8)
    pdf.bullet_point("برند قوی با ۶۵K+ فالوئر و تاریخچه ۱۳۰۰")
    pdf.bullet_point("تنوع محصولات (مبلمان، میز، صندلی)")
    pdf.bullet_point("محتوای پشت صحنه (کارگاه تولید)")
    pdf.bullet_point("هایلایت‌های منظم")
    pdf.bullet_point("ریلز منظم (۲-۳ بار در هفته)")
    pdf.set_font("Vazirmatn", "B", 9)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 6, fa("نقاط ضعف:"), align="R")
    pdf.ln()
    pdf.set_text_color(*BLACK)
    pdf.set_font("Vazirmatn", "", 8)
    pdf.bullet_point("بیو ضعیف (بدون CTA، بدون ایموجی)")
    pdf.bullet_point("تعامل کم با مخاطب")
    pdf.bullet_point("محتوای تکراری")
    pdf.bullet_point("کم‌رنگ بودن")
    pdf.ln(4)
    pdf.sub_title("کاناپو (@canappo.ir)")
    pdf.add_info_box("اطلاعات کلی", "۶۲,۴۰۰+ فالوئر | ۱۳۹ فالوئینگ | مبلمان، غذاخوری، تخت خواب")
    pdf.set_font("Vazirmatn", "B", 9)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 6, fa("نقاط قوت:"), align="R")
    pdf.ln()
    pdf.set_text_color(*BLACK)
    pdf.set_font("Vazirmatn", "", 8)
    pdf.bullet_point("برند قوی با ۶۲K+ فالوئر")
    pdf.bullet_point("تنوع محصولات (مبلمان، تخت، غذاخوری)")
    pdf.bullet_point("هایلایت‌های متنوع (۱۰ هایلایت)")
    pdf.bullet_point("عکس‌های مشتریان (ارسالی شما)")
    pdf.bullet_point("سبک مینیمال و مدرن")
    pdf.bullet_point("شماره تماس در بیو")
    pdf.set_font("Vazirmatn", "B", 9)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 6, fa("نقاط ضعف:"), align="R")
    pdf.ln()
    pdf.set_text_color(*BLACK)
    pdf.set_font("Vazirmatn", "", 8)
    pdf.bullet_point("بیو ضعیف (بدون CTA، بدون ایموجی)")
    pdf.bullet_point("تعامل کم با مخاطب")
    pdf.bullet_point("هایلایت تکراری (ارسالی شما دو بار)")
    pdf.bullet_point("کم‌رنگ بودن")

    # === PAGE 5: COMPARISON ===
    pdf.add_page()
    pdf.chapter_title("مقایسه رقبا")
    headers = ["معیار", "هیواهوم", "کاناپو", "برنده"]
    rows = [["فالوئر", "۶۵.۶K", "۶۲.۴K", "هیواهوم"], ["فالوئینگ", "۳۱", "۱۳۹", "کاناپو"], ["تنوع محصولات", "متوسط", "زیاد", "کاناپو"], ["هایلایت‌ها", "۱۰", "۱۰", "مساوی"], ["عکس مشتریان", "ندارد", "دارد", "کاناپو"], ["شماره تماس", "ندارد", "دارد", "کاناپو"], ["سبک بصری", "کلاسیک", "مینیمال", "کاناپو"], ["فرکانس انتشار", "۳-۵/هفته", "۲-۴/هفته", "هیواهوم"]]
    pdf.add_table(headers, rows, [50, 45, 45, 50])
    pdf.sub_title("نتیجه‌گیری")
    pdf.body_text("کاناپو رقیب قوی‌تری نسبت به هیواهوم محسوب میشه چون فالوئر مشابه داره، محتوای متنوع‌تری داره، هایلایت‌های بهتری داره و سبک مینیمال و مدرن داره که به سبک سناتور نزدیکه.")

    # === PAGE 6: CONTENT STRATEGY ===
    pdf.add_page()
    pdf.chapter_title("استراتژی محتوا")
    pdf.sub_title("۵ ستون محتوایی")
    pillars = [("محصولات", "۴۰٪", "عکس و ویدیوی محصولات"), ("آموزشی", "۲۰٪", "راهنمای انتخاب، مراقبت، نکات"), ("تعاملی", "۱۵٪", "نظرسنجی، سوال و جواب، مسابقه"), ("اعتمادساز", "۱۵٪", "نظرات مشتریان، پشت صحنه"), ("تبلیغاتی", "۱۰٪", "تخفیف، پیشنهاد ویژه، فروش")]
    pdf.add_table(["ستون", "درصد", "محتوا"], pillars, [50, 30, 110])
    pdf.sub_title("چیدمان گرید")
    pdf.body_text("الگوی متناوب: لوکس، مینیمال، لوکس. هر سه پست اول باید یه تصویر واحد و هماهنگ باشن تا گرید قشنگ به نظر برسه.")
    pdf.sub_title("انواع محتوا")
    pdf.bullet_point("پست تکی: عکس محصول، جزئیات، لات لایف")
    pdf.bullet_point("کاروسل: معرفی محصولات، راهنماها")
    pdf.bullet_point("ریلز: پشت صحنه، ASMR، قبل/بعد، نمایش محصول")
    pdf.bullet_point("استوری: نظرسنجی، سوال و جواب، کد تخفیف")

    # === PAGE 7: CONTENT CALENDAR ===
    pdf.add_page()
    pdf.chapter_title("تقویم محتوایی (۴ هفته)")
    weeks = [("هفته ۱: معرفی برند", "معرفی برند + ۵ مدل محبوب | ویدیوی کوتاه از کارگاه | نظرسنجی | عکس مدل لوکس | پشت صحنه تولید | سوال و جواب | عکس مدل کلاسیک با قیمت"), ("هفته ۲: آموزش و اطلاعات", "راهنمای انتخاب رنگ | ویدیوی مراقبت | مقایسه پارچه‌ها | عکس مدل نئوکلاسیک | تغییر دکوراسیون | نظرات مشتریان | عکس مدل مینیمال"), ("هفته ۳: تعامل و اعتماد", "قبل و بعد دکوراسیون | ویدیوی بسته‌بندی | مسابقه | عکس با مشتری راضی | نمایش سریع محصولات | پاسخ به سوالات | عکس مدل جدید"), ("هفته ۴: فروش و تبلیغات", "پیشنهاد ویژه هفته | ویدیوی تبلیغاتی | کد تخفیف | عکس با تخفیف | ویدیوی مشتری در خانه | شمارش معکوس | عکس محصول پرفروش")]
    for week_title, content in weeks:
        pdf.sub_title(week_title)
        pdf.body_text(content)
        pdf.ln(2)

    # === PAGE 8: REELS IDEAS ===
    pdf.add_page()
    pdf.chapter_title("ایده‌های ریلز")
    reels = [("ASMR بسته‌بندی", "صدای پارچه، چینش مرتب"), ("Before/After", "تغییر دکوراسیون اتاق خواب"), ("Speed Run", "چینش سریع تخت در ۳۰ ثانیه"), ("Behind the Scenes", "کارگاه تولید، دستگاه‌ها"), ("Customer Review", "نظرات مشتریان واقعی"), ("Product Showcase", "نمایش ۳۶۰ درجه محصول"), ("Day in the Life", "یه روز کاری در شرکت سناتور")]
    pdf.add_table(["ایده", "توضیحات"], reels, [80, 110])
    pdf.sub_title("کپشن‌های پیشنهادی")
    captions = ["خواب خوب، زندگی خوب", "هر شب یه شروع جدید", "لوکس بودن یعنی سادگی", "انتخاب درست، استراحت درست", "سناتور، همراه خواب شما"]
    for cap in captions:
        pdf.bullet_point(cap)

    # === PAGE 9: HASHTAGS ===
    pdf.add_page()
    pdf.chapter_title("استراتژی هشتگ")
    pdf.sub_title("هشتگ‌های اصلی (هر پست)")
    pdf.set_fill_color(*CREAM)
    pdf.rect(10, pdf.get_y(), 190, 25, "F")
    pdf.set_text_color(*NAVY)
    pdf.set_font("Vazirmatn", "B", 8)
    pdf.set_xy(15, pdf.get_y() + 3)
    pdf.multi_cell(180, 5, fa("#سرویس_خواب #سناتور #تخت_خواب #دکوراسیون_اتاق_خواب\n#مد_کلاسیک #نئوکلاسیک #خواب_لوکس #استراحت #خانه_لوکس"), align="R")
    pdf.set_text_color(*BLACK)
    pdf.ln(29)
    pdf.sub_title("هشتگ‌های تکمیلی")
    pdf.set_fill_color(*CREAM)
    pdf.rect(10, pdf.get_y(), 190, 25, "F")
    pdf.set_text_color(*NAVY)
    pdf.set_font("Vazirmatn", "B", 8)
    pdf.set_xy(15, pdf.get_y() + 3)
    pdf.multi_cell(180, 5, fa("#فروش_سرویس_خواب #پارچه_نخی #پارچه_کتان #دکوراسیون_مدرن\n#اتاق_خواب_رویایی #تخت_دو_نفره #تخت_یک_نفره #لوازم_خانه\n#دکوراسیون_داخلی #طراحی_داخلی #خانه_دلنشین #زندگی_لوکس"), align="R")
    pdf.set_text_color(*BLACK)
    pdf.ln(29)

    # === PAGE 10: GROWTH STRATEGY ===
    pdf.add_page()
    pdf.chapter_title("استراتژی رشد")
    pdf.sub_title("کوتاه‌مدت (۱-۳ ماه)")
    pdf.bullet_point("۳ پست در هفته (حداقل)")
    pdf.bullet_point("۵ ریلز در هفته")
    pdf.bullet_point("استوری روزانه (حداقل ۳ اسلاید)")
    pdf.bullet_point("پاسخ به کامنت‌ها و دایرکت‌ها")
    pdf.bullet_point("استفاده از هشتگ‌های مرتبط")
    pdf.sub_title("میان‌مدت (۳-۶ ماه)")
    pdf.bullet_point("همکاری با اینفلوئنسرهای دکوراسیون")
    pdf.bullet_point("مسابقه و جایزه")
    pdf.bullet_point("محتوای آموزشی بیشتر")
    pdf.bullet_point("معرفی محصولات جدید")
    pdf.sub_title("بلندمدت (۶+ ماه)")
    pdf.bullet_point("برند شخصی مدیر شرکت")
    pdf.bullet_point("محتوای ویدیویی حرفه‌ای")
    pdf.bullet_point("همکاری با برندهای مکمل")
    pdf.bullet_point("فروش آنلاین و اینستاگرام شاپ")

    # === PAGE 11: KPIs ===
    pdf.add_page()
    pdf.chapter_title("معیارهای موفقیت (KPI)")
    headers = ["معیار", "هدف ۳ ماهه", "هدف ۶ ماهه"]
    rows = [["فالوئر", "۱,۰۰۰+", "۵,۰۰۰+"], ["نرخ تعامل", "۳٪+", "۵٪+"], ["بازدید ریلز", "۱,۰۰۰+", "۵,۰۰۰+"], ["کلیک لینک", "۱۰۰+", "۵۰۰+"], ["پیام سفارش", "۱۰+", "۵۰+"]]
    pdf.add_table(headers, rows, [70, 60, 60])
    pdf.sub_title("چکلیست روزانه")
    checklist = ["پست روزانه منتشر شده؟", "استوری گذاشته شده؟", "به کامنت‌ها پاسخ داده شده؟", "به دایرکت‌ها پاسخ داده شده؟", "ریلز جدید گذاشته شده؟", "هشتگ‌ها به روز هستن؟", "با پیج‌های مشابه تعامل داشتید？"]
    for item in checklist:
        pdf.bullet_point(item)

    # === PAGE 12: FINAL STRATEGY ===
    pdf.add_page()
    pdf.chapter_title("استراتژی نهایی سناتور")
    pdf.sub_title("۵ مزیت رقابتی")
    advantages = [("بیو حرفه‌ای‌تر", "ترکیب بهترین‌ها + CTA + ایموجی + هشتگ"), ("تنوع محتوایی بیشتر", "عکس مشتری + آموزش + نظرات + قبل/بعد"), ("تعامل فعال", "پاسخ به کامنت، نظرسنجی، مسابقه"), ("رنگ‌بندی متنوع‌تر", "سرمهای، کرم طلایی، طلایی ملایم"), ("هایلایت‌های کامل‌تر", "درباره ما، نظرات، سوالات متداول، تماس")]
    pdf.add_table(["مزیت", "جزئیات"], advantages, [70, 120])
    pdf.sub_title("نتیجه‌گیری نهایی")
    pdf.body_text("سناتور می‌تونه با ترکیب نقاط قوت هر دو رقیب (هیواهوم و کاناپو) + اضافه کردن محتوای آموزشی، تعامل فعال با مخاطب، رنگ‌بندی متنوع‌تر و هایلایت‌های کامل‌تر، از هر دو رقیب جلو بزنه و سریع‌تر رشد کنه.")
    pdf.ln(10)
    pdf.set_fill_color(*GOLD)
    pdf.rect(10, pdf.get_y(), 190, 20, "F")
    pdf.set_text_color(*WHITE)
    pdf.set_font("Vazirmatn", "B", 10)
    pdf.set_xy(15, pdf.get_y() + 3)
    pdf.multi_cell(180, 6, fa("سناتور | سرویس خواب لوکس\nکلاسیک  -  نئوکلاسیک  -  مینیمال"), align="C")
    pdf.set_text_color(*BLACK)

    output_path = r"C:\Users\Lucifer\Documents\Default Project\senator-strategy-final.pdf"
    pdf.output(output_path)
    print(f"PDF saved to: {output_path}")

if __name__ == "__main__":
    create_pdf()
