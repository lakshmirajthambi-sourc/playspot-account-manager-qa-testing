from lib import *
import re
F = "main form[action$='invoice/store']"
with sync_playwright() as p:
    x = Ctx(p)
    x.go("/invoice/create")
    print("green plus:", x.pg.eval_on_selector_all(F + " a, " + F + " button, " + F + " i, " + F + " svg", "e=>e.filter(n=>!/Save|Close/.test(n.innerText||'')).map(n=>n.tagName+' '+(n.className.baseVal??n.className)+' '+(n.getAttribute('onclick')||'')+' '+(n.id||'')).slice(0,15)"))
    scripts = x.pg.eval_on_selector_all("script:not([src])", "e=>e.map(s=>s.textContent)")
    js = "\n".join(scripts)
    for kw in ["inv_tax", "total", "amount"]:
        for m in re.finditer(kw, js):
            pass
    i = js.find("inv_tax")
    open("../explore/invoice_inline.js", "w", encoding="utf-8").write(js)

    def total():
        t = x.pg.inner_text(F); return t[t.find("Total Amount"):][:30].replace("\n", " ")
    for amt, tax in [("1000", ""), ("1000", "10"), ("1000", "0"), ("100", "18"), ("1000", "5"), ("250.50", "")]:
        x.pg.fill("input[name='amount[0]'] >> nth=0", amt); x.pg.press("input[name='amount[0]'] >> nth=0", "Tab")
        x.pg.fill("#inv_tax", tax); x.pg.press("#inv_tax", "Tab"); time.sleep(0.5)
        print(f"amount={amt} tax={tax} -> {total()}")
    x.b.close()
