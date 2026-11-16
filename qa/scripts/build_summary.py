import json, os
from collections import Counter, OrderedDict
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from testcases import TC
from build_reports import R, status_of, ROOT, OUT, ENV

bugs = json.load(open(os.path.join(ROOT, "results", "bugs_built.json"), encoding="utf-8"))

doc = Document()
st = doc.styles["Normal"]; st.font.name = "Arial"; st.font.size = Pt(10)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
for s in ["Heading 1", "Heading 2", "Title"]:
    doc.styles[s].font.name = "Arial"; doc.styles[s].font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
for sec in doc.sections:
    sec.left_margin = sec.right_margin = Cm(2)


def shade(cell, hexcol):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hexcol); tcPr.append(sh)


def tbl(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Table Grid"
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""; r = c.paragraphs[0].add_run(h); r.bold = True; r.font.color.rgb = RGBColor(255, 255, 255); r.font.size = Pt(9)
        shade(c, "1F3864")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""; rr = cells[i].paragraphs[0].add_run(str(v)); rr.font.size = Pt(9)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths): row.cells[i].width = Cm(w)
    doc.add_paragraph()
    return t


def bullet(text):
    doc.add_paragraph(text, style="List Bullet")


doc.add_heading("QA Testing Summary Report", 0)
p = doc.add_paragraph(); p.add_run("Application: ").bold = True; p.add_run("Accounts Manager (provided as 'Hotel Management System')")
p = doc.add_paragraph(); p.add_run("Environment: ").bold = True; p.add_run(ENV)
p = doc.add_paragraph(); p.add_run("Test approach: ").bold = True; p.add_run("Exploratory walkthrough followed by scripted manual test cases executed through Playwright (Python) browser automation, with screenshots captured as evidence.")

doc.add_heading("1. Application Overview", 1)
doc.add_paragraph("The application at the given URL identifies itself as 'Accounts Manager' (CoreUI/Laravel). It is a small accounting app, "
                  "not a hotel management system: it has no rooms, bookings or guests. After login, admin users land on a Dashboard that shows "
                  "totals for Invoices, Receipts, Expenses and Reimbursement.")
doc.add_paragraph("Modules discovered during exploration:")
for m in ["Dashboard - summary tiles (INR totals and counts) for Invoices, Receipts, Expenses and Reimbursement",
          "Quotations - list/add quotation with vendor & category filters (not in scope; not tested)",
          "Income > Invoice - create, list, view, search/filter by vendor, category and date range, export to Excel",
          "Income > Receipts - create receipt (with optional 'Fetch Invoices' link), payment type Card/Cash, list, search, export",
          "Reports - Quotation, Invoice and Receipt report menus (not in scope)",
          "Master Settings > Vendors - add / edit / delete vendor with logo, search, export",
          "Master Settings > Categories - add / edit / delete Income or Expense categories (modal form)",
          "Expenses and Reimbursement lists - linked from Dashboard (both found broken, see bugs)",
          "User menu - 'Switch to user' impersonation entries and Logout"]:
    bullet(m)
doc.add_paragraph("Workflow: an admin first sets up master data (categories typed Income/Expense, and vendors). Invoices record income against an "
                  "Income category and a vendor. Receipts record expense payments against an Expense category and a vendor. Each document "
                  "has one or more line items, a tax %, a computed Total Amount and a manually typed 'amount in words' (English and Arabic).")

doc.add_heading("2. Scope - Modules Tested", 1)
tbl(["Module", "Areas covered"], [
    ["Category Management", "Add Income/Expense, mandatory fields, duplicates (exact and case-insensitive), whitespace, 1/255/256-char boundaries, script injection, edit, delete (cancel/confirm), category-type filtering in Invoice/Receipt"],
    ["Vendor Management", "Add (full/minimal), mandatory fields, email/phone format, phone length, duplicates, 255/256-char boundaries, logo upload (image/non-image), script injection, edit, delete, search, clear, export, availability in transactions"],
    ["Invoices", "Form UI, mandatory fields, valid create, missing category, tax calculation, multiple line items, negative/zero/non-numeric amounts, tax > 100%, category dropdown filtering, list/actions, view, search, dashboard, export"],
    ["Receipts", "Same coverage as Invoices, plus Payment Type"],
    ["General / Navigation", "Login, Dashboard links to Expenses/Reimbursement, static asset loading, label spelling"],
], [4, 13])
doc.add_paragraph("Test types applied: Positive, Negative, Boundary Value, Functional, Field Validation, CRUD and UI.")
doc.add_paragraph("Out of scope: Quotations, Reports, user switching, Forgot Password, performance and security penetration testing. "
                  "Security-relevant observations made incidentally are still reported.")

