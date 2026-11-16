from lib import *
import sys
ONLY = set(sys.argv[1:])
M = "#add-category"


def open_add(x):
    x.go("/category/list"); x.pg.click("#add-cat"); x.pg.wait_for_selector(M + ".show"); time.sleep(0.5)


def fill(x, name=None, lo=None, typ=None):
    if name is not None: x.pg.fill("#category_name", name)
    if lo is not None: x.pg.fill("#category_lo_name", lo)
    if typ is not None: x.pg.select_option("#category_type", typ)


def save(x):
    x.pg.click(M + ".show >> text=Save"); x.settle(2)


def msgs(x):
    return visible_msgs(x, M)


def names(x):
    return [r[1] for r in rows(x) if len(r) > 2]


def cnt(x, n):
    return sum(1 for v in names(x) if v == n)


def open_edit(x, name):
    x.go("/category/list")
    x.pg.locator("main table tbody tr", has_text=name).first.locator("#category_edit").click()
    x.pg.wait_for_selector(M + ".show"); x.settle(1)


with sync_playwright() as p:
    x = Ctx(p)

    def c01():
        open_add(x); txt = x.pg.inner_text(M + ".show"); ev = x.shot("CAT-01_modal", False)
        opts = x.pg.eval_on_selector_all("#category_type option", "e=>e.map(o=>o.text)")
        ok = all(k in txt for k in ["Name", "Arabic Name", "Type", "Save", "Close"])
        return ("Pass" if ok else "Fail", f"Add Category modal opened with Name, Arabic Name, Type (options: {', '.join(opts)}), Close and Save.", ev)

    def c02():
        open_add(x); save(x); m = msgs(x)
        return ("Pass" if len(m) >= 3 else "Fail", f"Form not submitted; inline messages: {m}", x.shot("CAT-02_empty", False))

    def c03():
        open_add(x); fill(x, "QA Income Cat 02", "فئة دخل", "1"); save(x)
        r = [r for r in rows(x) if "QA Income Cat 02" in r]
        return ("Pass" if len(r) == 1 and "Income" in r[0] else "Fail", f"Alert '{x.alert()}'. Row: {r}", x.shot("CAT-03_income_added"))

    def c04():
        open_add(x); fill(x, "QA Expense Cat 01", "فئة مصروف", "2"); save(x)
        r = [r for r in rows(x) if "QA Expense Cat 01" in r]
        return ("Pass" if r and "Expense" in r[0] else "Fail", f"Alert '{x.alert()}'. Row: {r}", x.shot("CAT-04_expense_added"))

    def c05():
        open_add(x); fill(x, "", "عربي", "1"); save(x); m = msgs(x)
        return ("Pass" if any("name" in s.lower() for s in m) else "Fail", f"Messages: {m}", x.shot("CAT-05", False))

    def c06():
        open_add(x); fill(x, "QA NoType Cat", "عربي"); save(x); m = msgs(x); n = cnt(x, "QA NoType Cat")
        return ("Pass" if any("type" in s.lower() for s in m) and n == 0 else "Fail", f"Messages: {m}; rows created={n}", x.shot("CAT-06", False))

    def c07():
        open_add(x); fill(x, "QA NoArabic Cat", "", "1"); save(x); m = msgs(x); n = cnt(x, "QA NoArabic Cat")
        return ("Pass" if m and n == 0 else "Fail", f"Arabic name blank -> messages: {m}; rows created={n}", x.shot("CAT-07", False))

    def c08():
        open_add(x); fill(x, "QA Income Cat 02", "مكرر", "1"); save(x); n = cnt(x, "QA Income Cat 02")
        return ("Pass" if n == 1 else "Fail", f"Duplicate name+type submitted. Alert '{x.alert()}'. Messages {msgs(x)}. Rows named 'QA Income Cat 02' now: {n}", x.shot("CAT-08_duplicate"))

    def c09():
        open_add(x); fill(x, "qa income cat 02", "مكرر", "1"); save(x)
        n = sum(1 for v in names(x) if v.lower() == "qa income cat 02")
        return ("Pass" if n == 1 else "Fail", f"Lower-case duplicate submitted. Alert '{x.alert()}'. Case-insensitive matches: {n}", x.shot("CAT-09_dup_case"))

    def c10():
        open_add(x); fill(x, "     ", "     ", "1"); save(x)
        blank = sum(1 for v in names(x) if v.strip() == "")
        return ("Pass" if blank == 0 else "Fail", f"Whitespace-only name. Messages {msgs(x)}. Alert '{x.alert()}'. Blank-name rows: {blank}", x.shot("CAT-10_whitespace"))

    def c11():
        open_add(x); fill(x, "Q", "ق", "2"); save(x); n = cnt(x, "Q")
        return ("Pass" if n >= 1 else "Fail", f"1-char name. Alert '{x.alert()}'. Rows: {n}", x.shot("CAT-11_min"))

    def c12():
        nm = "QA" + "L" * 253
        open_add(x); fill(x, nm, "ع", "2"); save(x); n = cnt(x, nm)
        return ("Pass" if n == 1 else "Fail", f"255-char name. Alert '{x.alert()}'. Saved intact: {n == 1}. Title: {x.pg.title()!r}", x.shot("CAT-12_255"))

    def c13():
        nm = "QA" + "M" * 254
        open_add(x); fill(x, nm, "ع", "2"); save(x)
        title = x.pg.title(); body = x.pg.inner_text("body")[:250]
        saved = [len(v) for v in names(x) if v.startswith("QAMMM")] if "main" in x.pg.content() else []
        return ("Pass" if not saved and "Exception" not in body else "Fail", f"256-char name. Page title {title!r}. Saved lengths {saved}. Body: {body[:200]!r}", x.shot("CAT-13_256"))

    def c14():
        nm = "<script>alert('xss')</script>QA"
        open_add(x); fill(x, nm, "ع", "1"); save(x)
        return ("Pass" if not any("xss" in d for d in x.dialogs) else "Fail", f"Script in name. JS dialogs fired: {x.dialogs}. Rendered as literal text: {nm in names(x)}", x.shot("CAT-14_xss"))

    def c15():
        open_edit(x, "QA Expense Cat 01")
        vals = [x.pg.input_value("#category_name"), x.pg.input_value("#category_lo_name"), x.pg.input_value("#category_type")]
        x.shot("CAT-15_edit_prefill", False)
        x.pg.fill("#category_name", "QA Expense Cat 01 Edited"); save(x)
        a, b = cnt(x, "QA Expense Cat 01"), cnt(x, "QA Expense Cat 01 Edited")
        return ("Pass" if b == 1 and a == 0 and vals[0] == "QA Expense Cat 01" else "Fail", f"Edit modal prefilled {vals}. Alert '{x.alert()}'. old-name rows={a}, new-name rows={b}", x.shot("CAT-15_edited"))

    def c16():
        open_edit(x, "QA Expense Cat 01 Edited"); x.pg.fill("#category_name", ""); save(x); m = msgs(x)
        x.go("/category/list"); n = cnt(x, "QA Expense Cat 01 Edited")
        return ("Pass" if m and n == 1 else "Fail", f"Name blanked in edit. Messages {m}. Original still present: {n}", "")

    def c17():
        open_edit(x, "QA Expense Cat 01 Edited")
        x.pg.fill("#category_name", "QA Income Cat 02"); x.pg.select_option("#category_type", "1"); save(x)
        n = cnt(x, "QA Income Cat 02")
        return ("Pass" if n == 1 else "Fail", f"Edited category renamed to existing 'QA Income Cat 02'/Income. Alert '{x.alert()}'. Rows with that name: {n}", x.shot("CAT-17_edit_dup"))

    def c18():
        x.go("/category/list"); before = len(names(x)); x.dialog_accept = False
        x.pg.locator("main table tbody tr", has_text="QA NoArabic Cat").first.locator("a.btn-danger").click() if cnt(x, "QA NoArabic Cat") else x.pg.locator("main table tbody tr", has_text="Q").last.locator("a.btn-danger").click()
        x.settle(2); after = len(names(x))
        return ("Pass" if before == after and x.dialogs else "Fail", f"Confirm '{x.dialogs}' dismissed. Rows before={before}, after={after}", "")

    def c19():
        x.go("/category/list"); before = cnt(x, "QA Income Cat 01")
        x.pg.locator("main table tbody tr", has_text="QA Income Cat 01").first.locator("a.btn-danger").click(); x.settle(3)
        after = cnt(x, "QA Income Cat 01")
        return ("Pass" if before == 1 and after == 0 else "Fail", f"Confirm '{x.dialogs}' accepted. Alert '{x.alert()}'. Rows before={before}, after={after}", x.shot("CAT-19_deleted"))

    def cat_types():
        x.go("/category/list"); r = rows(x)
        return [a[1] for a in r if len(a) > 2 and a[2] == "Income"], [a[1] for a in r if len(a) > 2 and a[2] == "Expense"]

    def c20():
        inc, exp = cat_types(); x.go("/invoice/create")
        o = x.pg.eval_on_selector_all("#category_id option", "e=>e.map(o=>o.text.trim())")
        bad = [e for e in exp if e in o]
        return ("Pass" if not bad and any(i in o for i in inc) else "Fail", f"Invoice Category dropdown: {o}. Expense categories present: {bad}", x.shot("CAT-20_invoice_dropdown", False))

    def c21():
        inc, exp = cat_types(); x.go("/receipt/create")
        o = x.pg.eval_on_selector_all("#category_id option", "e=>e.map(o=>o.text.trim())")
        bad = [i for i in inc if i in o]
        return ("Pass" if not bad and any(e in o for e in exp) else "Fail", f"Receipt Category dropdown: {o}. Income categories present: {bad}", x.shot("CAT-21_receipt_dropdown", False))

    def c22():
        x.go("/category/list")
        return ("Info", f"List page text: {x.main()[:300]!r}", x.shot("CAT-22_list"))

    T = [("CAT-01", c01), ("CAT-02", c02), ("CAT-03", c03), ("CAT-04", c04), ("CAT-05", c05), ("CAT-06", c06),
         ("CAT-07", c07), ("CAT-08", c08), ("CAT-09", c09), ("CAT-10", c10), ("CAT-11", c11), ("CAT-12", c12),
         ("CAT-13", c13), ("CAT-14", c14), ("CAT-15", c15), ("CAT-16", c16), ("CAT-17", c17), ("CAT-18", c18),
         ("CAT-19", c19), ("CAT-20", c20), ("CAT-21", c21), ("CAT-22", c22)]
    for tid, fn in T:
        if not ONLY or tid in ONLY:
            x.run(tid, fn)
    x.save("category")
