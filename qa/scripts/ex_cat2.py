from lib import *
import time
def add(pg,log,name,lo,typ):
    pg.click("text=Add Category"); time.sleep(1)
    pg.fill("#category_name",name); pg.fill("#category_lo_name",lo); pg.select_option("#category_type",typ)
    pg.click(".modal.show >> text=Save"); time.sleep(4); pg.wait_for_load_state("networkidle")
    flush(log); print("URL",pg.url)
    print(pg.inner_text("main")[:1500])
with sync_playwright() as p:
    b,pg,log=start(p)
    pg.goto(BASE+"/category/list"); pg.wait_for_load_state("networkidle"); log.clear()
    add(pg,log,"QA Income Cat 01","دخل","1")
    pg.screenshot(path="../explore/cat_after_add.png", full_page=True)
    print(pg.eval_on_selector_all("main table a, main table button, main .card a, main .card button","els=>els.map(e=>e.outerHTML.slice(0,300))"))
    b.close()
