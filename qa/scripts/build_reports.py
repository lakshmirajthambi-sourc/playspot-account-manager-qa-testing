import json, os, glob, shutil
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from openpyxl.drawing.image import Image as XLImage
from testcases import TC

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "deliverables"); os.makedirs(OUT, exist_ok=True)
ENV = "URL: http://64.227.145.76/account-manager-2/public | Chrome (Playwright Chromium 1.65, headless) | Windows 11 | 1366x900 | Tested 16-Nov-2026"

# ---- load results
R = {}
for f in [g for g in glob.glob(os.path.join(ROOT, "results", "*.json")) if "bugs_built" not in g]:
    for r in json.load(open(f, encoding="utf-8")):
        R[r["id"]] = r

# QA-reviewed overrides: automation passed the step but evidence shows a defect
OVERRIDE = {
    "VEN-03": ("Fail", "Vendor created and listed, but the Logo column shows a broken image: <img src='.../public/public/vendor'> (HTTP 404, naturalWidth 0). Uploaded logo is not displayed."),
}
for k, (st, act) in OVERRIDE.items():
    if k in R:
        R[k]["status"] = st; R[k]["actual"] = act

# ---- bug definitions: (linked TCs, module, title, pre, steps, expected, actual, severity, priority)
BUGS = [
    (["GEN-02"], "General / Navigation", "Reimbursement list crashes with Laravel debug page exposing source code and server paths",
     "Logged in as admin", "1. Log in\n2. From Dashboard click 'Reimbursement' (or open /reimbursement/list)",
     "Reimbursement list page loads; no internal errors shown to users",
     "ErrorException 'Undefined variable $total' rendered on Ignition debug page, revealing /var/www/html/account-manager-2 path, Blade template source and stack trace (APP_DEBUG enabled in production)",
     "Critical", "P1"),
    (["CAT-13"], "Category Management", "Category name longer than 255 chars causes unhandled SQL exception (debug page with SQL query)",
     "Logged in; Categories page open", "1. Click Add Category\n2. Enter a 256-character name, any Arabic name, Type=Expense\n3. Click Save",
     "Validation message such as 'Name may not be greater than 255 characters'; no server error",
     "Page shows 'SQLSTATE[22001]: String data, right truncated: 1406 Data too long for column cat_name' with the full INSERT statement",
     "High", "P1"),
    (["VEN-11"], "Vendor Management", "Vendor name longer than 255 chars causes unhandled server/SQL error",
     "Logged in; Add Vendor page open", "1. Enter a 256-character Name and any Name(ar)\n2. Click Save",
     "Max-length validation message; no server error", "See Actual Result in VEN-11", "High", "P1"),
    (["INV-05"], "Invoices", "Invoice Total Amount calculated incorrectly when Tax % is entered",
     "Logged in; Add invoice page open", "1. Enter line amount 1000\n2. Enter Tax 10\n3. Observe Total Amount\n4. Repeat with 1000/0%, 100/18%, 1000/5%",
     "Total = Amount x (1 + Tax/100): 1100, 1000, 118, 1050", "See INV-05 actual result (e.g. 1000 @10% shows INR 1102; 1000 @0% shows INR 1002; 100 @18% shows INR 120)",
     "Critical", "P1"),
    (["REC-05"], "Receipts", "Receipt Total Amount calculated incorrectly when Tax % is entered",
     "Logged in; Add receipt page open", "1. Enter line amount 1000\n2. Enter Tax 10\n3. Observe Total Amount",
     "Total = Amount x (1 + Tax/100)", "See REC-05 actual result", "Critical", "P1"),
    (["CAT-20", "INV-11"], "Invoices", "Expense categories are offered in the Invoice (income) Category dropdown",
     "Logged in; at least one Expense category exists", "1. Open Invoice > Add Invoice\n2. Expand Category dropdown",
     "Only Income-type categories are listed", "Expense category 'QA Expense Cat 01' (and other Expense categories) appear in the list", "High", "P2"),
    (["CAT-21", "REC-11"], "Receipts", "Income categories are offered in the Receipt (expense) Category dropdown",
     "Logged in; at least one Income category exists", "1. Open Receipts > Add receipt\n2. Expand Category dropdown",
     "Only Expense-type categories are listed", "Income categories appear in the list", "High", "P2"),
    (["INV-02", "INV-04"], "Invoices", "Invoice can be saved without selecting a Category",
     "Logged in; Add invoice page open", "1. Fill Title, Title(ar), Vendor, Date, line item, amount, amount in words\n2. Leave Category = 'Please select'\n3. Save",
     "Category is mandatory; validation message shown", "See INV-04 actual result", "High", "P2"),
    (["REC-02", "REC-04"], "Receipts", "Receipt can be saved without selecting a Category",
     "Logged in; Add receipt page open", "1. Fill all fields except Category\n2. Save",
     "Category is mandatory; validation message shown", "See REC-04 actual result", "High", "P2"),
    (["INV-07"], "Invoices", "Invoice accepts negative line amount", "Logged in", "1. Fill valid invoice\n2. Amount -500\n3. Save",
     "Negative amounts rejected", "See INV-07 actual result", "High", "P2"),
    (["REC-07"], "Receipts", "Receipt accepts negative line amount", "Logged in", "1. Fill valid receipt\n2. Amount -500\n3. Save",
     "Negative amounts rejected", "See REC-07 actual result", "High", "P2"),
    (["INV-08"], "Invoices", "Non-numeric invoice amount not validated", "Logged in", "1. Fill valid invoice\n2. Amount 'abc'\n3. Save",
     "Numeric validation message", "See INV-08 actual result", "Medium", "P2"),
    (["REC-08"], "Receipts", "Non-numeric receipt amount not validated", "Logged in", "1. Fill valid receipt\n2. Amount 'abc'\n3. Save",
     "Numeric validation message", "See REC-08 actual result", "Medium", "P2"),
    (["INV-09"], "Invoices", "Invoice accepts tax percentage above 100", "Logged in", "1. Fill valid invoice\n2. Tax 150\n3. Save",
     "Tax restricted to 0-100%", "See INV-09 actual result", "Medium", "P3"),
    (["REC-09"], "Receipts", "Receipt accepts tax percentage above 100", "Logged in", "1. Fill valid receipt\n2. Tax 150\n3. Save",
     "Tax restricted to 0-100%", "See REC-09 actual result", "Medium", "P3"),
    (["INV-10"], "Invoices", "Invoice with zero amount is accepted", "Logged in", "1. Fill valid invoice\n2. Amount 0\n3. Save",
     "Amount must be greater than 0", "See INV-10 actual result", "Low", "P3"),
    (["REC-10"], "Receipts", "Receipt with zero amount is accepted", "Logged in", "1. Fill valid receipt\n2. Amount 0\n3. Save",
     "Amount must be greater than 0", "See REC-10 actual result", "Low", "P3"),
    (["INV-06"], "Invoices", "Multiple line items not added/summed correctly on Invoice", "Logged in", "1. Amount 500\n2. Click green + icon\n3. Enter 300 in new row",
     "Second row added; Total 800", "See INV-06 actual result", "High", "P2"),
    (["REC-06"], "Receipts", "Multiple line items not added/summed correctly on Receipt", "Logged in", "1. Amount 500\n2. Click green + icon\n3. Enter 300 in new row",
     "Second row added; Total 800", "See REC-06 actual result", "High", "P2"),
    (["VEN-05"], "Vendor Management", "Vendor saved with invalid email format", "Logged in; Add Vendor page",
     "1. Name 'QA Vendor BadEmail', Name(ar)\n2. Email 'abc@'\n3. Save", "Email format validation error; vendor not saved",
     "'Vendor created successfully'; vendor listed with email 'abc@'", "Medium", "P2"),
    (["VEN-06"], "Vendor Management", "Vendor phone accepts letters and special characters", "Logged in; Add Vendor page",
     "1. Fill Name/Name(ar)\n2. Phone 'abcd!@#$'\n3. Save", "Phone accepts digits (and + - space) only", "Vendor saved with phone 'abcd!@#$'", "Medium", "P2"),
    (["VEN-07"], "Vendor Management", "Vendor phone has no length limit (30 digits accepted)", "Logged in; Add Vendor page",
     "1. Fill Name/Name(ar)\n2. Phone with 30 digits\n3. Save", "Length validation (e.g. 7-15 digits)", "Vendor saved with 30-digit phone", "Low", "P3"),
    (["VEN-08"], "Vendor Management", "Duplicate vendor allowed (identical name, phone and email)", "Logged in; vendor 'QA Vendor Beta' exists",
     "1. Add Vendor with same Name, Phone, Email as existing vendor\n2. Save", "Duplicate rejected with message",
     "'Vendor created successfully'; two identical 'QA Vendor Beta' rows in list", "Medium", "P2"),
    (["VEN-03"], "Vendor Management", "Uploaded vendor logo not displayed (broken image, wrong path /public/public/vendor)", "Logged in",
     "1. Add Vendor with a valid PNG logo\n2. Save\n3. View Logo column in Vendor list", "Uploaded logo thumbnail shown",
     "Broken image; img src 'http://64.227.145.76/account-manager-2/public/public/vendor' returns 404", "Medium", "P3"),
    (["VEN-12"], "Vendor Management", "Non-image file accepted as vendor logo", "Logged in", "1. Fill Name/Name(ar)\n2. Choose .txt file as Logo\n3. Save",
     "Only image types (jpg/png) accepted", "See VEN-12 actual result", "Medium", "P3"),
    (["CAT-24", "CAT-15"], "Category Management", "Category Edit does not load data - edit request goes to wrong application path (account-manager-qa) and returns 401",
     "Logged in; category 'QA Expense Cat 01' exists", "1. Open Master Settings > Categories\n2. Click the blue edit (pencil) button on 'QA Expense Cat 01'\n3. Observe the modal and the network request",
     "Modal opens prefilled with the category's Name, Arabic Name and Type; changes can be saved",
     "See CAT-24 actual result: request GET http://64.227.145.76/account-manager-qa/public/category/edit/<id> -> 401; modal fields stay empty, so an existing category cannot be edited",
     "High", "P1"),
    (["VEN-16", "VEN-17"], "Vendor Management", "Vendor Search does not filter the list",
     "Logged in; several vendors exist", "1. Open Vendors list\n2. Type 'Beta' (or 'zzNoSuchVendorzz') in search box\n3. Click Search",
     "Only vendors matching the search text are listed (or 0 items)", "All vendors remain listed; the search term has no effect (re-verified with a 20 s wait)",
     "Medium", "P2"),
    (["VEN-20"], "Vendor Management", "Vendor delete shows success message but the vendor remains in the list",
     "Logged in; vendor 'QA Vendor Min Edited' exists", "1. Open Vendors list\n2. Click delete (red) on 'QA Vendor Min Edited'\n3. Click OK on confirmation\n4. Check list",
     "Vendor removed from list", "'Vendor deleted successfully' is shown but 'QA Vendor Min Edited' is still listed (reproduced twice)", "High", "P2"),
    (["CAT-23"], "Category Management", "Long category names break list layout (horizontal overflow)",
     "Logged in; a category with a long unbroken name exists", "1. Create category with 255-char name without spaces\n2. Open category list",
     "Long text wraps or is truncated; table fits within page", "See CAT-23 actual result", "Low", "P3"),
    (["GEN-03"], "General / Navigation", "Expenses list page renders only the text '1'", "Logged in",
     "1. From Dashboard click 'Expenses' (or open /expense/list)", "Expense list page with layout and table", "Blank page containing only '1'", "High", "P2"),
    (["GEN-04"], "General / Navigation", "Multiple CSS/JS/icon assets return 404 on every page", "Logged in",
     "1. Open any page (e.g. Categories)\n2. Open browser DevTools > Network", "All static assets load (HTTP 200)",
     "See GEN-04 actual result (coreui.bundle.min.js, style.css, main.js, Chart.min.js, icon sprites ... 404)", "Low", "P3"),
    (["GEN-05"], "General / Navigation", "Typo in Invoice and Receipt list header: 'Caegory'", "Logged in",
     "1. Open Invoice list\n2. Open Receipt list", "Header reads 'Category'", "Header reads 'Caegory'", "Low", "P4"),
]

