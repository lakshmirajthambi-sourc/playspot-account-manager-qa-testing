from playwright.sync_api import sync_playwright
BASE="http://64.227.145.76/account-manager-2/public"
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={"width":1366,"height":900}); pg=c.new_page()
    pg.goto(BASE+"/login"); pg.screenshot(path="explore/login.png", full_page=True)
    print(pg.title()); print(pg.inner_text("body")[:1500])
    pg.fill("input[name=email]","admin@admin.com"); pg.fill("input[name=password]","password")
    pg.click("button[type=submit]"); pg.wait_for_load_state("networkidle")
    print("URL", pg.url); pg.screenshot(path="explore/dashboard.png", full_page=True)
    c.storage_state(path="state.json")
    links=pg.eval_on_selector_all("a","els=>els.map(e=>[e.innerText.trim(),e.href])")
    for l in links: print(l)
    b.close()
