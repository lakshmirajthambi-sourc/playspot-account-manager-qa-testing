from lib import *
import time
with sync_playwright() as p:
    b,pg,log=start(p)
    pg.goto(BASE+"/category/list"); pg.wait_for_load_state("networkidle"); flush(log)
    pg.click("text=Add Category"); time.sleep(1)
    pg.screenshot(path="explore/cat_modal.png")
    print(pg.inner_text(".modal.show") if pg.locator(".modal.show").count() else "no modal")
    # empty save
    pg.click(".modal.show >> text=Save"); time.sleep(2)
    print("AFTER EMPTY SAVE url", pg.url); flush(log)
    pg.screenshot(path="explore/cat_empty_save.png")
    print(pg.inner_text("main")[:800])
    b.close()
