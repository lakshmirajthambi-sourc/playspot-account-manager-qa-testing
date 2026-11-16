import sys
from playwright.sync_api import sync_playwright
BASE="http://64.227.145.76/account-manager-2/public"
pages=sys.argv[1:]
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(storage_state="state.json",viewport={"width":1366,"height":900}); pg=c.new_page()
    for path in pages:
        pg.goto(BASE+"/"+path); pg.wait_for_load_state("networkidle")
        name=path.strip("/").replace("/","_") or "root"
        pg.screenshot(path=f"explore/{name}.png", full_page=True)
        print("=====",path,"->",pg.url, pg.title())
        print(pg.inner_text("main") if pg.locator("main").count() else pg.inner_text("body")[:3000])
        print("-- links:", [l for l in pg.eval_on_selector_all("main a, main button","els=>els.map(e=>(e.innerText.trim()+' '+(e.getAttribute('href')||'')+' '+(e.getAttribute('onclick')||'')).slice(0,150))") ][:40])
        print("-- inputs:", pg.eval_on_selector_all("main input, main select, main textarea","els=>els.map(e=>[e.tagName,e.name,e.type,e.id,e.required,e.getAttribute('maxlength'),e.tagName=='SELECT'?Array.from(e.options).map(o=>o.value+':'+o.text).slice(0,15).join('|'):''])"))
        print("-- forms:", pg.eval_on_selector_all("main form","els=>els.map(e=>[e.action,e.method])"))
    b.close()
