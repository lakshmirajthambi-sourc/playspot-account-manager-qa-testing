# Test case definitions: id -> (module, scenario, type, preconditions, steps, data, expected, priority)
PRE_LOGIN = "User logged in as admin@admin.com"
TC = {}


def add(i, mod, scen, typ, pre, steps, data, exp, pri):
    TC[i] = dict(module=mod, scenario=scen, type=typ, pre=pre, steps=steps, data=data, expected=exp, priority=pri)


# ---------------- General / Login / Navigation ----------------
G = "General / Navigation"
add("GEN-01", "Login", "Login with valid credentials", "Positive / Functional", "Application URL reachable",
    "1. Open /login\n2. Enter email and password\n3. Click Login", "admin@admin.com / password",
    "User is redirected to Dashboard showing Invoices, Receipts, Expenses, Reimbursement tiles", "High")
add("GEN-02", G, "Open Reimbursement list from Dashboard link", "Functional / UI", PRE_LOGIN,
    "1. On Dashboard click 'Reimbursement' tile/link (/reimbursement/list)", "-",
    "Reimbursement list page loads (empty list message if no data)", "High")
add("GEN-03", G, "Open Expenses list from Dashboard link", "Functional / UI", PRE_LOGIN,
    "1. On Dashboard click 'Expenses' (/expense/list)", "-",
    "Expense list page loads with standard layout", "Medium")
add("GEN-04", G, "Static assets load without errors", "UI", PRE_LOGIN,
    "1. Open any page\n2. Inspect network requests", "-",
    "All CSS/JS/icon resources return HTTP 200", "Low")
add("GEN-05", G, "Invoice/Receipt list column headers spelled correctly", "UI", PRE_LOGIN,
    "1. Open Invoice list\n2. Open Receipt list\n3. Read table headers", "-",
    "Column header reads 'Category'", "Low")

# ---------------- Category ----------------
C = "Category Management"
CP = PRE_LOGIN + "; Master Settings > Categories page open"
add("CAT-01", C, "Open Add Category modal - verify UI", "UI", CP, "1. Click 'Add Category'", "-",
    "Modal shows Name, Arabic Name, Type (Income/Expense), Close and Save", "Medium")
add("CAT-02", C, "Save with all fields empty", "Negative / Field validation", CP,
    "1. Click Add Category\n2. Click Save without data", "All blank",
    "Form not submitted; required messages for Name, Arabic Name and Type", "High")
add("CAT-03", C, "Add Income category", "Positive / CRUD-Create", CP,
    "1. Click Add Category\n2. Enter Name, Arabic Name\n3. Type = Income\n4. Save", "QA Income Cat 02 / فئة دخل / Income",
    "Success message; category listed with type Income", "High")
add("CAT-04", C, "Add Expense category", "Positive / CRUD-Create", CP,
    "1. Click Add Category\n2. Enter Name, Arabic Name\n3. Type = Expense\n4. Save", "QA Expense Cat 01 / فئة مصروف / Expense",
    "Success message; category listed with type Expense", "High")
add("CAT-05", C, "Name blank, other fields filled", "Negative / Mandatory", CP,
    "1. Leave Name blank\n2. Fill Arabic name, Type=Income\n3. Save", "Name = ''", "'Please enter category name' shown; not saved", "High")
add("CAT-06", C, "Type not selected", "Negative / Mandatory", CP,
    "1. Fill Name, Arabic Name\n2. Leave Type = Please select\n3. Save", "QA NoType Cat", "'Please choose category type' shown; not saved", "High")
add("CAT-07", C, "Arabic name blank", "Negative / Mandatory", CP,
    "1. Fill Name, Type\n2. Leave Arabic Name blank\n3. Save", "QA NoArabic Cat", "Validation message for Arabic name; not saved", "Medium")
add("CAT-08", C, "Duplicate category (same name & type)", "Negative / Duplicate", CP + "; 'QA Income Cat 02' exists",
    "1. Add category with an existing name and type\n2. Save", "QA Income Cat 02 / Income", "Duplicate rejected with message; only one record", "High")