HDR_FILL = PatternFill("solid", start_color="1F3864"); HDR_FONT = Font(name="Arial", bold=True, color="FFFFFF", size=10)
BODY = Font(name="Arial", size=9); THIN = Side(style="thin", color="BFBFBF")
BRD = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
STATUS_FILL = {"Pass": "C6EFCE", "Fail": "FFC7CE", "Blocked": "FFEB9C", "Not Executed": "D9D9D9", "Info": "DDEBF7"}


def table(ws, headers, data, widths):
    ws.append(headers)
    for c in ws[1]:
        c.fill = HDR_FILL; c.font = HDR_FONT; c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center"); c.border = BRD
    for row in data:
        ws.append(row)
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font = BODY; c.alignment = WRAP; c.border = BRD
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "B2"; ws.auto_filter.ref = ws.dimensions
    ws.row_dimensions[1].height = 30


def status_of(tid):
    r = R.get(tid)
    if not r: return "Not Executed", "Not executed (not reached in automated run - server response time / time constraints)"
    st = r["status"]
    if st == "Info": st = "Pass"
    act = r["actual"]
    if r["status"] == "Blocked":
        act = "Not executed to completion - " + act
    return st, act


def build_tc():
    wb = Workbook(); ws = wb.active; ws.title = "Test Cases"
    hdr = ["Test Case ID", "Module", "Test Scenario", "Test Type", "Preconditions", "Test Steps", "Test Data", "Expected Result", "Actual Result", "Status", "Priority", "Evidence"]
    data = []
    for tid, t in TC.items():
        st, act = status_of(tid)
        ev = (R.get(tid) or {}).get("evidence", "")
        data.append([tid, t["module"], t["scenario"], t["type"], t["pre"], t["steps"], t["data"], t["expected"], act[:1500], st, t["priority"], ev])
    table(ws, hdr, data, [11, 18, 30, 16, 26, 38, 24, 34, 50, 11, 9, 26])
    n = len(data) + 1
    for st, col in STATUS_FILL.items():
        ws.conditional_formatting.add(f"J2:J{n}", CellIsRule(operator="equal", formula=[f'"{st}"'], fill=PatternFill("solid", start_color=col)))
    dv = DataValidation(type="list", formula1='"Pass,Fail,Blocked,Not Executed"', allow_blank=True); ws.add_data_validation(dv); dv.add(f"J2:J{n}")

    s = wb.create_sheet("Summary")
    s["A1"] = "Test Execution Summary"; s["A1"].font = Font(name="Arial", bold=True, size=14)
    s["A2"] = ENV; s["A2"].font = Font(name="Arial", italic=True, size=9)
    heads = ["Module", "Total", "Pass", "Fail", "Blocked", "Not Executed", "Pass %"]
    for i, h in enumerate(heads, 1):
        c = s.cell(row=4, column=i, value=h); c.fill = HDR_FILL; c.font = HDR_FONT; c.border = BRD
    mods = list(dict.fromkeys(t["module"] for t in TC.values()))
    for j, m in enumerate(mods, 5):
        s.cell(row=j, column=1, value=m)
        s.cell(row=j, column=2, value=f"=COUNTIF('Test Cases'!$B:$B,A{j})")
        for k, st in enumerate(["Pass", "Fail", "Blocked", "Not Executed"], 3):
            s.cell(row=j, column=k, value=f"=COUNTIFS('Test Cases'!$B:$B,$A{j},'Test Cases'!$J:$J,\"{st}\")")
        s.cell(row=j, column=7, value=f"=IF(B{j}-F{j}=0,0,C{j}/(B{j}-F{j}))").number_format = "0.0%"
    tr = 5 + len(mods)
    s.cell(row=tr, column=1, value="Total").font = Font(name="Arial", bold=True)
    for k in range(2, 7):
        col = get_column_letter(k); s.cell(row=tr, column=k, value=f"=SUM({col}5:{col}{tr-1})").font = Font(name="Arial", bold=True)
    s.cell(row=tr, column=7, value=f"=IF(B{tr}-F{tr}=0,0,C{tr}/(B{tr}-F{tr}))").number_format = "0.0%"
    for row in s.iter_rows(min_row=5, max_row=tr):
        for c in row: c.border = BRD; c.font = Font(name="Arial", size=10, bold=(c.row == tr))
    s.cell(row=tr + 2, column=1, value="Pass % = Pass / Executed (Total - Not Executed). Status values come from Playwright execution logs in results/*.json; 'Not Executed' rows were not run.").font = Font(name="Arial", italic=True, size=9)
    s.column_dimensions["A"].width = 24
    for c in "BCDEFG": s.column_dimensions[c].width = 13
    wb.calculation.fullCalcOnLoad = True
    p = os.path.join(OUT, "Test_Cases.xlsx"); wb.save(p); return p


