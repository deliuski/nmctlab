"""Lab8 Data Cube ба AOI — тайлан (docx) үүсгэх скрипт.
Lab11 тайлангийн нүүр хуудсыг загвар болгон ашиглана.
Ажиллуулах: python build_report.py  (DataCube хавтсаас)
"""
import copy
from pathlib import Path
import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "LAB11" / "Lab11_Report.docx"
OUT = HERE / "Lab8_Report.docx"

LAB_NO = "8"
COURSE = "Өгөгдлийн олборлолт"
TOPIC = "Data Cube ба AOI"
DATE = "2026 он 11 сар 25 өдөр"

FONT = "Times New Roman"
BODY = Pt(12)

d = docx.Document(str(TEMPLATE))
body = d.element.body


# ---------- нүүр хуудас ----------
def set_text_keep_format(par, text):
    runs = par.runs
    if not runs:
        r = par.add_run(text)
        r.font.name = FONT
        return
    runs[0].text = text
    for r in runs[1:]:
        r.text = ""


for p in d.paragraphs[:15]:
    if "ЛАБОРАТОРИЙН ТАЙЛАН" in p.text:
        set_text_keep_format(p, f"ЛАБОРАТОРИЙН ТАЙЛАН №{LAB_NO}")
    if "Гүйцэтгэсэн" in p.text:
        set_text_keep_format(p, f"Гүйцэтгэсэн он сар өдөр：{DATE}")
        date_par = p

cover = d.tables[0]
seen = set()
for row in cover.rows:
    label = row.cells[0].text.strip()
    for cell in row.cells[1:]:
        if id(cell._tc) in seen or cell.text.strip() == label:
            continue
        seen.add(id(cell._tc))
        if label.startswith("Хичээлийн"):
            set_text_keep_format(cell.paragraphs[0], COURSE)
        elif label.startswith("Сэдвийн"):
            set_text_keep_format(cell.paragraphs[0], TOPIC)

# нүүрийн дараах бүх агуулгыг устгана (sectPr-ийг үлдээнэ)
children = list(body)
start = children.index(date_par._p) + 1
for el in children[start:]:
    if el.tag != qn("w:sectPr"):
        body.remove(el)


# ---------- туслах функцууд ----------
def _font(run, size=BODY, bold=None, italic=None, name=FONT):
    run.font.name = name
    run.font.size = size
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(a), name)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def para(text="", bold=False, align=None, indent=True, size=BODY, space_after=4, italic=False):
    p = d.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(0)
    pf.line_spacing = 1.15
    if align is not None:
        pf.alignment = align
    else:
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent:
        pf.first_line_indent = Cm(1.0)
    if text:
        _font(p.add_run(text), size=size, bold=bold, italic=italic)
    return p


def rich(parts, align=None, indent=True):
    """parts: [(text, bold)]"""
    p = para(indent=indent, align=align)
    for t, b in parts:
        _font(p.add_run(t), bold=b)
    return p


def h1(text):
    p = para(text, bold=True, indent=False, space_after=6)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.keep_with_next = True
    return p


def h2(text):
    p = para(text, bold=True, indent=False, space_after=4)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.keep_with_next = True
    return p