add("CAT-09", C, "Duplicate category with different letter case", "Negative / Duplicate", CP + "; 'QA Income Cat 02' exists",
    "1. Add 'qa income cat 02' as Income\n2. Save", "qa income cat 02", "Duplicate rejected (case-insensitive)", "Medium")
add("CAT-10", C, "Whitespace-only name", "Negative / Field validation", CP,
    "1. Enter only spaces in Name and Arabic Name\n2. Type Income\n3. Save", "'     '", "Rejected as empty; no blank record", "Medium")
add("CAT-11", C, "Minimum length name (1 char)", "Boundary", CP, "1. Name 'Q', Arabic 'ق', Type Expense\n2. Save", "Q", "Category saved", "Low")
add("CAT-12", C, "Maximum length name (255 chars)", "Boundary", CP, "1. Enter 255-char name\n2. Save", "'QA'+253x'L'", "Category saved with full name", "Medium")
add("CAT-13", C, "Name exceeding max length (256 chars)", "Boundary / Negative", CP, "1. Enter 256-char name\n2. Save", "'QA'+254x'M'",
    "Friendly validation message (max 255 chars); no server error", "High")
add("CAT-14", C, "Script injection in category name", "Negative / Security", CP, "1. Enter <script> payload as name\n2. Save\n3. View list",
    "<script>alert('xss')</script>QA", "Text stored/displayed escaped; no script execution", "High")
add("CAT-15", C, "Edit category name", "Positive / CRUD-Update", CP + "; 'QA Expense Cat 01' exists",
    "1. Click edit (pencil) on row\n2. Verify prefilled values\n3. Change name\n4. Save", "QA Expense Cat 01 Edited",
    "Modal prefilled with current values; updated name listed; no duplicate row", "High")
add("CAT-16", C, "Edit category - clear name", "Negative / CRUD-Update", CP, "1. Edit category\n2. Clear Name\n3. Save", "Name = ''",
    "Validation message; original record unchanged", "Medium")
add("CAT-17", C, "Edit category to an existing name", "Negative / Duplicate", CP, "1. Edit a category\n2. Rename to existing 'QA Income Cat 02' / Income\n3. Save",
    "QA Income Cat 02", "Duplicate rejected", "Medium")
add("CAT-18", C, "Delete category - cancel confirmation", "Functional / CRUD-Delete", CP, "1. Click delete\n2. Click Cancel on confirm dialog", "-",
    "Confirmation shown; record not deleted", "Medium")
add("CAT-19", C, "Delete category - confirm", "Positive / CRUD-Delete", CP + "; 'QA Income Cat 01' exists (unused)", "1. Click delete\n2. Click OK",
    "QA Income Cat 01", "Record removed; success message", "High")
add("CAT-20", C, "Invoice category dropdown shows only Income categories", "Functional / Integration", CP + "; Income & Expense categories exist",
    "1. Open Invoice > Add Invoice\n2. Expand Category", "-", "Only Income categories listed", "High")
add("CAT-21", C, "Receipt category dropdown shows only Expense categories", "Functional / Integration", CP + "; Income & Expense categories exist",
    "1. Open Receipts > Add receipt\n2. Expand Category", "-", "Only Expense categories listed", "High")
add("CAT-22", C, "Category list display", "UI", CP, "1. Open category list", "-", "List shows #, Name, Type, Action with item count", "Low")

add("CAT-23", C, "List layout with very long category name", "UI", CP + "; 255-char category exists (CAT-12)", "1. Open category list\n2. Check table fits the page", "-",
    "Long names wrap/truncate; no horizontal page overflow", "Low")
add("CAT-24", C, "Edit request loads category data", "Functional / CRUD-Update", CP, "1. Click edit (pencil) on 'QA Expense Cat 01'\n2. Observe network request and modal", "-",
    "Edit data request returns 200 and modal is prefilled", "High")

