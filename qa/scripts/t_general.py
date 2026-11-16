from lib import *
with sync_playwright() as p:
    x = Ctx(p)

    def g01():
        x.go("/"); t = x.main()
        return ("Pass" if "Invoices" in t and "Receipts" in t else "Fail", f"Redirected to {x.pg.url}; dashboard tiles: {t[:120]!r}", x.shot("GEN-01_dashboard"))

    def g02():
        x.go("/reimbursement/list"); title = x.pg.title(); body = x.pg.inner_text("body")
        bad = "Undefined variable" in body or "Exception" in body
        return ("Fail" if bad else "Pass", f"Page title {title!r}. Laravel debug error page shown exposing server path and Blade source (e.g. '/var/www/html/account-manager-2/...')" if bad else "Loaded", x.shot("GEN-02_reimbursement_error", False))

    def g03():
        x.go("/expense/list"); body = x.pg.inner_text("body").strip()
        return ("Fail" if len(body) < 20 else "Pass", f"Page body text: {body[:80]!r} (no layout, menu or list rendered)", x.shot("GEN-03_expense_list", False))

    def g04():
        x.log.clear(); x.go("/category/list")
        bad = [l for l in x.log if " 404 " in l]
        return ("Fail" if bad else "Pass", f"{len(bad)} resources returned 404: " + "; ".join(l.split('/public/')[-1] for l in bad), "")

    def g05():
        x.go("/invoice/list"); a = x.main(); x.shot("GEN-05_invoice_header_typo", False)
        x.go("/receipt/list"); b = x.main()
        typo = "Caegory" in a and "Caegory" in b
        return ("Fail" if typo else "Pass", "Column header reads 'Caegory' on both Invoice and Receipt lists" if typo else "OK", "screens/GEN-05_invoice_header_typo.png")

    for tid, fn in [("GEN-01", g01), ("GEN-02", g02), ("GEN-03", g03), ("GEN-04", g04), ("GEN-05", g05)]:
        x.run(tid, fn)
    x.save("general")