def formula(text):
    p = para(indent=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    _font(p.add_run(text))
    return p


def code(text):
    for line in text.strip("\n").split("\n"):
        p = d.add_paragraph()
        pf = p.paragraph_format
        pf.space_after = Pt(0)
        pf.space_before = Pt(0)
        pf.line_spacing = 1.0
        pf.left_indent = Cm(0.5)
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        _font(p.add_run(line if line else " "), size=Pt(9), name="Consolas")
    para("", indent=False, space_after=2)


def _shade(cell, color="EDEDED"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def table(header, rows, widths=None, first_left=True):
    t = d.add_table(rows=1, cols=len(header))
    t.style = d.styles["Table Grid"]
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.text = ""
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if (i == 0 and first_left) else WD_ALIGN_PARAGRAPH.CENTER
        _font(p.add_run(str(h)), size=Pt(10.5), bold=True)
        _shade(c)
    for r in rows:
        cells = t.add_row().cells
        for i, v in enumerate(r):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if (i == 0 and first_left) else WD_ALIGN_PARAGRAPH.CENTER
            _font(p.add_run(str(v)), size=Pt(10.5))
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    para("", indent=False, space_after=2)
    return t


fig_no = [0]


def figure(path, caption, width=15):
    p = para(indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    p.add_run().add_picture(str(HERE / path), width=Cm(width))
    p.paragraph_format.keep_with_next = True
    fig_no[0] += 1
    para(f"Зураг {fig_no[0]}. {caption}", indent=False, align=WD_ALIGN_PARAGRAPH.CENTER,
         size=Pt(10.5), space_after=8)


# ---------- агуулга ----------
h1("1. Зорилго")
para("Data Cube-ийн dimension, measure, cell, cuboid ойлголтыг pandas ашиглан тооцоолж, roll-up, "
     "drill-down, slice, dice, pivot үйлдлүүдийг хийх. Мөн хэмжүүрийг зөв нэгтгэх, AOI аргаар "
     "оюутны өгөгдлийг ерөнхийлөх, flat хүснэгтээс од болон snowflake схем зохиох.")

h1("2. Онол")
para("Data Cube нь өгөгдлийг хэд хэдэн хэмжээсээр харах арга. Dimension нь ямар өнцгөөс харах "
     "(сар, бараа, салбар), measure нь юуг тооцох (орлого), cell нь хэмжээсүүдийн нэг хослолын "
     "утга юм. Жишээ нь (2026-01, Ном, УБ) = 120.")
para("n хэмжээстэй cube-д 2^n cuboid байна. Хэмжээс бүр шатлалтай бол cuboid-ийн тоо:")
formula("T = (L1 + 1)(L2 + 1)...(Ln + 1)")
para("Энд Li нь i-р хэмжээсийн түвшний тоо. Бүх хэмжээстэй cuboid-ийг base, ямар ч хэмжээсгүйг "
     "apex cuboid гэнэ.")
para("Roll-up нь дээд түвшинд нэгтгэх (сараас улирал руу), drill-down нь эсрэгээрээ задлах, slice "
     "нь нэг хэмжээсийн нэг утгыг сонгох, dice нь хэд хэдэн хэмжээсээр шүүх, pivot нь мөр баганыг "
     "солих үйлдэл.")
table(["Ангилал", "Жишээ", "Нэгтгэх арга"], [
    ["Distributive", "SUM, COUNT, MIN, MAX", "Хэсгийн дүнгээс шууд"],
    ["Algebraic", "AVG", "SUM ба COUNT хадгална"],
    ["Holistic", "MEDIAN", "Бүх өгөгдлөөс дахин бодно"],
], widths=[3.5, 5.0, 6.0])
para("AOI нь атрибутын утгыг шатлалаар ерөнхийлж (жишээ нь CS, SE-г Мэдээллийн технологи болгох), "
     "ижил болсон мөрүүдийг нэгтгээд count гаргадаг арга.")

h1("3. Аргачлал")
h2("Од схем ба cuboid")
para("Эхлээд cube_small.csv дээр cell, cuboid-ийг тоолсон. combinations ашиглан 3 хэмжээсийн бүх "
     "дэд олонлогийг гаргаад groupby хийсэн. Дараа нь fact_sales (864 мөр)-ийг dim_month, "
     "dim_product, dim_branch-тай merge хийсэн. Grain нь нэг сар, нэг бараа, нэг салбар.")
figure("figs/fig1_star.png", "Борлуулалтын од схем", width=12)
code('''
dw = (fact.merge(d_mon, on="month_key", validate="many_to_one")
          .merge(d_pro, on="product_key", validate="many_to_one")
          .merge(d_bra, on="branch_key", validate="many_to_one"))
''')
h2("OLAP ба хэмжүүр")
para("Roll-up хийхдээ groupby-ийн баганыг quarter, year, region гэх мэтээр сольсон. Slice, dice-ийг "
     "шүүлтээр, pivot-ийг pivot_table-аар хийсэн. Дунджийг бүх мөрөөр болон бүсүүдийн дундаж "
     "дээрээс хоёр янзаар бодож харьцуулсан.")
h2("AOI")
para("student_id-г хассан. Насыг pd.cut-ээр 20-29, 30-39, 40-49 болгож, мэргэжлийг МТ, Бизнес, "
     "Инженер гэж бүлэглэсэн. Дараа нь groupby().size()-аар count гаргасан.")
code('''
g["age_g"] = pd.cut(g["age"], bins=[19, 29, 39, 49], labels=labels)
aoi = g.groupby(["age_g", "major_g"]).size()
''')
h2("Схем зохиох")
para("cube_payments_flat.csv-ээс drop_duplicates ашиглан dim_date, dim_course, dim_branch гаргаж, "
     "түлхүүр өгөөд fact_payment үүсгэсэн. Snowflake хийхдээ dim_product-оос category-г салгаж "
     "dim_category болгосон. Эцэст нь PK, FK, grain, нийлбэрийг шалгах quality_check функц бичсэн.")

h1("4. Үр дүн")
h2("Cube ба cuboid")
table(["Асуулт", "Хариу"], [
    ["Cell-ийн тоо", "8"],
    ["Нийт орлого", "660"],
    ["УБ, Ном, Ном+УБ", "440, 400, 270"],
    ["Cuboid-ийн тоо", "8"],
    ["Шатлалтай cube", "48 (өдөр нэмбэл 60)"],
], widths=[6.0, 6.0])
para("Бүх 8 cuboid-ийн нийлбэр 660 гарсан, учир нь бүгд нэг өгөгдлийг өөр түвшинд нэгтгэж байгаа.")
h2("Roll-up, drill-down")
para("Холболтын дараа 864 мөр, нийт 36449 хэвээрээ, давхардал 0. 2026 оны орлого 18970 "
     "(2025 онд 17479).")
table(["Түвшин", "Үр дүн"], [
    ["Улирал", "Q1 4908, Q2 4367, Q3 4552, Q4 5143"],
    ["Q4-ийг сараар", "10 сар 1846, 11 сар 1632, 12 сар 1665"],
    ["Бүс", "Төв 9461, Хойд 5419, Баруун 2236, Хангай 1854"],
    ["Улаанбаатар", "УБ 5522 + УБ-2 3939 = 9461"],
], widths=[4.0, 10.0])
para("Хотоор бүлэглэхэд УБ, УБ-2 хоёр нэг хот учир нэг мөр болсон.")
h2("Slice, dice, pivot")
para("2026-01 сарын slice 1380, хамгийн их нь Үүргэвч 480. Dice 8 мөр, нийт 660. Pivot хийгээд "
     "эргүүлэхэд нийлбэр 660 хэвээр.")
table(["Салбар", "Дэвтэр", "Ном"], [
    ["Дархан", "90", "130"],
    ["УБ", "170", "270"],
], widths=[4.0, 3.0, 3.0])
h2("Хэмжүүр")
table(["Тооцоолол", "Зөв", "Буруу"], [
    ["Лекцийн жишээ AVG", "14.62", "20.0"],
    ["Бодит AVG", "42.19", "38.63"],
    ["Median", "20.0", "13.25"],
    ["closing_stock", "3539 (сарын эцэс)", "123048 (SUM)"],
], widths=[5.0, 4.0, 4.0])
para("Дундажийн дундаж буруу гарч байгаа нь бүлгүүдийн мөрийн тоо өөр учраас. Үлдэгдлийг өдрөөр "
     "нэмэхэд нэг барааг олон дахин тоолж байгаа.")
h2("AOI")
para("6 оюутны жишээнд (20-29, МТ) 4 буюу 66.7%, (30-39, Бизнес) 2 буюу 33.3% гарсан. 150 оюутан "
     "дээр 9 мөр гарсан:")
table(["Нас", "Чиглэл", "Count", "Хувь"], [
    ["20-29", "Мэдээллийн технологи", "63", "42.0"],
    ["20-29", "Бизнес", "29", "19.3"],
    ["30-39", "Бизнес", "18", "12.0"],
    ["20-29", "Инженер", "12", "8.0"],
    ["40-49", "Бизнес", "10", "6.7"],
    ["30-39", "Инженер", "7", "4.7"],
    ["40-49", "Мэдээллийн технологи", "6", "4.0"],
    ["30-39", "Мэдээллийн технологи", "3", "2.0"],
    ["40-49", "Инженер", "2", "1.3"],
], widths=[2.5, 5.5, 2.5, 2.5])
figure("figs/fig4_aoi.png", "AOI-ийн үр дүн", width=13)
para("gpa нэмэхэд 20 мөр болсон тул босго 10-аас хэтэрнэ. Тиймээс нас, мэргэжил хоёроор үлдээсэн.")
h2("Схем")
para("Төлбөрийн схемд 467 төлбөр, нийт 101775, өвөрмөц оюутан 160. COUNT(*) нь төлбөрийн тоог "
     "тоолдог болохоос оюутны тоо биш. 2026-03 сард 78 төлбөр, 16463. Хамгийн их хот Улаанбаатар "
     "46885. Чиглэлээр МТ 63493, Бизнес 29597, Хэл 8685.")
para("Snowflake-аар ангиллын орлого (Сургалтын хэрэгсэл 13300, Электрон 3850, Бичиг хэрэг 1820) од "
     "схемтэй ижил гарсан. Чанарын шалгалт бүгд True, fact-ээс 1 мөр хасахад зөвхөн нийлбэрийн "
     "шалгалт False болсон.")
h2("Гараар бодолт")
para("Кодын үр дүнг гараар бодож шалгасан, бүгд таарсан.")
figure("figs/hand_calc.jpg", "Гараар бодолт", width=14)

h1("Дүгнэлт")
para("Энэ лабораториор Data Cube, OLAP үйлдлүүд, AOI-г pandas дээр хийж үзлээ. Хамгийн их анхаарал "
     "татсан нь дундажийн дундаж буруу гардаг явдал байсан, AVG-г SUM, COUNT-оор бодох хэрэгтэй юм "
     "байна. Мөн үлдэгдлийг хугацаагаар нэмж болохгүйг ойлгосон.")

h1("Хавсралт")
para("A. Код: Lab8_DataCube_AOI.ipynb")
para("B. Орчин: Windows 11, Python 3.13, pandas 3.1.1")


d.save(str(OUT))
print("saved", OUT)
