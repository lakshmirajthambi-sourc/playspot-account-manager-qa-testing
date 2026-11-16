from lib import *
with sync_playwright() as p:
    x = Ctx(p)
    # vendor list current state
    x.go("/vendor/list")
    print("VENDOR NAMES:", [r[2][:30] for r in rows(x) if len(r) > 3])
    # search with explicit response wait
    x.pg.fill("#search_term", "Beta")
    x.log.clear()
    x.pg.click("main >> text=Search"); time.sleep(20); x.settle(3)
    print("SEARCH net:", x.log)
    print("AFTER SEARCH NAMES:", [r[2][:30] for r in rows(x) if len(r) > 3])
    print("search btn:", x.pg.eval_on_selector("main >> text=Search", "e=>e.outerHTML"))
    x.shot("VERIFY_vendor_search")
    # category edit
    x.go("/category/list")
    btn = x.pg.locator("main table tbody tr", has_text="QA Expense Cat 01").first.locator("#category_edit")
    print("edit btn:", btn.evaluate("e=>e.outerHTML.slice(0,120)"))
    x.log.clear()
    btn.click()
    for i in range(12):
        time.sleep(5)
        if x.pg.locator("#add-category.show").count():
            break
    print("modal shown:", x.pg.locator("#add-category.show").count(), "net:", x.log, "name val:", x.pg.input_value("#category_name"))
    x.shot("VERIFY_cat_edit", False)
    x.b.close()