doc.add_heading("3. Test Execution Summary", 1)
mods = list(OrderedDict.fromkeys(t["module"] for t in TC.values()))
rows = []; tot = Counter()
for m in mods:
    c = Counter(status_of(i)[0] for i, t in TC.items() if t["module"] == m)
    n = sum(c.values()); ex = n - c["Not Executed"]
    rows.append([m, n, c["Pass"], c["Fail"], c["Blocked"], c["Not Executed"], f"{(c['Pass'] / ex * 100) if ex else 0:.0f}%"])
    tot.update(c); tot["Total"] += n
ex = tot["Total"] - tot["Not Executed"]
rows.append(["TOTAL", tot["Total"], tot["Pass"], tot["Fail"], tot["Blocked"], tot["Not Executed"], f"{(tot['Pass'] / ex * 100) if ex else 0:.0f}%"])
tbl(["Module", "Total", "Pass", "Fail", "Blocked", "Not Executed", "Pass % (of executed)"], rows)
doc.add_paragraph("Status definitions: Pass/Fail are taken from the Playwright execution log. 'Blocked' means the run started but the step timed out "
                  "because the test server was slow (responses of 30-120 s were seen), so no verdict was recorded. 'Not Executed' means the case was not run. "
                  "No result was assumed or invented. Every case is listed in Test_Cases.xlsx with its actual result.")

doc.add_heading("4. Bugs Found", 1)
sev = Counter(b[8] for b in bugs)
doc.add_paragraph(f"{len(bugs)} reproducible defects logged - " + ", ".join(f"{k}: {sev[k]}" for k in ["Critical", "High", "Medium", "Low"] if sev[k]) + ". Full details and screenshots are in Bug_Report.xlsx.")
tbl(["Bug ID", "Module", "Title", "Severity", "Priority"], [[b[0], b[1], b[2], b[8], b[9]] for b in bugs], [1.8, 3.2, 9, 1.8, 1.6])

doc.add_heading("5. Key Observations", 1)
for o in ["Production debug mode: unhandled exceptions render the Laravel Ignition page, which exposes source code, file paths and SQL statements to end users.",
          "Server-side validation is inconsistent. Categories reject duplicates, but vendors do not. Vendor email and phone formats are not validated.",
          "Category type (Income/Expense) is not used to filter the category dropdowns on Invoice and Receipt, so transactions can be posted to the wrong ledger type.",
          "Required fields are not marked with an asterisk on any form. 'Amount in words' is mandatory and typed by hand, so it can contradict the computed total.",
          "Delete actions use plain GET links protected only by a JavaScript confirm() (CSRF-prone design). Recommend POST/DELETE with a CSRF token.",
          "The test server responds very slowly (individual pages took 30 s or more), which caused several automation timeouts."]:
    bullet(o)

doc.add_heading("6. Conclusion", 1)
crit = sev["Critical"] + sev["High"]
doc.add_paragraph(f"Basic CRUD flows for categories and vendors, and creation of invoices and receipts, work. However, {crit} Critical/High defects remain open, "
                  "including incorrect total calculation, debug pages exposing source code and SQL, and missing category validation. "
                  "Recommendation: NOT READY FOR RELEASE. Fix the Critical/High defects, disable APP_DEBUG, add server-side validation "
                  "(lengths, formats, numeric ranges, duplicates), then re-run the failed, blocked and not-executed cases as a regression cycle.")
doc.add_heading("7. Test Data & Artefacts", 1)
doc.add_paragraph("All test records are prefixed 'QA ' (e.g. QA Income Cat 02, QA Vendor Beta, QA Invoice Valid 01). The database had no business data before testing "
                  "(all lists showed 0 items), so no existing data was changed or deleted. Deliverables: Test_Cases.xlsx, Bug_Report.xlsx (with an Evidence sheet), "
                  "this summary, the Screenshots folder, and the Playwright scripts in qa/scripts.")
p = os.path.join(OUT, "QA_Testing_Summary.docx"); doc.save(p); print(p)
