from lib import *
import sys, base64
ONLY = set(sys.argv[1:])
DATA = os.path.join(HERE, "..", "testdata"); os.makedirs(DATA, exist_ok=True)
PNG = os.path.join(DATA, "qa_logo.png")
open(PNG, "wb").write(base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAAHUlEQVR4nGNgGAWjYBSMglEwCkbBKBgFo2AUDAQAB5AAAeVY5dEAAAAASUVORK5CYII="))
TXT = os.path.join(DATA, "not_an_image.txt"); open(TXT, "w").write("plain text, not an image")


def fill(x, name="", lo="", phone="", email="", addr="", loaddr="", logo=None):
    x.pg.fill("#vendor_name", name); x.pg.fill("#vendor_lo_name", lo)
    x.pg.fill("#vendor_phone", phone); x.pg.fill("#vendor_email", email)
    x.pg.fill("#vendor_address", addr); x.pg.fill("#vendor_lo_address", loaddr)
    if logo: x.pg.set_input_files("input[name=ven_file]", logo)


def save(x):
    x.pg.click("main >> text=Save"); x.settle(3)


def msgs(x):
    return visible_msgs(x, "main")


def names(x):
    return [r[2] for r in rows(x) if len(r) > 3]


def cnt(x, n):
    x.go("/vendor/list"); return sum(1 for v in names(x) if v == n)


def create(x, **kw):
    x.go("/vendor/create"); fill(x, **kw); save(x)
    return x.pg.url, x.alert(), msgs(x)


with sync_playwright() as p:
    x = Ctx(p)

    def v01():
        x.go("/vendor/create"); t = x.main()
        ok = all(k in t for k in ["Name", "Name (ar)", "Phone", "Email", "Address", "Logo", "Save", "Close"])
        return ("Pass" if ok else "Fail", "Add Vendor page shows Name, Name (ar), Phone, Email, Address, Address (ar), Logo upload, Close, Save. No asterisk marks the mandatory fields.", x.shot("VEN-01_form"))

    def v02():
        x.go("/vendor/create"); save(x); m = msgs(x)
        return ("Pass" if len(m) >= 2 and "create" in x.pg.url else "Fail", f"Stayed on {x.pg.url}; messages {m}", x.shot("VEN-02_empty"))

    def v03():
        u, a, m = create(x, name="QA Vendor Beta", lo="مورد بيتا", phone="9876500001", email="qa.beta@example.com", addr="1 QA Road, Kochi", loaddr="عنوان", logo=PNG)
        r = [r for r in rows(x) if "QA Vendor Beta" in r]
        imgs = x.pg.eval_on_selector_all("main table tbody tr img", "e=>e.map(i=>[i.getAttribute('src'),i.naturalWidth])")
        return ("Pass" if r else "Fail", f"Redirected to {u}; alert '{a}'; row {r}; logo img(src,naturalWidth)={imgs}", x.shot("VEN-03_added"))

    def v04():
        u, a, m = create(x, name="QA Vendor Min", lo="حد أدنى")
        return ("Pass" if "list" in u and "QA Vendor Min" in names(x) else "Fail", f"Only mandatory fields filled. URL {u}; alert '{a}'; messages {m}", x.shot("VEN-04_min"))

    def v05():
        u, a, m = create(x, name="QA Vendor BadEmail", lo="بريد", email="abc@", phone="9876500002")
        n = cnt(x, "QA Vendor BadEmail")
        return ("Pass" if n == 0 else "Fail", f"Email 'abc@' submitted. URL after save {u}; alert '{a}'; messages {m}; vendor rows created={n}", x.shot("VEN-05_bad_email"))

    def v06():
        u, a, m = create(x, name="QA Vendor BadPhone", lo="هاتف", phone="abcd!@#$", email="qa.phone@example.com")
        n = cnt(x, "QA Vendor BadPhone")
        row = [r for r in rows(x) if "QA Vendor BadPhone" in r]
        return ("Pass" if n == 0 else "Fail", f"Phone 'abcd!@#$' submitted. Alert '{a}'; messages {m}; rows created={n} {row}", x.shot("VEN-06_bad_phone"))

    def v07():
        ph = "1" * 30
        u, a, m = create(x, name="QA Vendor LongPhone", lo="هاتف", phone=ph)
        n = cnt(x, "QA Vendor LongPhone"); title = x.pg.title()
        return ("Pass" if n == 0 else "Fail", f"30-digit phone submitted. Alert '{a}'; messages {m}; rows created={n}; title {title!r}", x.shot("VEN-07_long_phone"))

    def v08():
        u, a, m = create(x, name="QA Vendor Beta", lo="مكرر", phone="9876500001", email="qa.beta@example.com")
        n = cnt(x, "QA Vendor Beta")
        return ("Pass" if n == 1 else "Fail", f"Same name/phone/email as existing vendor. Alert '{a}'; messages {m}; rows named 'QA Vendor Beta' = {n}", x.shot("VEN-08_duplicate"))

    def v09():
        u, a, m = create(x, name="     ", lo="     ")
        x.go("/vendor/list"); blank = sum(1 for v in names(x) if v.strip() == "")
        return ("Pass" if blank == 0 else "Fail", f"Whitespace-only name. Alert '{a}'; messages {m}; blank-name rows={blank}", x.shot("VEN-09_whitespace"))

    def v10():
        nm = "QAV" + "N" * 252
        u, a, m = create(x, name=nm, lo="ع")
        n = cnt(x, nm)
        return ("Pass" if n == 1 else "Fail", f"255-char name. Alert '{a}'; saved intact={n == 1}", x.shot("VEN-10_255"))

    def v11():
        nm = "QAV" + "O" * 253
        x.go("/vendor/create"); fill(x, name=nm, lo="ع"); save(x)
        title = x.pg.title(); body = x.pg.inner_text("body")[:300]
        return ("Pass" if "Exception" not in body and "QueryException" not in title else "Fail", f"256-char name. URL {x.pg.url}; title {title!r}; body {body[:220]!r}", x.shot("VEN-11_256"))

    def v12():
        u, a, m = create(x, name="QA Vendor TxtLogo", lo="شعار", logo=TXT)
        n = cnt(x, "QA Vendor TxtLogo")
        return ("Pass" if n == 0 else "Fail", f".txt file uploaded as logo. Alert '{a}'; messages {m}; rows created={n}", x.shot("VEN-12_txt_logo"))

    def v13():
        nm = "<script>alert('xss')</script>QAV"
        create(x, name=nm, lo="ع")
        return ("Pass" if not any("xss" in d for d in x.dialogs) else "Fail", f"Script in name. JS dialogs fired: {x.dialogs}", x.shot("VEN-13_xss"))

    def v14():
        x.go("/vendor/list")
        x.pg.locator("main table tbody tr", has_text="QA Vendor Min").first.locator("#vendor_edit").click(); x.settle(2)
        pre = [x.pg.input_value("#vendor_name"), x.pg.input_value("#vendor_lo_name")]
        x.shot("VEN-14_edit_page")
        x.pg.fill("#vendor_name", "QA Vendor Min Edited"); x.pg.fill("#vendor_phone", "9876500099"); save(x)
        r = [r for r in rows(x) if "QA Vendor Min Edited" in r]; old = sum(1 for v in names(x) if v == "QA Vendor Min")
        return ("Pass" if r and old == 0 and "9876500099" in r[0] else "Fail", f"Edit page prefilled {pre}; after save alert '{x.alert()}'; row {r}; old rows {old}", x.shot("VEN-14_edited"))

    def v15():
        x.go("/vendor/list")
        x.pg.locator("main table tbody tr", has_text="QA Vendor Min Edited").first.locator("#vendor_edit").click(); x.settle(2)
        x.pg.fill("#vendor_name", ""); save(x); m = msgs(x)
        n = cnt(x, "QA Vendor Min Edited")
        return ("Pass" if m and n == 1 else "Fail", f"Name blanked on edit; messages {m}; original still present={n}", "")

    def v16():
        x.go("/vendor/list"); x.pg.fill("#search_term", "Beta"); x.pg.click("main >> text=Search"); x.settle(3)
        n = names(x)
        return ("Pass" if n and all("Beta" in v for v in n) else "Fail", f"Search 'Beta' -> rows {n}", x.shot("VEN-16_search"))

    def v17():
        x.go("/vendor/list"); x.pg.fill("#search_term", "zzNoSuchVendorzz"); x.pg.click("main >> text=Search"); x.settle(3)
        n = names(x); t = x.main()
        return ("Pass" if not n else "Fail", f"Search non-existent -> rows {n}; text {t[t.find('You got'):t.find('You got')+25]!r}", x.shot("VEN-17_search_none"))

    def v18():
        x.go("/vendor/list")
        with x.pg.expect_download(timeout=120000) as d:
            x.pg.click("main >> text=Export to excel")
        f = d.value; path = os.path.join(DATA, "vendor_export_" + f.suggested_filename); f.save_as(path)
        return ("Pass" if os.path.getsize(path) > 0 else "Fail", f"Downloaded '{f.suggested_filename}' ({os.path.getsize(path)} bytes)", "")

    def v19():
        x.go("/vendor/list"); before = len(names(x)); x.dialog_accept = False
        x.pg.locator("main table tbody tr", has_text="QA Vendor Min Edited").first.locator("a.btn-danger").click(); x.settle(2)
        return ("Pass" if len(names(x)) == before and x.dialogs else "Fail", f"Confirm '{x.dialogs}' dismissed; rows before {before} after {len(names(x))}", "")

    def v20():
        x.go("/vendor/list")
        x.pg.locator("main table tbody tr", has_text="QA Vendor Min Edited").first.locator("a.btn-danger").click(); x.settle(3)
        a = x.alert(); n = sum(1 for v in names(x) if v == "QA Vendor Min Edited")
        return ("Pass" if n == 0 else "Fail", f"Confirm accepted; alert '{a}'; remaining rows {n}", x.shot("VEN-20_deleted"))

    def v21():
        x.go("/vendor/list"); vs = names(x)
        x.go("/invoice/create"); inv = x.pg.eval_on_selector_all("#vendor_id option", "e=>e.map(o=>o.text.trim())")
        x.go("/receipt/create"); rec = x.pg.eval_on_selector_all("#vendor_id option", "e=>e.map(o=>o.text.trim())")
        miss = [v for v in vs if v.strip() and (v not in inv or v not in rec)]
        return ("Pass" if not miss else "Fail", f"Vendors in list {len(vs)}; invoice dropdown {inv}; receipt dropdown {rec}; missing {miss}", x.shot("VEN-21_receipt_vendor_dd", False))

    def v22():
        x.go("/vendor/list"); x.pg.fill("#search_term", "Beta"); x.pg.click("main >> text=Search"); x.settle(2)
        x.pg.click("main >> text=Clear"); x.settle(3)
        return ("Pass" if x.pg.input_value("#search_term") == "" and len(names(x)) > 1 else "Fail", f"After Clear: search box '{x.pg.input_value('#search_term')}', rows {len(names(x))}", "")

    T = [("VEN-01", v01), ("VEN-02", v02), ("VEN-03", v03), ("VEN-04", v04), ("VEN-05", v05), ("VEN-06", v06),
         ("VEN-07", v07), ("VEN-08", v08), ("VEN-09", v09), ("VEN-10", v10), ("VEN-11", v11), ("VEN-12", v12),
         ("VEN-13", v13), ("VEN-14", v14), ("VEN-15", v15), ("VEN-16", v16), ("VEN-17", v17), ("VEN-18", v18),
         ("VEN-19", v19), ("VEN-20", v20), ("VEN-21", v21), ("VEN-22", v22)]
    for tid, fn in T:
        if not ONLY or tid in ONLY:
            x.run(tid, fn)
    x.save("vendor")
