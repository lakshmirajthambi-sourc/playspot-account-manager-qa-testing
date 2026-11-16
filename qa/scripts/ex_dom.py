from lib import *
with sync_playwright() as p:
    x = Ctx(p)
    for path in ["/invoice/create", "/receipt/create"]:
        x.go(path)
        h = x.pg.eval_on_selector("main form", "f=>f.outerHTML")
        name = path.split("/")[1]
        open(f"../explore/{name}_form.html", "w", encoding="utf-8").write(h)
        js = x.pg.eval_on_selector_all("script", "e=>e.map(s=>s.src||s.textContent).join('\n=====\n')")
        open(f"../explore/{name}_scripts.txt", "w", encoding="utf-8").write(js)
    x.b.close()
