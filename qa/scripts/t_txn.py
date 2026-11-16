"""Invoice (INV) and Receipt (REC) suites. usage: python t_txn.py inv|rec [ids...]"""
from lib import *
import sys
KIND = sys.argv[1]
ONLY = set(sys.argv[2:])
if KIND == "inv":
    P = dict(pre="INV", path="invoice", form="main form[action$='invoice/store']", date="#invoice_date", title="#invoice_title",
             lotitle="#invoice_lo_title", it="ititle", tax="#inv_tax", words="#inv_amount_words", lowords="#inv_lo_amount_words",
             cat="QA Income Cat 02", wrongcat_type="Expense", notes="#invoice_notes", ptype=None, name="Invoice")
else:
    P = dict(pre="REC", path="receipt", form="main form[action$='receipt/store']", date="#payment_date", title="#payment_title",
             lotitle="#payment_lo_title", it="ptitle", tax="#pay_tax", words="#payment_amount_words", lowords="#payment_lo_amount_words",
             cat="QA Expense Cat 01", wrongcat_type="Income", notes="#payment_notes", ptype="#payment_type_id", name="Receipt")
F = P["form"]; PRE = P["pre"]
VENDOR = "QA Vendor Alpha"


def amt(i=0): return f"{F} input[name='amount[{i}]'] >> nth=0"


def total(x):
    t = x.pg.inner_text(F); i = t.find("Total Amount")
    return t[i + 12:i + 40].strip().split("\n")[0].strip()


def base(x, title, category=True, amount="1000", tax="", date=True, vendor=True):
    x.go(f"/{P['path']}/create")
    if category:
        opts = x.pg.eval_on_selector_all("#category_id option", "e=>e.map(o=>o.text.trim())")
        x.pg.select_option("#category_id", label=P["cat"] if P["cat"] in opts else [o for o in opts if o.startswith("QA")][0])
    x.pg.fill(P["title"], title); x.pg.fill(P["lotitle"], "عنوان")
    if vendor: x.pg.select_option("#vendor_id", label=VENDOR)
    if date:
        x.pg.click(P["date"]); time.sleep(0.8); x.pg.click(".ui-datepicker-today a"); time.sleep(0.5)
    x.pg.fill(f"{F} input[name='{P['it']}[0]'] >> nth=0", "Line item 1")
    x.pg.fill(f"{F} input[name='{P['it']}_lo[0]'] >> nth=0", "بند")
    x.pg.fill(amt(), amount); x.pg.press(amt(), "Tab")
    if tax != "": x.pg.fill(P["tax"], tax); x.pg.press(P["tax"], "Tab")
    if P["ptype"]: x.pg.select_option(P["ptype"], label="Cash")
    x.pg.fill(P["words"], "QA amount words"); x.pg.fill(P["lowords"], "كلمات")
    time.sleep(0.5)


def save(x):
    x.pg.click(F + " >> text=Save"); x.settle(3)


def titles(x):
    return [r[2] for r in rows(x) if len(r) > 3]


def listed(x, title):
    x.go(f"/{P['path']}/list"); return [r for r in rows(x) if title in r]