# ---------------- Vendor ----------------
V = "Vendor Management"
VP = PRE_LOGIN + "; Master Settings > Vendors"
add("VEN-01", V, "Add Vendor form UI", "UI", VP, "1. Click Add Vendor", "-", "Fields Name, Name(ar), Phone, Email, Address, Address(ar), Logo; mandatory fields marked", "Low")
add("VEN-02", V, "Save with all fields empty", "Negative / Mandatory", VP, "1. Add Vendor\n2. Click Save", "All blank", "Required messages for Name and Name(ar); not saved", "High")
add("VEN-03", V, "Add vendor with all fields and PNG logo", "Positive / CRUD-Create", VP,
    "1. Fill all fields\n2. Upload PNG logo\n3. Save", "QA Vendor Beta / 9876500001 / qa.beta@example.com / qa_logo.png",
    "Vendor created; listed with details and logo image visible", "High")
add("VEN-04", V, "Add vendor with mandatory fields only", "Positive", VP, "1. Fill Name and Name(ar)\n2. Save", "QA Vendor Min", "Vendor created", "Medium")
add("VEN-05", V, "Invalid email format", "Negative / Field validation", VP, "1. Fill name fields\n2. Email 'abc@'\n3. Save", "abc@", "Email format error; not saved", "High")
add("VEN-06", V, "Non-numeric phone", "Negative / Field validation", VP, "1. Fill name fields\n2. Phone 'abcd!@#$'\n3. Save", "abcd!@#$", "Phone format error; not saved", "High")
add("VEN-07", V, "Phone exceeding valid length", "Boundary", VP, "1. Phone with 30 digits\n2. Save", "111111111111111111111111111111", "Length validation error; not saved", "Medium")
add("VEN-08", V, "Duplicate vendor (same name, phone, email)", "Negative / Duplicate", VP + "; QA Vendor Beta exists",
    "1. Add vendor identical to existing one\n2. Save", "QA Vendor Beta / 9876500001 / qa.beta@example.com", "Duplicate rejected", "High")
add("VEN-09", V, "Whitespace-only name", "Negative", VP, "1. Spaces in Name / Name(ar)\n2. Save", "'     '", "Rejected; no blank record", "Medium")
add("VEN-10", V, "Name 255 chars", "Boundary", VP, "1. 255-char name\n2. Save", "'QAV'+252x'N'", "Saved intact", "Low")
add("VEN-11", V, "Name 256 chars", "Boundary / Negative", VP, "1. 256-char name\n2. Save", "'QAV'+253x'O'", "Friendly max-length validation; no server error", "High")
add("VEN-12", V, "Upload non-image file as logo", "Negative / File validation", VP, "1. Fill name fields\n2. Upload .txt as logo\n3. Save", "not_an_image.txt", "File type rejected", "Medium")
add("VEN-13", V, "Script injection in vendor name", "Negative / Security", VP, "1. Enter <script> payload\n2. Save\n3. View list", "<script>alert('xss')</script>QAV", "Escaped; no execution", "High")
add("VEN-14", V, "Edit vendor", "Positive / CRUD-Update", VP + "; QA Vendor Min exists", "1. Click edit\n2. Verify prefill\n3. Change name & phone\n4. Save",
    "QA Vendor Min Edited / 9876500099", "Updated values listed", "High")
add("VEN-15", V, "Edit vendor - clear name", "Negative", VP, "1. Edit\n2. Clear Name\n3. Save", "''", "Validation message; record unchanged", "Medium")
add("VEN-16", V, "Search vendor by name", "Functional", VP, "1. Enter 'Beta' in search\n2. Click Search", "Beta", "Only matching vendors listed", "Medium")
add("VEN-17", V, "Search with no match", "Negative", VP, "1. Search non-existent text", "zzNoSuchVendorzz", "No rows; 0 items", "Low")
add("VEN-18", V, "Export vendors to Excel", "Functional", VP, "1. Click Export to excel", "-", "Excel file downloads", "Low")
add("VEN-19", V, "Delete vendor - cancel", "Functional / CRUD-Delete", VP, "1. Click delete\n2. Cancel", "-", "Record not deleted", "Medium")
add("VEN-20", V, "Delete vendor - confirm", "Positive / CRUD-Delete", VP, "1. Click delete\n2. OK", "QA Vendor Min Edited", "Record removed", "High")
add("VEN-21", V, "Vendors available for selection in Invoice & Receipt", "Integration", VP, "1. Compare vendor list with Vendor dropdown on Add Invoice and Add receipt", "-", "All vendors selectable", "High")
add("VEN-22", V, "Clear search", "Functional", VP, "1. Search 'Beta'\n2. Click Clear", "Beta", "Search box cleared; full list shown", "Low")

