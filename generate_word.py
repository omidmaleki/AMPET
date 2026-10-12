from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# Colors
NAVY = RGBColor(0x1B, 0x2A, 0x4A)
GOLD = RGBColor(0xC9, 0xA9, 0x6E)
BLACK = RGBColor(0x2C, 0x2C, 0x2C)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CREAM = RGBColor(0xF5, 0xF0, 0xE8)

def set_cell_shading(cell, color):
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), color)
    shading_elm.set(qn('w:val'), 'clear')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def add_heading_rtl(doc, text, level=1, color=NAVY, size=16):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run(text)
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.color.rgb = color
    return p

def add_paragraph_rtl(doc, text, size=11, bold=False, color=BLACK):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run(text)
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return p

def add_bullet_rtl(doc, text, size=11):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run(f"• {text}")
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(size)
    run.font.color.rgb = BLACK
    return p

def add_table_rtl(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    
    # Headers
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(header)
        run.font.name = 'Vazirmatn'
        run.font.size = Pt(10)
        run.font.bold = True
        run.font.color.rgb = WHITE
        set_cell_shading(cell, "1B2A4A")
    
    # Rows
    for i, row in enumerate(rows):
        for j, cell_text in enumerate(row):
            cell = table.rows[i + 1].cells[j]
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(str(cell_text))
            run.font.name = 'Vazirmatn'
            run.font.size = Pt(9)
            run.font.color.rgb = BLACK
            if i % 2 == 0:
                set_cell_shading(cell, "F5F0E8")
    
    return table

def create_word():
    doc = Document()
    
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Vazirmatn'
    font.size = Pt(11)
    
    # Set RTL for the document
    sectPr = doc.sections[0]._sectPr
    rtl = OxmlElement('w:bidi')
    rtl.set(qn('w:val'), 'true')
    sectPr.append(rtl)
    
    # === COVER PAGE ===
    for _ in range(6):
        doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("سناتور")
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(48)
    run.font.bold = True
    run.font.color.rgb = NAVY
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("سرویس خواب لوکس")
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(24)
    run.font.bold = True
    run.font.color.rgb = GOLD
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("کلاسیک  •  نئوکلاسیک  •  مینیمال")
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(14)
    run.font.color.rgb = BLACK
    
    for _ in range(4):
        doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("استراتژی کامل محتوا و طراحی پیج اینستاگرام")
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = NAVY
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("تحلیل رقبا: هیواهوم (۶۵.۶K)  |  کاناپو (۶۲.۴K)")
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(12)
    run.font.color.rgb = BLACK
    
    for _ in range(6):
        doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("۱۴۰۵/۰۷/۱۲")
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(10)
    run.font.color.rgb = BLACK
    
    doc.add_page_break()
    
    # === BRAND IDENTITY ===
    add_heading_rtl(doc, "هویت برند", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_heading_rtl(doc, "اطلاعات پایه", size=14, color=GOLD)
    add_paragraph_rtl(doc, "برند: سناتور (Senator)")
    add_paragraph_rtl(doc, "حوزه فعالیت: سرویس خواب (Bed Sets)")
    add_paragraph_rtl(doc, "مخاطب هدف: خریداران سبک کلاسیک و نئوکلاسیک")
    add_paragraph_rtl(doc, "سبک بصری: ترکیبی از لوکس و مینیمال (لوکس مینیمال)")
    doc.add_paragraph()
    
    add_heading_rtl(doc, "الت رنگی", size=14, color=GOLD)
    add_table_rtl(doc, 
        ["رنگ", "کد HEX", "کاربرد"],
        [
            ["سرمهای تیره", "#1B2A4A", "رنگ اصلی برند"],
            ["کرم طلایی", "#F5F0E8", "رنگ ثانویه"],
            ["طلایی ملایم", "#C9A96E", "تاکیدها و قاب‌ها"],
            ["مشکی مات", "#2C2C2C", "متن اصلی"],
            ["خاکستری روشن", "#E8E8E8", "پس‌زمینه ثانویه"],
        ],
        col_widths=[Cm(4), Cm(4), Cm(8)]
    )
    doc.add_paragraph()
    
    add_heading_rtl(doc, "فونت", size=14, color=GOLD)
    add_bullet_rtl(doc, "عنوان‌ها: وزیرمتن (Bold)")
    add_bullet_rtl(doc, "متن اصلی: وزیرمتن (Regular)")
    add_bullet_rtl(doc, "اعداد و قیمت: وزیرمتن (Medium)")
    doc.add_paragraph()
    
    add_heading_rtl(doc, "لوگو", size=14, color=GOLD)
    add_bullet_rtl(doc, "لوگو باید ساده و مینیمال باشه")
    add_bullet_rtl(doc, "ترکیب حرف S با یه المان خواب/تخت")
    add_bullet_rtl(doc, "رنگ لوگو: سرمهای یا طلایی")
    
    doc.add_page_break()
    
    # === BIO & HIGHLIGHTS ===
    add_heading_rtl(doc, "بیو پیج و هایلایت‌ها", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_heading_rtl(doc, "بیو پیج پیشنهادی", size=14, color=GOLD)
    add_paragraph_rtl(doc, "🛏️ سناتور | سرویس خواب لوکس")
    add_paragraph_rtl(doc, "✨ کلاسیک • نئوکلاسیک • مینیمال")
    add_paragraph_rtl(doc, "📦 ارسال سراسری")
    add_paragraph_rtl(doc, "📩 سفارش دایرکت")
    add_paragraph_rtl(doc, "📞 021-XXXXXXX")
    doc.add_paragraph()
    
    add_heading_rtl(doc, "هایلایت‌های پیشنهادی", size=14, color=GOLD)
    add_table_rtl(doc,
        ["هایلایت", "محتوا"],
        [
            ["درباره ما", "معرفی برند و تاریخچه"],
            ["محصولات", "انواع سرویس خواب"],
            ["نظرات مشتریان", "رضایت‌نامه‌ها و نظرات"],
            ["پشت صحنه", "کارگاه تولید"],
            ["سوالات متداول", "پاسخ به سوالات رایج"],
            ["تماس با ما", "اطلاعات تماس"],
            ["ارسالی شما", "عکس‌های مشتریان"],
        ],
        col_widths=[Cm(5), Cm(11)]
    )
    
    doc.add_page_break()
    
    # === COMPETITOR ANALYSIS ===
    add_heading_rtl(doc, "تحلیل رقبا", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_heading_rtl(doc, "هیواهوم (@hivahome)", size=14, color=GOLD)
    add_paragraph_rtl(doc, "۶۵,۶۰۰+ فالوئر | ۳۱ فالوئینگ | مبلمان و صنایع چوبی")
    doc.add_paragraph()
    
    add_paragraph_rtl(doc, "نقاط قوت:", bold=True, color=NAVY)
    add_bullet_rtl(doc, "برند قوی با ۶۵K+ فالوئر و تاریخچه ۱۳۰۰")
    add_bullet_rtl(doc, "تنوع محصولات (مبلمان، میز، صندلی)")
    add_bullet_rtl(doc, "محتوای پشت صحنه (کارگاه تولید)")
    add_bullet_rtl(doc, "هایلایت‌های منظم")
    add_bullet_rtl(doc, "ریلز منظم (۲-۳ بار در هفته)")
    doc.add_paragraph()
    
    add_paragraph_rtl(doc, "نقاط ضعف:", bold=True, color=NAVY)
    add_bullet_rtl(doc, "بیو ضعیف (بدون CTA، بدون ایموجی)")
    add_bullet_rtl(doc, "تعامل کم با مخاطب")
    add_bullet_rtl(doc, "محتوای تکراری")
    add_bullet_rtl(doc, "کم‌رنگ بودن")
    doc.add_paragraph()
    
    add_heading_rtl(doc, "کاناپو (@canappo.ir)", size=14, color=GOLD)
    add_paragraph_rtl(doc, "۶۲,۴۰۰+ فالوئر | ۱۳۹ فالوئینگ | مبلمان، غذاخوری، تخت خواب")
    doc.add_paragraph()
    
    add_paragraph_rtl(doc, "نقاط قوت:", bold=True, color=NAVY)
    add_bullet_rtl(doc, "برند قوی با ۶۲K+ فالوئر")
    add_bullet_rtl(doc, "تنوع محصولات (مبلمان، تخت، غذاخوری)")
    add_bullet_rtl(doc, "هایلایت‌های متنوع (۱۰ هایلایت)")
    add_bullet_rtl(doc, "عکس‌های مشتریان (ارسالی شما)")
    add_bullet_rtl(doc, "سبک مینیمال و مدرن")
    add_bullet_rtl(doc, "شماره تماس در بیو")
    doc.add_paragraph()
    
    add_paragraph_rtl(doc, "نقاط ضعف:", bold=True, color=NAVY)
    add_bullet_rtl(doc, "بیو ضعیف (بدون CTA، بدون ایموجی)")
    add_bullet_rtl(doc, "تعامل کم با مخاطب")
    add_bullet_rtl(doc, "هایلایت تکراری (ارسالی شما دو بار)")
    add_bullet_rtl(doc, "کم‌رنگ بودن")
    
    doc.add_page_break()
    
    # === COMPARISON ===
    add_heading_rtl(doc, "مقایسه رقبا", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_table_rtl(doc,
        ["معیار", "هیواهوم", "کاناپو", "برنده"],
        [
            ["فالوئر", "۶۵.۶K", "۶۲.۴K", "هیواهوم"],
            ["فالوئینگ", "۳۱", "۱۳۹", "کاناپو"],
            ["تنوع محصولات", "متوسط", "زیاد", "کاناپو"],
            ["هایلایت‌ها", "۱۰", "۱۰", "مساوی"],
            ["عکس مشتریان", "ندارد", "دارد", "کاناپو"],
            ["شماره تماس", "ندارد", "دارد", "کاناپو"],
            ["سبک بصری", "کلاسیک", "مینیمال", "کاناپو"],
            ["فرکانس انتشار", "۳-۵/هفته", "۲-۴/هفته", "هیواهوم"],
        ],
        col_widths=[Cm(4), Cm(3.5), Cm(3.5), Cm(3.5)]
    )
    doc.add_paragraph()
    
    add_heading_rtl(doc, "نتیجه‌گیری", size=14, color=GOLD)
    add_paragraph_rtl(doc, "کاناپو رقیب قوی‌تری نسبت به هیواهوم محسوب میشه چون فالوئر مشابه داره، محتوای متنوع‌تری داره، هایلایت‌های بهتری داره و سبک مینیمال و مدرن داره که به سبک سناتور نزدیکه.")
    
    doc.add_page_break()
    
    # === CONTENT STRATEGY ===
    add_heading_rtl(doc, "استراتژی محتوا", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_heading_rtl(doc, "۵ ستون محتوایی", size=14, color=GOLD)
    add_table_rtl(doc,
        ["ستون", "درصد", "محتوا"],
        [
            ["محصولات", "۴۰٪", "عکس و ویدیوی محصولات"],
            ["آموزشی", "۲۰٪", "راهنمای انتخاب، مراقبت، نکات"],
            ["تعاملی", "۱۵٪", "نظرسنجی، سوال و جواب، مسابقه"],
            ["اعتمادساز", "۱۵٪", "نظرات مشتریان، پشت صحنه"],
            ["تبلیغاتی", "۱۰٪", "تخفیف، پیشنهاد ویژه، فروش"],
        ],
        col_widths=[Cm(4), Cm(3), Cm(9)]
    )
    doc.add_paragraph()
    
    add_heading_rtl(doc, "چیدمان گرید", size=14, color=GOLD)
    add_paragraph_rtl(doc, "الگوی متناوب: لوکس → مینیمال → لوکس. هر سه پست اول باید یه تصویر واحد و هماهنگ باشن تا گرید قشنگ به نظر برسه.")
    doc.add_paragraph()
    
    add_heading_rtl(doc, "انواع محتوا", size=14, color=GOLD)
    add_bullet_rtl(doc, "پست تکی: عکس محصول، جزئیات، لات لایف")
    add_bullet_rtl(doc, "کاروسل: معرفی محصولات، راهنماها")
    add_bullet_rtl(doc, "ریلز: پشت صحنه، ASMR، قبل/بعد، نمایش محصول")
    add_bullet_rtl(doc, "استوری: نظرسنجی، سوال و جواب، کد تخفیف")
    
    doc.add_page_break()
    
    # === CONTENT CALENDAR ===
    add_heading_rtl(doc, "تقویم محتوایی (۴ هفته)", size=18, color=NAVY)
    doc.add_paragraph()
    
    weeks = [
        ("هفته ۱: معرفی برند", "معرفی برند + ۵ مدل محبوب | ویدیوی کوتاه از کارگاه | نظرسنجی | عکس مدل لوکس | پشت صحنه تولید | سوال و جواب | عکس مدل کلاسیک با قیمت"),
        ("هفته ۲: آموزش و اطلاعات", "راهنمای انتخاب رنگ | ویدیوی مراقبت | مقایسه پارچه‌ها | عکس مدل نئوکلاسیک | تغییر دکوراسیون | نظرات مشتریان | عکس مدل مینیمال"),
        ("هفته ۳: تعامل و اعتماد", "قبل و بعد دکوراسیون | ویدیوی بسته‌بندی | مسابقه | عکس با مشتری راضی | نمایش سریع محصولات | پاسخ به سوالات | عکس مدل جدید"),
        ("هفته ۴: فروش و تبلیغات", "پیشنهاد ویژه هفته | ویدیوی تبلیغاتی | کد تخفیف | عکس با تخفیف | ویدیوی مشتری در خانه | شمارش معکوس | عکس محصول پرفروش"),
    ]
    
    for week_title, content in weeks:
        add_heading_rtl(doc, week_title, size=14, color=GOLD)
        add_paragraph_rtl(doc, content)
        doc.add_paragraph()
    
    doc.add_page_break()
    
    # === REELS IDEAS ===
    add_heading_rtl(doc, "ایده‌های ریلز", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_table_rtl(doc,
        ["ایده", "توضیحات"],
        [
            ["ASMR بسته‌بندی", "صدای پارچه، چینش مرتب"],
            ["Before/After", "تغییر دکوراسیون اتاق خواب"],
            ["Speed Run", "چینش سریع تخت در ۳۰ ثانیه"],
            ["Behind the Scenes", "کارگاه تولید، دستگاه‌ها"],
            ["Customer Review", "نظرات مشتریان واقعی"],
            ["Product Showcase", "نمایش ۳۶۰ درجه محصول"],
            ["Day in the Life", "یه روز کاری در شرکت سناتور"],
        ],
        col_widths=[Cm(5), Cm(11)]
    )
    doc.add_paragraph()
    
    add_heading_rtl(doc, "کپشن‌های پیشنهادی", size=14, color=GOLD)
    captions = [
        "خواب خوب، زندگی خوب",
        "هر شب یه شروع جدید",
        "لوکس بودن یعنی سادگی",
        "انتخاب درست، استراحت درست",
        "سناتور، همراه خواب شما",
    ]
    for cap in captions:
        add_bullet_rtl(doc, cap)
    
    doc.add_page_break()
    
    # === HASHTAGS ===
    add_heading_rtl(doc, "استراتژی هشتگ", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_heading_rtl(doc, "هشتگ‌های اصلی (هر پست)", size=14, color=GOLD)
    add_paragraph_rtl(doc, "#سرویس_خواب #سناتور #تخت_خواب #دکوراسیون_اتاق_خواب")
    add_paragraph_rtl(doc, "#مد_کلاسیک #نئوکلاسیک #خواب_لوکس #استراحت #خانه_لوکس")
    doc.add_paragraph()
    
    add_heading_rtl(doc, "هشتگ‌های تکمیلی", size=14, color=GOLD)
    add_paragraph_rtl(doc, "#فروش_سرویس_خواب #پارچه_نخی #پارچه_کتان #دکوراسیون_مدرن")
    add_paragraph_rtl(doc, "#اتاق_خواب_رویایی #تخت_دو_نفره #تخت_یک_نفره #لوازم_خانه")
    add_paragraph_rtl(doc, "#دکوراسیون_داخلی #طراحی_داخلی #خانه_دلنشین #زندگی_لوکس")
    
    doc.add_page_break()
    
    # === GROWTH STRATEGY ===
    add_heading_rtl(doc, "استراتژی رشد", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_heading_rtl(doc, "کوتاه‌مدت (۱-۳ ماه)", size=14, color=GOLD)
    add_bullet_rtl(doc, "۳ پست در هفته (حداقل)")
    add_bullet_rtl(doc, "۵ ریلز در هفته")
    add_bullet_rtl(doc, "استوری روزانه (حداقل ۳ اسلاید)")
    add_bullet_rtl(doc, "پاسخ به کامنت‌ها و دایرکت‌ها")
    add_bullet_rtl(doc, "استفاده از هشتگ‌های مرتبط")
    doc.add_paragraph()
    
    add_heading_rtl(doc, "میان‌مدت (۳-۶ ماه)", size=14, color=GOLD)
    add_bullet_rtl(doc, "همکاری با اینفلوئنسرهای دکوراسیون")
    add_bullet_rtl(doc, "مسابقه و جایزه")
    add_bullet_rtl(doc, "محتوای آموزشی بیشتر")
    add_bullet_rtl(doc, "معرفی محصولات جدید")
    doc.add_paragraph()
    
    add_heading_rtl(doc, "بلندمدت (۶+ ماه)", size=14, color=GOLD)
    add_bullet_rtl(doc, "برند شخصی مدیر شرکت")
    add_bullet_rtl(doc, "محتوای ویدیویی حرفه‌ای")
    add_bullet_rtl(doc, "همکاری با برندهای مکمل")
    add_bullet_rtl(doc, "فروش آنلاین و اینستاگرام شاپ")
    
    doc.add_page_break()
    
    # === KPIs ===
    add_heading_rtl(doc, "معیارهای موفقیت (KPI)", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_table_rtl(doc,
        ["معیار", "هدف ۳ ماهه", "هدف ۶ ماهه"],
        [
            ["فالوئر", "۱,۰۰۰+", "۵,۰۰۰+"],
            ["نرخ تعامل", "۳٪+", "۵٪+"],
            ["بازدید ریلز", "۱,۰۰۰+", "۵,۰۰۰+"],
            ["کلیک لینک", "۱۰۰+", "۵۰۰+"],
            ["پیام سفارش", "۱۰+", "۵۰+"],
        ],
        col_widths=[Cm(5), Cm(5), Cm(5)]
    )
    doc.add_paragraph()
    
    add_heading_rtl(doc, "چکلیست روزانه", size=14, color=GOLD)
    checklist = [
        "پست روزانه منتشر شده؟",
        "استوری گذاشته شده؟",
        "به کامنت‌ها پاسخ داده شده؟",
        "به دایرکت‌ها پاسخ داده شده؟",
        "ریلز جدید گذاشته شده؟",
        "هشتگ‌ها به روز هستن؟",
        "با پیج‌های مشابه تعامل داشتید؟",
    ]
    for item in checklist:
        add_bullet_rtl(doc, item)
    
    doc.add_page_break()
    
    # === FINAL STRATEGY ===
    add_heading_rtl(doc, "استراتژی نهایی سناتور", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_heading_rtl(doc, "۵ مزیت رقابتی", size=14, color=GOLD)
    add_table_rtl(doc,
        ["مزیت", "جزئیات"],
        [
            ["بیو حرفه‌ای‌تر", "ترکیب بهترین‌ها + CTA + ایموجی + هشتگ"],
            ["تنوع محتوایی بیشتر", "عکس مشتری + آموزش + نظرات + قبل/بعد"],
            ["تعامل فعال", "پاسخ به کامنت، نظرسنجی، مسابقه"],
            ["رنگ‌بندی متنوع‌تر", "سرمهای، کرم طلایی، طلایی ملایم"],
            ["هایلایت‌های کامل‌تر", "درباره ما، نظرات، سوالات متداول، تماس"],
        ],
        col_widths=[Cm(5), Cm(11)]
    )
    doc.add_paragraph()
    
    add_heading_rtl(doc, "نتیجه‌گیری نهایی", size=14, color=GOLD)
    add_paragraph_rtl(doc, "سناتور می‌تونه با ترکیب نقاط قوت هر دو رقیب (هیواهوم و کاناپو) + اضافه کردن محتوای آموزشی، تعامل فعال با مخاطب، رنگ‌بندی متنوع‌تر و هایلایت‌های کامل‌تر، از هر دو رقیب جلو بزنه و سریع‌تر رشد کنه.")
    
    doc.add_paragraph()
    doc.add_paragraph()
    
    # Footer
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("سناتور | سرویس خواب لوکس")
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = NAVY
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("کلاسیک  •  نئوکلاسیک  •  مینیمال")
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(12)
    run.font.color.rgb = GOLD
    
    # Save
    output_path = r"C:\Users\Lucifer\Documents\Default Project\senator-strategy-final.docx"
    doc.save(output_path)
    print(f"Word saved to: {output_path}")

if __name__ == "__main__":
    create_word()