with sync_playwright() as p:
    x = Ctx(p)

    def t01():
        x.go(f"/{P['path']}/create"); t = x.pg.inner_text(F)
        return ("Pass", f"Add {P['name'].lower()} form shows Category, Title, Title(ar), Vendor, Date, line item (title/arabic title/amount, + icon), Tax, Total Amount (INR), Amount in words (en/ar), Notes{', Payment Type, Fetch Invoices toggle' if KIND == 'rec' else ''}, Close, Save. No asterisks on mandatory fields.", x.shot(f"{PRE}-01_form"))

    def t02():
        x.go(f"/{P['path']}/create"); save(x); m = visible_msgs(x, F)
        cat_msg = any("categor" in s.lower() for s in m)
        return ("Pass" if m and "create" in x.pg.url and cat_msg else "Fail", f"Not submitted. Messages: {m}. Category validation message shown: {cat_msg}", x.shot(f"{PRE}-02_empty"))

    def t03():
        base(x, f"QA {P['name']} Valid 01", amount="1000"); tot = total(x); save(x)
        r = listed(x, f"QA {P['name']} Valid 01")
        return ("Pass" if r else "Fail", f"Total shown before save: {tot}. Saved row: {r}", x.shot(f"{PRE}-03_created"))

    def t04():
        base(x, f"QA {P['name']} NoCat", category=False); save(x)
        url, a, m = x.pg.url, x.alert(), visible_msgs(x, F)
        r = listed(x, f"QA {P['name']} NoCat")
        return ("Pass" if not r else "Fail", f"Saved with Category = 'Please select'. URL {url}; alert '{a}'; messages {m}; rows created: {r}", x.shot(f"{PRE}-04_no_category"))

    def t05():
        res = []
        for a_, t_, exp in [("1000", "10", "1100"), ("1000", "0", "1000"), ("100", "18", "118"), ("1000", "5", "1050")]:
            x.go(f"/{P['path']}/create")
            x.pg.fill(amt(), a_); x.pg.press(amt(), "Tab"); x.pg.fill(P["tax"], t_); x.pg.press(P["tax"], "Tab"); time.sleep(0.5)
            res.append((a_, t_ + "%", exp, total(x)))
        ev = x.shot(f"{PRE}-05_tax_calc", False)
        bad = [r for r in res if r[2] not in r[3].replace(",", "")]
        return ("Pass" if not bad else "Fail", "(amount, tax, expected, displayed): " + "; ".join(str(r) for r in res), ev)

    def t06():
        x.go(f"/{P['path']}/create")
        x.pg.fill(amt(0), "500"); x.pg.press(amt(0), "Tab")
        x.pg.click(f"{F} img[title='Add New'] >> nth=0"); time.sleep(1)
        names = x.pg.eval_on_selector_all(f"{F} input[name^='amount']", "e=>e.filter(i=>i.offsetParent!==null).map(i=>i.name)")
        new = [n for n in names if n != "amount[0]"]
        if new:
            x.pg.fill(f"{F} input[name='{new[0]}'] >> nth=0", "300"); x.pg.press(f"{F} input[name='{new[0]}'] >> nth=0", "Tab"); time.sleep(0.5)
        tot = total(x)
        return ("Pass" if new and "800" in tot else "Fail", f"Visible amount inputs after '+': {names}. 500 + 300 -> Total shown {tot}", x.shot(f"{PRE}-06_multi_line"))

    def t07():
        base(x, f"QA {P['name']} Negative", amount="-500"); tot = total(x); save(x)
        r = listed(x, f"QA {P['name']} Negative")
        return ("Pass" if not r else "Fail", f"Amount -500: total displayed {tot}; saved rows {r}", x.shot(f"{PRE}-07_negative"))

    def t08():
        base(x, f"QA {P['name']} Alpha Amt", amount="abc"); tot = total(x); save(x)
        url, a, m = x.pg.url, x.alert(), visible_msgs(x, F); body = x.pg.title()
        r = listed(x, f"QA {P['name']} Alpha Amt")
        return ("Pass" if not r and "Exception" not in body else "Fail", f"Amount 'abc': total {tot}; after save URL {url}, title {body!r}, alert '{a}', messages {m}; rows {r}", x.shot(f"{PRE}-08_alpha_amount"))

    def t09():
        base(x, f"QA {P['name']} Tax150", amount="1000", tax="150"); tot = total(x); save(x)
        r = listed(x, f"QA {P['name']} Tax150")
        return ("Pass" if not r else "Fail", f"Tax 150%: total {tot}; saved rows {r}", x.shot(f"{PRE}-09_tax_150"))

    def t10():
        base(x, f"QA {P['name']} Zero", amount="0"); save(x)
        r = listed(x, f"QA {P['name']} Zero")
        return ("Pass" if not r else "Fail", f"Amount 0 saved rows {r}", "")

    def t11():
        x.go("/category/list")
        wrong = [r[1] for r in rows(x) if len(r) > 2 and r[2] == P["wrongcat_type"]]
        x.go(f"/{P['path']}/create"); o = x.pg.eval_on_selector_all("#category_id option", "e=>e.map(o=>o.text.trim())")
        bad = [w for w in wrong if w in o]
        return ("Pass" if not bad else "Fail", f"Category dropdown {o}; {P['wrongcat_type']} categories wrongly listed: {bad}", x.shot(f"{PRE}-11_cat_dropdown", False))

    def t12():
        x.go(f"/{P['path']}/list"); t = x.main()
        acts = x.pg.eval_on_selector_all("main table tbody tr:first-child td:last-child a, main table tbody tr:first-child td:last-child button", "e=>e.map(a=>(a.className+' '+(a.getAttribute('href')||'')).slice(0,90))")
        return ("Info", f"List header/columns: {t[t.find('#'):t.find('#')+70]!r}. Action controls on first row: {acts}", x.shot(f"{PRE}-12_list"))

    def t13():
        x.go(f"/{P['path']}/list")
        x.pg.locator("main table tbody tr a", has_text=f"QA {P['name']} Valid 01").first.click(); x.settle(3)
        t = x.main()
        return ("Pass" if f"QA {P['name']} Valid 01" in t else "Fail", f"View page {x.pg.url} text: {t[:400]!r}", x.shot(f"{PRE}-13_view"))

    def t14():
        x.go(f"/{P['path']}/list")
        x.pg.fill("#search_term", "Valid 01"); x.pg.click("main >> text=Search"); x.settle(3)
        t = titles(x)
        return ("Pass" if t and all("Valid 01" in v for v in t) else "Fail", f"Search 'Valid 01' -> titles {t}", x.shot(f"{PRE}-14_search"))

    def t15():
        x.go("/")
        t = x.main()
        return ("Info", f"Dashboard after creating {P['name'].lower()}s: {t[:250]!r}", x.shot(f"{PRE}-15_dashboard"))

    def t16():
        x.go(f"/{P['path']}/list")
        with x.pg.expect_download(timeout=150000) as d:
            x.pg.click("main >> text=Export to excel")
        f = d.value
        return ("Pass", f"Export downloaded '{f.suggested_filename}'", "")

    T = [(f"{PRE}-{i:02d}", fn) for i, fn in enumerate([t01, t02, t03, t04, t05, t06, t07, t08, t09, t10, t11, t12, t13, t14, t15, t16], 1)]
    for tid, fn in T:
        if not ONLY or tid in ONLY:
            x.run(tid, fn)
    x.save(KIND)
