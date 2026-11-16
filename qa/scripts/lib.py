from playwright.sync_api import sync_playwright
import json, time, os
BASE = "http://64.227.145.76/account-manager-2/public"
HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "screens")
os.makedirs(SHOTS, exist_ok=True)


class Ctx:
    def __init__(s, p, headless=True):
        s.b = p.chromium.launch(headless=headless)
        s.c = s.b.new_context(viewport={"width": 1366, "height": 900})
        s.pg = s.c.new_page()
        s.pg.set_default_timeout(90000)
        s.pg.set_default_navigation_timeout(120000)
        s.log = []
        s.dialog_accept = True
        s.dialogs = []
        s.pg.on("dialog", s._dlg)
        s.pg.on("response", s._resp)
        s.pg.goto(BASE + "/login", wait_until="domcontentloaded")
        s.pg.fill("input[name=email]", "admin@admin.com")
        s.pg.fill("input[name=password]", "password")
        s.pg.click("button[type=submit]")
        s.pg.wait_for_load_state("domcontentloaded")
        s.results = []

    def _resp(s, r):
        u = r.url
        if u.endswith((".ttf", ".woff", ".map")) or "64h6xh" in u:
            return
        if r.request.method != "GET" or r.status >= 400:
            s.log.append(f"{r.request.method} {r.status} {u}")

    def _dlg(s, d):
        s.dialogs.append(d.message)
        if s.dialog_accept:
            d.accept()
        else:
            d.dismiss()

    def go(s, path):
        s.pg.goto(BASE + path, wait_until="domcontentloaded")
        s.settle()

    def settle(s, t=1.0):
        try:
            s.pg.wait_for_load_state("networkidle", timeout=60000)
        except Exception:
            pass
        time.sleep(t)

    def shot(s, name, full=True):
        s.pg.screenshot(path=os.path.join(SHOTS, name + ".png"), full_page=full)
        return "screens/" + name + ".png"

    def main(s):
        return s.pg.inner_text("main")

    def alert(s):
        a = s.pg.eval_on_selector_all("main .alert", "els=>els.map(e=>e.innerText.replace('×','').trim())")
        return " | ".join(a)

    def run(s, tid, fn):
        s.log.clear(); s.dialogs.clear(); s.dialog_accept = True
        print(f"--- {tid}", flush=True)
        try:
            out = fn()
            status, actual = out[0], out[1]
            ev = out[2] if len(out) > 2 else ""
        except Exception as e:
            status, actual, ev = "Blocked", "Automation error: " + str(e).splitlines()[0][:200], ""
            try:
                ev = s.shot(f"{tid}_error")
            except Exception:
                pass
        print(f"    {status}: {actual}", flush=True)
        if s.log:
            print("    net:", s.log[-6:], flush=True)
        s.results.append({"id": tid, "status": status, "actual": actual, "evidence": ev,
                          "net": s.log[-6:], "dialogs": list(s.dialogs)})

    def save(s, name):
        p = os.path.join(HERE, "..", "results"); os.makedirs(p, exist_ok=True)
        fp = os.path.join(p, name + ".json")
        old = json.load(open(fp, encoding="utf-8")) if os.path.exists(fp) else []
        ids = {r["id"] for r in s.results}
        merged = [r for r in old if r["id"] not in ids] + s.results
        merged.sort(key=lambda r: r["id"])
        json.dump(merged, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        s.b.close()


def rows(x):
    return x.pg.eval_on_selector_all(
        "main table tbody tr",
        "els=>els.map(e=>Array.from(e.querySelectorAll('td,th')).map(c=>c.innerText.trim()))")


def visible_msgs(x, scope):
    return x.pg.eval_on_selector_all(
        f"{scope} .invalid-feedback, {scope} label.error, {scope} span.error, {scope} .text-danger, {scope} .help-block",
        "els=>els.filter(e=>e.offsetParent!==null).map(e=>e.innerText.trim()).filter(t=>t)")
