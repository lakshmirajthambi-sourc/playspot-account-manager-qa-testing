from lib import *
with sync_playwright() as p:
    x = Ctx(p)
    x.go("/invoice/create")
    x.pg.click("main form[action$='invoice/store'] >> text=Save"); x.settle(2)
    print("EMPTY url", x.pg.url, "msgs", visible_msgs(x, "main"))
    x.shot("ex_inv_empty")
    print("date attrs", x.pg.eval_on_selector("#invoice_date", "e=>[e.readOnly,e.className,e.placeholder]"))
    print("cat opts", x.pg.eval_on_selector_all("#category_id option", "e=>e.map(o=>o.value+':'+o.text)"))
    print("ven opts", x.pg.eval_on_selector_all("#vendor_id option", "e=>e.map(o=>o.value+':'+o.text)"))
    x.pg.fill("input[name='amount[0]']", "1000"); x.pg.locator("input[name='amount[0]']").first.press("Tab"); x.settle(1)
    print("total after 1000:", x.pg.inner_text("main form[action$='invoice/store']")[x.pg.inner_text("main form[action$='invoice/store']").find("Total"):][:60])
    x.pg.fill("#inv_tax", "10"); x.pg.press("#inv_tax", "Tab"); x.settle(1)
    t = x.pg.inner_text("main form[action$='invoice/store']"); print("total after tax10:", t[t.find("Total"):][:60])
    print("amount words:", x.pg.input_value("#inv_amount_words"))
    # add row
    plus = x.pg.locator("main form[action$='invoice/store'] .fa-plus-circle, main form[action$='invoice/store'] .add_row, main form[action$='invoice/store'] i.cil-plus, main form[action$='invoice/store'] [class*=plus]")
    print("plus count", plus.count(), [plus.nth(i).evaluate("e=>e.outerHTML.slice(0,200)") for i in range(min(plus.count(), 3))])
    if plus.count():
        plus.first.click(); x.settle(1)
        print("amount inputs", x.pg.eval_on_selector_all("main form[action$='invoice/store'] input[name^=amount]", "e=>e.map(i=>i.name)"))
    x.shot("ex_inv_calc")
    # datepicker
    x.pg.click("#invoice_date"); x.settle(1); x.shot("ex_inv_datepicker", False)
    print("date val", x.pg.input_value("#invoice_date"))
    x.b.close()
