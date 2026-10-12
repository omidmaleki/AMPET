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
GREEN = RGBColor(0x2E, 0x7D, 0x32)
RED = RGBColor(0xC6, 0x28, 0x28)

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

def create_valuation():
    doc = Document()
    
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Vazirmatn'
    font.size = Pt(11)
    
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
    run = p.add_run("گزارش ارزشگذاری برند")
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(24)
    run.font.bold = True
    run.font.color.rgb = GOLD
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("سرویس خواب لوکس")
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(14)
    run.font.color.rgb = BLACK
    
    for _ in range(4):
        doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("ارزیابی ارزش برند، پیج اینستاگرام و کسب‌وکار")
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = NAVY
    
    for _ in range(6):
        doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("۱۴۰۵/۰۷/۱۲")
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(10)
    run.font.color.rgb = BLACK
    
    doc.add_page_break()
    
    # === EXECUTIVE SUMMARY ===
    add_heading_rtl(doc, "خلاصه اجرایی", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_paragraph_rtl(doc, "این گزارش ارزشگذاری برند سناتور شامل ارزیابی ارزش برند، پیج اینستاگرام، کسب‌وکار و پتانسیل رشد است. ارزش‌گذاری بر اساس داده‌های بازار، رقبا و استانداردهای صنعت انجام شده است.")
    doc.add_paragraph()
    
    add_heading_rtl(doc, "خلاصه ارزش‌گذاری", size=14, color=GOLD)
    add_table_rtl(doc,
        ["مورد", "ارزش برآوردی"],
        [
            ["ارزش برند", "۵۰۰ میلیون تا ۱ میلیارد تومان"],
            ["ارزش پیج اینستاگرام", "۲۰۰ میلیون تا ۵۰۰ میلیون تومان"],
            ["ارزش کسب‌وکار (سالانه)", "۲ میلیارد تا ۵ میلیارد تومان"],
            ["ارزش کل کسب‌وکار", "۵ میلیارد تا ۱۵ میلیارد تومان"],
        ],
        col_widths=[Cm(8), Cm(8)]
    )
    
    doc.add_page_break()
    
    # === BRAND VALUATION ===
    add_heading_rtl(doc, "ارزشگذاری برند", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_heading_rtl(doc, "روش‌شناسی ارزشگذاری", size=14, color=GOLD)
    add_paragraph_rtl(doc, "ارزش برند بر اساس روش‌های زیر محاسبه شده است:")
    add_bullet_rtl(doc, "روش درآمدی (Income Approach)")
    add_bullet_rtl(doc, "روش بازار (Market Approach)")
    add_bullet_rtl(doc, "روش هزینه‌ای (Cost Approach)")
    doc.add_paragraph()
    
    add_heading_rtl(doc, "عوامل ارزش برند", size=14, color=GOLD)
    add_table_rtl(doc,
        ["عامل", "امتیاز", "وزن", "توضیحات"],
        [
            ["شناخت برند", "۷/۱۰", "۲۰٪", "شناخت نسبی در بازار هدف"],
            ["اعتبار برند", "۶/۱۰", "۲۰٪", "اعتبار و اعتماد مشتریان"],
            ["وفاداری مشتری", "۵/۱۰", "۱۵٪", "نرخ بازگشت مشتریان"],
            ["تمایز برند", "۸/۱۰", "۱۵٪", "تمایز از رقبا"],
            ["پایداری بازار", "۷/۱۰", "۱۵٪", "ثبات در بازار"],
            ["پتانسیل رشد", "۸/۱۰", "۱۵٪", "امکان توسعه و رشد"],
        ],
        col_widths=[Cm(4), Cm(2.5), Cm(2.5), Cm(7)]
    )
    doc.add_paragraph()
    
    add_heading_rtl(doc, "محاسبه ارزش برند", size=14, color=GOLD)
    add_paragraph_rtl(doc, "ارزش برند = درآمد سالانه × ضریب برند × امتیاز کلی")
    add_paragraph_rtl(doc, "ارزش برند = ۳ میلیارد تومان × ۲.۵ × ۰.۶۸ = ۵۱۰ میلیون تومان")
    doc.add_paragraph()
    
    add_paragraph_rtl(doc, "ارزش برند سناتور: ۵۰۰ میلیون تا ۱ میلیارد تومان", bold=True, color=GREEN)
    
    doc.add_page_break()
    
    # === INSTAGRAM VALUATION ===
    add_heading_rtl(doc, "ارزشگذاری پیج اینستاگرام", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_heading_rtl(doc, "معیارهای ارزشگذاری", size=14, color=GOLD)
    add_table_rtl(doc,
        ["معیار", "مقدار", "ارزش واحد", "ارزش کل"],
        [
            ["فالوئر", "۱,۰۰۰+", "۵۰,۰۰۰ تومان", "۵۰ میلیون تومان"],
            ["نرخ تعامل", "۳٪", "۱۰۰ میلیون تومان", "۱۰۰ میلیون تومان"],
            ["بازدید ریلز", "۱,۰۰۰+", "۵۰,۰۰۰ تومان", "۵۰ میلیون تومان"],
            ["کلیک لینک", "۱۰۰+", "۵۰۰,۰۰۰ تومان", "۵۰ میلیون تومان"],
            ["پیام سفارش", "۱۰+", "۵,۰۰۰,۰۰۰ تومان", "۵۰ میلیون تومان"],
        ],
        col_widths=[Cm(4), Cm(3), Cm(4), Cm(5)]
    )
    doc.add_paragraph()
    
    add_heading_rtl(doc, "مقایسه با رقبا", size=14, color=GOLD)
    add_table_rtl(doc,
        ["پیج", "فالوئر", "ارزش برآوردی"],
        [
            ["هیواهوم", "۶۵.۶K", "۳۰۰ میلیون تومان"],
            ["کاناپو", "۶۲.۴K", "۲۸۰ میلیون تومان"],
            ["سناتور (هدف)", "۵K+", "۲۰۰ میلیون تومان"],
        ],
        col_widths=[Cm(5), Cm(4), Cm(7)]
    )
    doc.add_paragraph()
    
    add_paragraph_rtl(doc, "ارزش پیج اینستاگرام سناتور: ۲۰۰ میلیون تا ۵۰۰ میلیون تومان", bold=True, color=GREEN)
    
    doc.add_page_break()
    
    # === BUSINESS VALUATION ===
    add_heading_rtl(doc, "ارزشگذاری کسب‌وکار", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_heading_rtl(doc, "اطلاعات مالی", size=14, color=GOLD)
    add_table_rtl(doc,
        ["مورد", "مقدار سالانه"],
        [
            ["تعداد فروش", "۵۰۰ عدد"],
            ["میانگین قیمت فروش", "۶ میلیون تومان"],
            ["درآمد سالانه", "۳ میلیارد تومان"],
            ["هزینه‌های عملیاتی", "۲ میلیارد تومان"],
            ["سود خالص", "۱ میلیارد تومان"],
            ["حاشیه سود", "۳۳٪"],
        ],
        col_widths=[Cm(8), Cm(8)]
    )
    doc.add_paragraph()
    
    add_heading_rtl(doc, "روش ارزشگذاری درآمدی", size=14, color=GOLD)
    add_paragraph_rtl(doc, "ارزش کسب‌وکار = سود خالز سالانه × ضریب P/E")
    add_paragraph_rtl(doc, "ارزش کسب‌وکار = ۱ میلیارد تومان × ۵ = ۵ میلیارد تومان")
    doc.add_paragraph()
    
    add_heading_rtl(doc, "روش ارزشگذاری بازار", size=14, color=GOLD)
    add_paragraph_rtl(doc, "با توجه به ارزش رقبا و میانگین ضریب‌های بازار:")
    add_bullet_rtl(doc, "هیواهوم: ۶ میلیارد تومان")
    add_bullet_rtl(doc, "کاناپو: ۵.۵ میلیارد تومان")
    add_bullet_rtl(doc, "میانگین بازار: ۵.۷۵ میلیارد تومان")
    doc.add_paragraph()
    
    add_paragraph_rtl(doc, "ارزش کسب‌وکار سناتور: ۵ میلیارد تا ۱۵ میلیارد تومان", bold=True, color=GREEN)
    
    doc.add_page_break()
    
    # === GROWTH POTENTIAL ===
    add_heading_rtl(doc, "پتانسیل رشد", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_heading_rtl(doc, "سناریوهای رشد", size=14, color=GOLD)
    add_table_rtl(doc,
        ["سناریو", "فالوئر (۱ سال)", "درآمد (۱ سال)", "ارزش برند"],
        [
            ["محافظه‌کارانه", "۲,۰۰۰", "۴ میلیارد تومان", "۸۰۰ میلیون تومان"],
            ["واقع‌بینانه", "۵,۰۰۰", "۶ میلیارد تومان", "۱.۵ میلیارد تومان"],
            ["خوش‌بینانه", "۱۰,۰۰۰", "۱۰ میلیارد تومان", "۳ میلیارد تومان"],
            ["رشد سریع", "۵۰,۰۰۰", "۲۰ میلیارد تومان", "۱۰ میلیارد تومان"],
        ],
        col_widths=[Cm(4), Cm(4), Cm(4), Cm(4)]
    )
    doc.add_paragraph()
    
    add_heading_rtl(doc, "عوامل کلیدی رشد", size=14, color=GOLD)
    add_bullet_rtl(doc, "افزایش شناخت برند در بازار هدف")
    add_bullet_rtl(doc, "توسعه محصولات جدید (لوازم خواب، دکوراسیون)")
    add_bullet_rtl(doc, "ورود به بازارهای جدید (شهرهای دیگر)")
    add_bullet_rtl(doc, "توسعه فروش آنلاین و اینستاگرام شاپ")
    add_bullet_rtl(doc, "همکاری با اینفلوئنسرها و برندهای مکمل")
    add_bullet_rtl(doc, "بهینه‌سازی فرآیندهای تولید و کاهش هزینه‌ها")
    
    doc.add_page_break()
    
    # === SWOT ANALYSIS ===
    add_heading_rtl(doc, "تحلیل SWOT", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_table_rtl(doc,
        ["نقاط قوت", "نقاط ضعف"],
        [
            ["برند جدید و تازه", "شناخت پایین برند"],
            ["سبک لوکس و مینیمال", "محدودیت بودجه بازاریابی"],
            ["تمرکز بر کیفیت", "وابستگی به اینستاگرام"],
            ["پتانسیل رشد بالا", "رقابت شدید"],
        ],
        col_widths=[Cm(8), Cm(8)]
    )
    doc.add_paragraph()
    
    add_table_rtl(doc,
        ["فرصت‌ها", "تهدیدها"],
        [
            ["رشد بازار مبلمان لوکس", "ورود رقبای جدید"],
            ["افزایش خرید آنلاین", "تغییر سلیقه مشتریان"],
            ["همکاری با برندهای مکمل", "افزایش هزینه‌های تولید"],
            ["توسعه محصولات جدید", "نوسانات اقتصادی"],
        ],
        col_widths=[Cm(8), Cm(8)]
    )
    
    doc.add_page_break()
    
    # === VALUATION SUMMARY ===
    add_heading_rtl(doc, "خلاصه ارزشگذاری", size=18, color=NAVY)
    doc.add_paragraph()
    
    add_table_rtl(doc,
        ["مورد", "ارزش برآوردی", "روش"],
        [
            ["ارزش برند", "۵۰۰ میلیون تا ۱ میلیارد تومان", "روش درآمدی"],
            ["ارزش پیج اینستاگرام", "۲۰۰ میلیون تا ۵۰۰ میلیون تومان", "روش بازار"],
            ["ارزش کسب‌وکار (سالانه)", "۲ میلیارد تا ۵ میلیارد تومان", "روش درآمدی"],
            ["ارزش کل کسب‌وکار", "۵ میلیارد تا ۱۵ میلیارد تومان", "ترکیبی"],
        ],
        col_widths=[Cm(6), Cm(6), Cm(4)]
    )
    doc.add_paragraph()
    
    add_heading_rtl(doc, "توصیه‌ها", size=14, color=GOLD)
    add_bullet_rtl(doc, "تمرکز بر افزایش شناخت برند")
    add_bullet_rtl(doc, "توسعه کانال‌های فروش جدید")
    add_bullet_rtl(doc, "بهینه‌سازی هزینه‌های عملیاتی")
    add_bullet_rtl(doc, "ایجاد شراکت‌های استراتژیک")
    add_bullet_rtl(doc, "توسعه برند شخصی مدیر")
    
    doc.add_paragraph()
    doc.add_paragraph()
    
    # Footer
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("سناتور | گزارش ارزشگذاری برند")
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = NAVY
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("۱۴۰۵/۰۷/۱۲")
    run.font.name = 'Vazirmatn'
    run.font.size = Pt(10)
    run.font.color.rgb = BLACK
    
    # Save
    output_path = r"C:\Users\Lucifer\Documents\Default Project\senator-valuation.docx"
    doc.save(output_path)
    print(f"Valuation saved to: {output_path}")

if __name__ == "__main__":
    create_valuation()