def build_bugs():
    wb = Workbook(); ws = wb.active; ws.title = "Bug Report"
    hdr = ["Bug ID", "Module", "Bug Title", "Environment", "Preconditions", "Steps to Reproduce", "Expected Result", "Actual Result", "Severity", "Priority", "Status", "Linked Test Case", "Screenshot Evidence"]
    data = []; shots = []; n = 0
    evdir = os.path.join(OUT, "Screenshots"); shutil.rmtree(evdir, ignore_errors=True); os.makedirs(evdir, exist_ok=True)
    for tcs, mod, title, pre, steps, exp, act, sev, pri in sorted(BUGS, key=lambda b: ["Critical", "High", "Medium", "Low"].index(b[7])):
        failed = [t for t in tcs if R.get(t, {}).get("status") == "Fail"]
        if not failed: continue
        n += 1; bid = f"BUG-{n:03d}"
        if act.startswith("See "):
            act = R[failed[0]]["actual"][:1200]
        ev = ""
        for t in failed:
            e = R[t].get("evidence")
            if e and os.path.exists(os.path.join(ROOT, e)):
                dst = f"{bid}_{os.path.basename(e)}"; shutil.copy(os.path.join(ROOT, e), os.path.join(evdir, dst))
                ev = "Screenshots/" + dst; shots.append((bid, os.path.join(evdir, dst))); break
        data.append([bid, mod, title, ENV, pre, steps, exp, act, sev, pri, "Open", ", ".join(failed), ev or "Network/console log (see Actual Result)"])
    table(ws, hdr, data, [9, 18, 36, 26, 24, 38, 32, 50, 10, 9, 9, 14, 30])
    sevc = {"Critical": "FF7C80", "High": "FFC7CE", "Medium": "FFEB9C", "Low": "C6EFCE"}
    for st, col in sevc.items():
        ws.conditional_formatting.add(f"I2:I{len(data)+1}", CellIsRule(operator="equal", formula=[f'"{st}"'], fill=PatternFill("solid", start_color=col)))
    ev = wb.create_sheet("Evidence")
    r = 1
    for bid, path in shots:
        ev.cell(row=r, column=1, value=bid).font = Font(name="Arial", bold=True, size=12)
        img = XLImage(path); scale = min(1.0, 900 / img.width, 900 / img.height); img.width *= scale; img.height *= scale
        ev.add_image(img, f"A{r+1}"); r += int(img.height / 20) + 4
    p = os.path.join(OUT, "Bug_Report.xlsx"); wb.save(p)
    return p, data


if __name__ == "__main__":
    print(build_tc()); p, d = build_bugs(); print(p, len(d), "bugs")
    json.dump(d, open(os.path.join(ROOT, "results", "bugs_built.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