# ---------------- Invoice / Receipt ----------------
for PRE, mod, nm, cat, wrong in [("INV", "Invoices", "Invoice", "Income", "Expense"), ("REC", "Receipts", "Receipt", "Expense", "Income")]:
    P0 = PRE_LOGIN + f"; {cat} category 'QA ... Cat' and vendor 'QA Vendor Alpha' exist"
    add(f"{PRE}-01", mod, f"Add {nm} form UI", "UI", P0, f"1. Open {mod} > Add {nm.lower()}", "-", "All fields present; mandatory fields marked", "Low")
    add(f"{PRE}-02", mod, "Save with empty form", "Negative / Mandatory", P0, "1. Click Save on empty form", "All blank",
        "Not saved; required messages for every mandatory field including Category", "High")
    add(f"{PRE}-03", mod, f"Create valid {nm.lower()}", "Positive / CRUD-Create", P0,
        f"1. Select {cat} category\n2. Title / Title(ar)\n3. Vendor\n4. Date (today)\n5. Line item + amount 1000\n6. Amount in words\n7. Save",
        f"QA {nm} Valid 01 / 1000", f"{nm} saved and listed with ID, title, vendor, category, date", "High")
    add(f"{PRE}-04", mod, "Save without selecting Category", "Negative / Mandatory", P0, "1. Fill all fields except Category\n2. Save",
        f"QA {nm} NoCat", "Category required message; not saved", "High")
    add(f"{PRE}-05", mod, "Total amount with tax %", "Functional / Calculation", P0, "1. Enter amount\n2. Enter tax %\n3. Read Total Amount",
        "1000@10%, 1000@0%, 100@18%, 1000@5%", "Total = amount x (1 + tax/100): 1100, 1000, 118, 1050", "Critical")
    add(f"{PRE}-06", mod, "Multiple line items summed", "Functional / Calculation", P0, "1. Amount 500\n2. Click + (Add New)\n3. Second amount 300",
        "500 + 300", "New line item row added; Total = 800", "High")
    add(f"{PRE}-07", mod, "Negative amount", "Negative / Boundary", P0, "1. Fill valid form with amount -500\n2. Save", "-500", "Rejected; not saved", "High")
    add(f"{PRE}-08", mod, "Non-numeric amount", "Negative / Field validation", P0, "1. Fill valid form with amount 'abc'\n2. Save", "abc", "Numeric validation message; no server error", "High")
    add(f"{PRE}-09", mod, "Tax above 100%", "Boundary", P0, "1. Valid form, tax 150\n2. Save", "150", "Tax limited to 0-100; not saved", "Medium")
    add(f"{PRE}-10", mod, "Zero amount", "Boundary", P0, "1. Valid form, amount 0\n2. Save", "0", "Rejected (amount must be > 0)", "Medium")
    add(f"{PRE}-11", mod, f"Category dropdown lists only {cat} categories", "Functional", P0, "1. Open Add form\n2. Expand Category", "-",
        f"No {wrong} categories listed", "High")
    add(f"{PRE}-12", mod, "List page columns and actions (edit/delete support)", "UI / CRUD", P0, f"1. Open {nm} list\n2. Check columns & action buttons", "-",
        "Columns correctly labelled; Edit / Delete actions available", "Medium")
    add(f"{PRE}-13", mod, f"View {nm.lower()} details", "Functional", P0 + f"; 'QA {nm} Valid 01' exists", "1. Click title in list", "-", "Detail page shows saved data", "Medium")
    add(f"{PRE}-14", mod, "Search by title", "Functional", P0, "1. Search 'Valid 01'", "Valid 01", "Only matching records", "Medium")
    add(f"{PRE}-15", mod, "Dashboard totals reflect saved records", "Integration", P0 + f"; at least one {nm.lower()} saved", "1. Open Dashboard",
        "-", f"{nm} count/amount tiles updated", "Medium")
    add(f"{PRE}-16", mod, "Export to Excel", "Functional", P0, "1. Click Export to excel", "-", "File downloads", "Low")
