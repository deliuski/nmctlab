"""Lab9 Cube space — тайлан (docx) үүсгэх скрипт.
Lab11 тайлангийн нүүр хуудсыг загвар болгон ашиглана.
Ажиллуулах: python build_report.py  (Lab9_CubeSpace хавтсаас)
"""
import subprocess
from pathlib import Path
import docx
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "LAB11" / "Lab11_Report.docx"
OUT = HERE / "Lab9_Report.docx"

LAB_NO = "9"
COURSE = "Өгөгдлийн олборлолт"
TOPIC = "Cube space"
DATE = "2026 он 11 сар 26 өдөр"

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


date_par = None
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
    pf.alignment = align if align is not None else WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent:
        pf.first_line_indent = Cm(1.0)
    if text:
        _font(p.add_run(text), size=size, bold=bold, italic=italic)
    return p


def h1(text, new_page=False):
    p = para(text, bold=True, indent=False, space_after=6)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.page_break_before = new_page
    return p


def h2(text):
    p = para(text, bold=True, indent=False, space_after=4)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.keep_with_next = True
    return p


def formula(text):
    p = para(indent=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    _font(p.add_run(text), italic=True)
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


# =====================================================================
h1("1. Зорилго", new_page=True)
para("Энэ лабораторийн ажлаар cube space-ийн үндсэн ойлголтуудыг (cell, cuboid, concept hierarchy, "
     "measure) pandas болон SQLite ашиглан кодоор хэрэгжүүлэх зорилготой. Мөн materialization, "
     "Iceberg cube, BUC, closed cell, ROLAP ба MOLAP-ийг туршиж, discovery-driven exploration болон "
     "prediction cube-ээр cube дотор mining хийв.")

h1("2. Онол")
para("Cube-ийн нэг мөрийг cell гэнэ. Бүх dimension утгатай бол base cell, зарим нь * бол aggregate "
     "cell, бүгд * бол apex cell болно. Илүү ерөнхий cell-ийг ancestor, илүү нарийвчилсныг descendant "
     "гэнэ. Dimension-ы дэд олонлог бүр нэг cuboid болох тул n dimension-д 2ⁿ cuboid, шатлалтай үед:")
formula("T = ∏ (Lᵢ + 1)")
para("Lᵢ нь i-р dimension-ийн түвшний тоо, +1 нь all түвшин. Хэмжүүрийг хэсгээс нэгтгэж болох эсэхээр "
     "нь гурав ангилна.")
table(["Төрөл", "Жишээ", "Хэсгээс нийтийг олох"], [
    ["Distributive", "sum, count, min, max", "Хэсгийн үр дүнгээр шууд"],
    ["Algebraic", "avg, stddev, max_N", "Хэдэн distributive утгаар (sum, count г.м.)"],
    ["Holistic", "median, mode, rank", "Боломжгүй, бүх утга хэрэгтэй"],
], widths=[3.0, 4.6, 7.6])
para("Бүх cuboid-ийг хадгалахыг full, огт хадгалахгүйг no, заримыг нь хадгалахыг partial "
     "materialization гэнэ. Iceberg cube нь COUNT ≥ min_sup байх cell-үүдийг л хадгална. Нэг cell "
     "босго давахгүй бол түүний descendant ч давахгүй (antimonotonicity) тул BUC тэр салбарыг prune "
     "хийдэг. Closed cell-үүдээс тогтсон cube-ийг quotient cube гэнэ.")
para("ROLAP нь relational хүснэгт, MOLAP нь олон хэмжээст массив ашигладаг, HOLAP хоёуланг нь "
     "хослуулна. SelfExp нь cell өөрөө хэр онцгой, InExp нь доор нь онцгой утга байгаа эсэхийг заана. "
     "Prediction cube нь cell бүрт загварын accuracy-г хадгална.")

# =====================================================================
h1("3. Аргачлал", new_page=True)
h2("Өгөгдөл")
para("cs_sales.csv-г cs_dim_item, cs_dim_location-тэй merge хийж 3000 мөртэй df гаргав (нийт "
     "борлуулалт 2602025). Жижиг жишээнүүдэд cs_coffee_mini, cs_iceberg_demo, cs_closed_demo-г ашиглав.")

h2("Cube ба GROUP BY CUBE")
para("cube_groupby нь dimension-ы бүх дэд олонлогоор groupby хийгээд бүлэглээгүй баганад NaN тавьж "
     "нэгтгэнэ. SQLite CUBE-г дэмждэггүй тул 4 SELECT-ийг UNION ALL-аар нийлүүлж шалгав.")
code('''
def cube_groupby(df, dims, measure, agg="sum"):
    parts = []
    for k in range(len(dims), -1, -1):
        for sub in combinations(dims, k):
            if sub:
                g = df.groupby(list(sub), as_index=False)[measure].agg(agg)
            else:
                g = pd.DataFrame({measure: [df[measure].agg(agg)]})
            for d in dims:
                if d not in sub:
                    g[d] = np.nan
            parts.append(g[dims + [measure]])
    return pd.concat(parts, ignore_index=True)
''')
figure("figs/fig1_lattice.png", "time, item, location, supplier 4 dimension-ийн 16 cuboid-ийн lattice", width=15)

h2("Cuboid сонгох ба materialization")
para("can_answer нь dimension бүрт materialized cuboid-ийн түвшин query-ийнхээс нарийн эсвэл тэнцүү "
     "эсэхийг шалгана. Materialization-д query-ийн өртгийг түүнийг хариулж чадах хамгийн жижиг "
     "cuboid-ийн мөрийн тоо гэж аваад greedy аргаар 2 cuboid сонгов.")

h2("Iceberg cube ба BUC")
para("buc нь apex-ээс эхэлж dimension бүрээр хуваана. Хэсгийн мөрийн тоо min_sup-аас бага бол доош "
     "явахгүй (prune). Үр дүнг бүтэн CUBE-ээс шүүсэнтэй харьцуулав.")
code('''
def buc(df, dims, min_sup):
    out, pruned = [], []
    n_part = 0
    def rec(part, prefix, start):
        nonlocal n_part
        out.append((prefix, len(part)))
        for i in range(start, len(dims)):
            for v, sub in part.groupby(dims[i], sort=True):
                n_part += 1
                cell = prefix[:i] + (v,) + prefix[i + 1:]
                if len(sub) >= min_sup:
                    rec(sub, cell, i + 1)
                else:
                    pruned.append((cell, len(sub)))
    if len(df) >= min_sup:
        rec(df, ("*",) * len(dims), 0)
    return out, pruned, n_part
''')
figure("figs/fig2_buc.png", "cs_iceberg_demo дээрх BUC-ийн мод (min_sup = 3)", width=15)

h2("Closed cell")
para("Cell бүрийн хамарсан мөрийн индексийг (cover) frozenset болгов. Ижил cover-тэй descendant "
     "байвал тэр cell closed биш.")
code('''
def covers(cell):
    m = np.ones(len(cd), dtype=bool)
    for d, v in zip(dims_c, cell):
        if v != "*":
            m &= (cd[d] == v).values
    return frozenset(int(i) for i in np.flatnonzero(m))

def is_closed(cell):
    return not any(is_ancestor(cell, o) and cov[o] == cov[cell]
                   for o in cell_list)
''')

h2("ROLAP ба MOLAP")
para("ROLAP-д SQLite дээр GROUP BY city, month хийв. MOLAP-д 8 × 6 × 6 numpy массив үүсгээд item "
     "тэнхлэгээр sum хийж, хоёр үр дүнг харьцуулав.")

h2("SelfExp ба InExp")
para("Барааны сарын өөрчлөлтийг (%) бодоод, хүлээгдэх утгыг мөрийн дундаж + баганын дундаж − нийт "
     "дундаж гэж үлдэгдлийг стандартчилав. InExp-д хотын өөрчлөлтөөс улсын өөрчлөлтийг хасаж "
     "стандартчилав.")
code('''
chg = ((nat / nat.shift(1, axis=1) - 1) * 100).loc[:, 1:6]
row_m = chg.mean(axis=1).to_numpy()[:, None]
col_m = chg.mean(axis=0).to_numpy()[None, :]
expv = row_m + col_m - chg.to_numpy().mean()
resid = chg - expv
z_self = resid / resid.stack().std()

cchg = ((cm / cm.shift(1, axis=1) - 1) * 100).loc[:, 1:6]
diff = cchg - chg.reindex(cchg.index.get_level_values("item")).to_numpy()
z_in = diff / diff.stack().std()
in_max = z_in.abs().groupby(level="item").max()
''')

h2("Prediction cube")
para("(city, year) cell бүр дээр logistic regression-ийг 5-fold cross validation-ээр сургаж accuracy "
     "гаргав. Дараа нь gender нэмж зөрүүг gender_gain гэж бодов.")
code('''
def cell_acc(g, feats):
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    cv = KFold(n_splits=5, shuffle=True, random_state=0)
    return cross_val_score(model, g[feats], g["approved"], cv=cv,
                           scoring="accuracy").mean()
''')

# =====================================================================
h1("4. Үр дүн", new_page=True)
para("TASK 1-13-ын гол үр дүнг доорх хүснэгтэд нэгтгэв. Дэлгэрэнгүйг дараагийн хэсгүүдэд үзүүлэв.")
table(["TASK", "Сэдэв", "Гол үр дүн"], [
    ["1", "Мини куб", "Apex 600, 8 cuboid; хамгийн их өсөлт (Дархан, Кофе) +30%"],
    ["2", "Cell", "27 cell; (УБ, Q1, Кофе)-д 7 ancestor, (УБ, *, *)-д 8 descendant"],
    ["3", "Cuboid-ийн тоо", "16; 24; 60 466 176; манай схем 96"],
    ["4", "GROUP BY CUBE", "49 мөр (36 + 6 + 6 + 1), SQL-тэй ижил"],
    ["5", "Концепцийн шатлал", "Монгол 1887750, Хятад 714275; 4 долоо хоног 2 сард хамаарна"],
    ["6", "Measure", "avg зөв 867.34, буруу 921.34; median 600 ≠ 900"],
    ["7", "Cuboid сонголт", "Q1 → (month, city) 36; Q2 → (month, city, item) 288; Q3 → 2"],
    ["8", "Materialization", "Full 441 / 55.1; No 288 / 288; Partial 372 / 102"],
    ["9", "Iceberg, BUC", "Demo: 7 cell, 2 prune; d4: 310 / 1636 cell, BUC = CUBE"],
    ["10", "Closed cell", "12 / 25 closed (0.48); shell fragment 6 cuboid"],
    ["11", "ROLAP, MOLAP", "Үр дүн ижил; хоосон биш cell 7.24%"],
    ["12", "SelfExp, InExp", "Чихэвч 5-р сар 2.82; Принтер 4-р сар Ховд InExp 10.56"],
    ["13", "Prediction cube", "Ховд хамгийн сул 0.652; Эрдэнэт gender +0.05"],
], widths=[1.4, 3.6, 10.2])
h2("Мини куб, cell, cuboid (TASK 1-3)")
table(["Асуулт", "Үр дүн"], [
    ["Roll-up: салбараар", "УБ 400, Дархан 200"],
    ["Slice: Q2 (салбар × бараа)", "УБ: Кофе 150, Цай 70; Дархан: Кофе 65, Цай 45"],
    ["Dice: УБ, Кофе", "Q1 120, Q2 150"],
    ["Apex (*, *, *)", "600"],
    ["Cuboid-ийн тоо", "2³ = 8"],
    ["Exception (Q1 → Q2)", "(Дархан, Кофе) +30.0%, дараа нь (УБ, Кофе) +25.0%"],
    ["Бүх cell", "27 = (2+1)(2+1)(2+1)"],
    ["(УБ, Q1, Кофе)-ийн ancestor", "7"],
    ["(УБ, *, *)-ийн descendant", "8 (4 aggregate, 4 base)"],
], widths=[5.5, 9.7])
para("Жишээ 3.9-ийн 5 cell зөв ангилагдсан. Дүнгээрээ УБ-ийн Кофе хамгийн их боловч хувиараа "
     "Дархан-ы Кофе хамгийн их өссөн.")
table(["Тохиолдол", "Тооцоо", "Cuboid"], [
    ["4 dimension, hierarchy-гүй", "1 + 4 + 6 + 4 + 1", "16"],
    ["Лекцийн жишээ (3, 2, 1)", "4 · 3 · 2", "24"],
    ["10 dimension × 5 түвшин", "6¹⁰", "60 466 176"],
    ["Манай схем (3, 3, 2, 1)", "4 · 4 · 3 · 2", "96"],
], widths=[5.5, 5.0, 4.7])
para("10 dimension-д 60 сая гаруй cuboid гарах тул бүгдийг урьдчилан тооцох боломжгүй.")

h2("GROUP BY CUBE ба концепцийн шатлал (TASK 4-5)")
para("CUBE 49 мөр гарсан (36 + 6 + 6 + 1). Apex нь нийт борлуулалт 2602025-тай тэнцүү, SQLite-ийн "
     "UNION ALL-ийн үр дүн ч ижил.")
table(["Түвшин", "Борлуулалт"], [
    ["Улс", "Монгол 1887750, Хятад 714275"],
    ["Хот (Монгол)", "Улаанбаатар 1131800, Дархан 333200, Эрдэнэт 272875, Ховд 149875"],
    ["Хот (Хятад)", "Бээжин 472975, Шанхай 241300"],
    ["Дүүрэг (Улаанбаатар)", "Сүхбаатар 429450, Хан-Уул 393525, Баянзүрх 308825"],
    ["Улирал", "Q1 1283550, Q2 1318475"],
], widths=[4.5, 10.7])
para("Улсын нийлбэр хотуудынхтай, хотынх дүүргүүдийнхтэй тэнцсэн. 4 долоо хоног (5, 9, 14, 18) хоёр "
     "сард хамаарч байгаа тул week ба month хэсэгчилсэн дараалалтай.")
table(["Интервал (200)", "Бараа", "Борлуулалт", "Интервал (100)", "Бараа", "Борлуулалт"], [
    ["(0, 200]", "4", "427125", "(0, 100]", "3", "221125"],
    ["", "", "", "(100, 200]", "1", "206000"],
    ["(200, 400]", "2", "997700", "(200, 300]", "1", "327300"],
    ["", "", "", "(300, 400]", "1", "670400"],
    ["(400, 600]", "1", "502000", "(400, 500]", "1", "502000"],
    ["(600, 800]", "1", "675200", "(700, 800]", "1", "675200"],
], widths=[2.8, 1.6, 2.4, 2.8, 1.6, 2.4], first_left=False)
para("Үнэ нь яг 200 байгаа Принтер right=True учир (0, 200] интервалд орсон.")

h2("Хэмжүүрийн нэгтгэл (TASK 6)")
table(["Тооцоо", "Хэсгээс", "Бүтнээр", "Тэнцүү эсэх"], [
    ["Лекц: sum", "60 + 90 = 150", "150", "Тийм"],
    ["Лекц: avg", "(20 + 45) / 2 = 32.5", "30.0", "Үгүй"],
    ["Лекц: avg (sum, count)", "150 / 5 = 30.0", "30.0", "Тийм"],
    ["Лекц: median", "median(20, 45) = 32.5", "30.0", "Үгүй"],
    ["sales avg (type-ийн дундажийн дундаж)", "921.34", "867.34", "Үгүй"],
    ["sales avg (sum, count)", "867.34", "867.34", "Тийм"],
    ["sales std (n, Σx, Σx²)", "858.23", "858.23", "Тийм"],
    ["sales median", "900", "600", "Үгүй"],
    ["sales top 3", "4000, 4000, 4000", "4000, 4000, 4000", "Тийм"],
], widths=[5.6, 3.8, 3.3, 2.5])
para("Дундажуудын дундаж бүлэг бүрд ижил жин өгдөг тул буруу (921.34) гарсан. median нь holistic тул "
     "хэсгээс бодож болохгүй.")

h2("Cuboid сонголт ба materialization (TASK 7-8)")
table(["Query", "Хариулж чадах cuboid (мөр)", "Сонгосон"], [
    ["(month, country, None)", "day-district-item 2616, month-city-item 288, month-city 36, month-country-item 96",
     "(month, city, None), 36"],
    ["(year, city, type)", "day-district-item 2616, month-city-item 288", "(month, city, item), 288"],
    ["(None, None, None)", "бүх 5 cuboid", "(year, country, None), 2"],
], widths=[3.6, 7.6, 4.0])
para("Q2-ыг (month, city, None) хариулж чадахгүй, учир нь тэнд item аль хэдийн all болсон.")
table(["Cuboid", "Мөр", "Cuboid", "Мөр"], [
    ["(item, city, month)", "288", "(item)", "8"],
    ["(item, city)", "48", "(city)", "6"],
    ["(item, month)", "48", "(month)", "6"],
    ["(city, month)", "36", "apex", "1"],
], widths=[4.4, 2.2, 4.4, 2.2])
figure("figs/fig3_materialization.png", "Full, No, Partial materialization-ийн хадгалалт ба дундаж өртөг", width=15)
para("Greedy эхлээд (city, month), дараа нь (item, city)-г сонгосон. Partial нь Full-ээс бага зай "
     "эзэлж, No-оос 2.8 дахин хурдан. Зөвхөн 3 cuboid хадгалах нь partial materialization юм.")

h2("Iceberg cube ба BUC (TASK 9)")
para("Demo өгөгдөлд min_sup = 3 үед 9 cell-ээс 7 үлдэж, (Ном, Дархан) ба (Дэвтэр, Дархан) prune "
     "болсон (Зураг 2).")
table(["Үзүүлэлт (d4, min_sup = 30)", "Утга"], [
    ["BUC = CUBE-ээс шүүсэн", "True"],
    ["Iceberg cell", "310"],
    ["Хянасан partition", "1135"],
    ["Prune хийсэн cell", "826"],
    ["Бүтэн cube-ийн cell", "1636"],
    ["Antimonotonicity", "True"],
], widths=[7.0, 4.0])
para("1636 cell-ээс 310 нь л үлдсэн.")

h2("Closed cell ба shell fragment (TASK 10)")
para("25 cell-ээс 12 нь closed. (Дархан, *, *) closed биш, учир нь (Дархан, Q1, *) яг ижил мөрүүдийг "
     "хамарна.")
table(["Closed cell", "Cover", "Closed cell", "Cover"], [
    ["(Дархан, Q1, Кофе)", "{0}", "(УБ, Q2, *)", "{2, 3}"],
    ["(Дархан, Q1, Цай)", "{1}", "(УБ, *, Цай)", "{3, 4}"],
    ["(УБ, Q2, Кофе)", "{2}", "(УБ, *, *)", "{2, 3, 4}"],
    ["(УБ, Q2, Цай)", "{3}", "(*, *, Кофе)", "{0, 2}"],
    ["(УБ, Q3, Цай)", "{4}", "(*, *, Цай)", "{1, 3, 4}"],
    ["(Дархан, Q1, *)", "{0, 1}", "(*, *, *)", "{0, 1, 2, 3, 4}"],
], widths=[4.3, 2.8, 4.3, 3.2])
para("Quotient cube 12 / 25 = 0.48. Shell fragment-д 6 cuboid тооцох бол бүтэн cube-д 15.")

h2("ROLAP ба MOLAP (TASK 11)")
para("ROLAP ба MOLAP-ийн үр дүн ижил гарсан (np.allclose = True). district × item × day × "
     "customer_group-ийн dense массивын 39096 cell-ээс 2829 (7.24%) нь л утгатай тул MOLAP их зай "
     "үрнэ. HOLAP нягт хэсгийг массивт, сийрэг хэсгийг хүснэгтэд хадгалж үүнийг шийддэг.")

h2("Discovery-driven exploration (TASK 12)")
table(["Бараа", "1-р сар", "2-р сар", "3-р сар", "4-р сар", "5-р сар", "6-р сар"], [
    ["Ноутбук", "2.0", "3.0", "1.0", "4.0", "2.0", "3.0"],
    ["Принтер", "-1.0", "0.1", "0.9", "-2.0", "0.1", "0.9"],
    ["Утас", "1.0", "2.0", "-14.0", "2.0", "1.0", "3.0"],
    ["Чихэвч", "2.9", "2.2", "3.9", "1.0", "22.0", "2.0"],
], widths=[2.6, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1])
para("SelfExp хамгийн өндөр нь Чихэвч 5-р сар (2.82), Утас 3-р сар (2.23). InExp хамгийн өндөр нь "
     "Принтер 4-р сар, Ховд хот (10.56).")
figure("figs/fig4_exceptions.png", "SelfExp ба InExp-ийн |z| утга (бараа × сар)", width=16)
para("Принтер 4-р сар улсаараа −2.0% тул энгийн харагдсан ч Ховд хотод 35% орчим унасан (Зураг 5). "
     "Чихэвч 5-р сар бол бүх хотод хамт өссөн тул InExp бага.")
figure("figs/fig5_printer.png", "Принтерийн хотын борлуулалтын индекс, Ховд хот тодоор", width=14)

h2("Prediction cube (TASK 13)")
table(["Хот", "n", "acc 2024", "acc 2025", "acc 2026", "gain 2024", "gain 2025", "gain 2026"], [
    ["Дархан", "200", "0.840", "0.810", "0.870", "+0.005", "0.000", "−0.010"],
    ["Улаанбаатар", "300", "0.887", "0.900", "0.893", "0.000", "−0.007", "+0.003"],
    ["Ховд", "90", "0.622", "0.622", "0.711", "+0.067", "−0.022", "−0.056"],
    ["Эрдэнэт", "200", "0.845", "0.795", "0.855", "+0.005", "+0.050", "+0.055"],
], widths=[2.8, 1.2, 1.7, 1.7, 1.7, 1.8, 1.8, 1.8])
para("Ховд хамгийн муу (дундаж 0.652), учир нь cell бүрт 90 мөр л байна. Эрдэнэт-д gender нэмэхэд "
     "accuracy өссөн, Ховд-д тогтворгүй. Gender нөлөөтэй байгаа нь өмнөх шийдвэрүүд хүйсээр "
     "ялгаварласан байж болзошгүйг харуулах тул fairness-ийг анхаарах хэрэгтэй.")

h2("Гараар бодолт ба кодын тулгалт")
hp = para("Кодын гаргасан зарим утгыг гараар бодож шалгав. Бүх утга notebook-ийн гаралттай тохирсон.")
hp.paragraph_format.keep_with_next = True
hp.paragraph_format.keep_together = True
figure("figs/hand_calc.jpg", "Гараар бодсон тооцоо", width=12.5)

# =====================================================================
h1("Дүгнэлт", new_page=True)
para("Энэ лабораторийн ажлаар cube нь dimension-ы бүх хослолоор нэгтгэсэн cuboid-уудаас тогтдог "
     "гэдгийг ойлголоо. GROUP BY CUBE-ийг өөрөө бичиж SQL-тэй харьцуулснаар CUBE хэрхэн ажилладгийг "
     "мэдэж авлаа.")
para("Хамгийн хэцүү нь BUC болон InExp байсан. BUC-ийн рекурсийг эхлээд жижиг жишээн дээр гараар "
     "зурж шалгаад дараа нь том өгөгдөл дээр ажиллуулсан. Antimonotonicity гэдэг нь cell-ийг "
     "нарийвчлах тусам мөрийн тоо нь өсөхгүй гэсэн үг тул босго давахгүй cell-ийн доошхийг тооцох "
     "шаардлагагүй.")
para("Бүх cuboid-ийг тооцоход хэт их зай, хугацаа шаардлагатай тул Iceberg, closed cell, partial "
     "materialization хэрэгтэй гэдгийг тоогоор харлаа. Discovery-driven exploration-ийг жишээ нь "
     "сургуулийн дүнгийн өгөгдөлд ашиглаж, нийтдээ хэвийн ч аль нэг анги дээр унасан дүнг олж болно.")

h1("Хавсралт")
para("A. Бүрэн код ба өгөгдөл: Lab9_CubeSpace.ipynb (TASK 1-13), figs.py (зургууд), build_report.py; "
     "cs_coffee_mini.csv, cs_sales.csv, cs_dim_item.csv, cs_dim_location.csv, cs_iceberg_demo.csv, "
     "cs_closed_demo.csv, cs_monthly_item_city.csv, cs_loans.csv.")
para("B. Git log:")
try:
    log = subprocess.run(["git", "log", "--oneline", "-6"], cwd=HERE, capture_output=True,
                         text=True, encoding="utf-8").stdout.strip()
except Exception:
    log = ""
if log:
    code(log)
para("C. Туршилтын орчин: Windows 11, Python 3.14.5, pandas 3.0.6, NumPy 2.5.3, scikit-learn 1.9.1, "
     "Matplotlib 3.11.2, SQLite (Python-ийн sqlite3).")
para("D. GitHub: https://github.com/deliuski/nmctlab")

d.save(str(OUT))
print("saved", OUT)
