import sys
import html
import logging
import re
from pathlib import Path
from datetime import datetime

import pandas as pd
import schedule
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.automation.automation_service import AutomationService
from app.automation.backup_service import BackupService
from app.automation.scheduler import AutomationScheduler
from app.database.customer_repository import CustomerRepository
from app.database.database_manager import DatabaseManager
from app.database.invoice_repository import InvoiceRepository
from app.database.order_repository import OrderRepository
from app.database.payment_repository import PaymentRepository
from app.database.product_repository import ProductRepository
from app.database.workspace_manager import WorkspaceManager
from app.llm.business_assistant import BusinessAssistant
from app.reports.report_generator import ReportGenerator

log = logging.getLogger("businessops.ui")

st.set_page_config(page_title="BusinessOps", page_icon="◆", layout="wide",
                   initial_sidebar_state="expanded")


# ------------------------------------------------------------------
# STYLE
# ------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root{--bg:#0f0e13;--panel:#18161e;--line:#2a2633;--text:#f4f1fa;--muted:#9b94a8;
--accent:#8b5cf6;--good:#10b981;--warn:#f59e0b;--bad:#f87171;}
html,body,.stApp,[class*="css"]{font-family:'Plus Jakarta Sans',system-ui,sans-serif;}
.stApp{background:var(--bg);color:var(--text);}
.main .block-container{max-width:1400px;padding:2rem 2rem 4rem;}
[data-testid="stSidebar"]{background:#14121a;border-right:1px solid var(--line);}
#MainMenu,footer{visibility:hidden;}

.brand{font-size:26px;font-weight:800;letter-spacing:-.8px;}
.brand span{color:var(--accent);}
.brand-sub{font-size:12px;color:var(--muted);margin:2px 0 22px;}
.status{margin-top:28px;padding:10px 14px;border-radius:10px;background:#1c1924;
border:1px solid var(--line);color:var(--good);font-size:13px;font-weight:600;}

.page-title{font-size:30px;font-weight:800;letter-spacing:-.8px;margin:0;}
.page-desc{color:var(--muted);font-size:15px;margin:4px 0 22px;max-width:70ch;}

.kpi{background:var(--panel);border:1px solid var(--line);border-radius:14px;
padding:18px 20px;min-height:122px;}
.kpi-top{display:flex;justify-content:space-between;align-items:center;color:var(--muted);
font-size:13px;font-weight:600;}
.kpi-icon{width:30px;height:30px;border-radius:8px;display:flex;align-items:center;
justify-content:center;font-size:15px;}
.kpi-value{font-size:28px;font-weight:800;letter-spacing:-.7px;margin:10px 0 2px;}
.kpi-hint{color:var(--muted);font-size:12.5px;}

[data-testid="stVerticalBlockBorderWrapper"]{border-radius:14px!important;
border-color:var(--line)!important;background:var(--panel);}
.panel-title{font-size:16px;font-weight:700;margin:0;}
.panel-desc{color:var(--muted);font-size:13px;margin:2px 0 12px;}

.bar{height:10px;border-radius:99px;background:#2a2633;overflow:hidden;margin:14px 0 8px;}
.bar>div{height:100%;border-radius:99px;background:var(--good);}
.big{font-size:34px;font-weight:800;letter-spacing:-1px;}
.row{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid var(--line);
font-size:14px;}
.row:last-child{border-bottom:none;}
.row small{color:var(--muted);display:block;font-size:12px;}
.pill{padding:2px 10px;border-radius:99px;font-size:12px;font-weight:600;}
.attn-row{display:flex;justify-content:space-between;align-items:center;gap:16px;
padding:14px 2px;border-bottom:1px solid var(--line);}
.attn-row:last-child{border-bottom:none;}
.attn-name{font-size:15px;font-weight:700;line-height:1.3;}
.attn-sub{font-size:12.5px;color:var(--muted);margin-top:4px;}
.attn-right{text-align:right;display:flex;flex-direction:column;align-items:flex-end;gap:6px;}
.attn-amt{font-size:15px;font-weight:800;}
.pill-unpaid{background:#3b1d1d;color:var(--bad);}
.pill-partly{background:#3b2f14;color:var(--warn);}
.pill-paid{background:#12332a;color:var(--good);}
.pill.Unpaid{background:#3b1d1d;color:var(--bad);}
.pill.Partly\\ paid{background:#3b2f14;color:var(--warn);}
.pill.Paid{background:#12332a;color:var(--good);}
.tip{background:#1d1830;border:1px solid #3d2f66;border-radius:12px;padding:14px 16px;
font-size:14px;line-height:1.65;color:#cfc8de;}

.kpi{position:relative;overflow:hidden;border-radius:16px;padding:16px 18px 8px;min-height:150px;}
.tone-purple{background:linear-gradient(160deg,#2b1d4d,#18161e 72%);border-color:#4b3473;}
.tone-teal{background:linear-gradient(160deg,#10343a,#18161e 72%);border-color:#1e5d66;}
.tone-indigo{background:linear-gradient(160deg,#1f2150,#18161e 72%);border-color:#37398a;}
.tone-violet{background:linear-gradient(160deg,#2e1a45,#18161e 72%);border-color:#5a3a82;}
.kpi-row{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-top:8px;}
.kpi-row .kpi-value{margin:0;}
.chip{font-size:12px;font-weight:700;color:#34d399;}
.kpi svg{display:block;width:100%;height:54px;margin-top:8px;}
.perf{width:100%;border-collapse:collapse;font-size:14px;}
.perf th{color:var(--muted);font-weight:600;font-size:12px;text-align:left;padding:8px 6px;border-bottom:1px solid var(--line);}
.perf td{padding:11px 6px;border-bottom:1px solid #221f2b;white-space:nowrap;}
.av{width:28px;height:28px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;margin-right:10px;vertical-align:middle;background:#2d2447;color:#c4b5fd;}
.badge{padding:3px 10px;border-radius:99px;font-size:12px;font-weight:600;border:1px solid;}
.b-good{background:#12332a;color:#34d399;border-color:#1b5a46;}
.b-warn{background:#3b2f14;color:#fbbf24;border-color:#6b5217;}
.b-key{background:#2d2050;color:#c4b5fd;border-color:#4b3473;}
.onboard-logo{font-size:42px;font-weight:800;letter-spacing:-1.5px;text-align:center;margin-top:6vh;}
.onboard-logo span{color:var(--accent);}
.onboard-sub{color:var(--muted);font-size:15px;text-align:center;margin:8px 0 26px;}
.business-box{margin:0 0 16px;padding:12px 14px;border-radius:10px;background:#1c1924;border:1px solid var(--line);}
.business-name{font-size:13px;font-weight:700;}
.business-type{font-size:11px;color:var(--muted);margin-top:3px;}
:focus-visible{outline:2px solid var(--accent)!important;outline-offset:2px;}
@media (max-width:768px){.main .block-container{padding:1rem;}.page-title{font-size:24px;}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important;}}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# WORKSPACE (each business has its own database and folders)
# ------------------------------------------------------------------
SYMBOLS = {"PKR": "₨", "USD": "$", "EUR": "€", "GBP": "£"}
SYM = "₨"

workspace_manager = WorkspaceManager()
existing_workspaces = workspace_manager.list_workspaces()
valid_workspace_ids = {w["workspace_id"] for w in existing_workspaces}

active_workspace_id = st.session_state.get("workspace_id")
if active_workspace_id not in valid_workspace_ids:
    active_workspace_id = None
    st.session_state.pop("workspace_id", None)
    st.session_state.pop("workspace_profile", None)


def reset_session_data():
    """Never carry one business's chat or report into another business."""
    for key in ("chat", "report_text", "pending_q", "import_summary"):
        st.session_state.pop(key, None)


def open_workspace(profile):
    log.info("Workspace opened: %s", profile["workspace_id"])
    st.session_state["workspace_id"] = profile["workspace_id"]
    st.session_state["workspace_profile"] = profile
    reset_session_data()


def create_new_workspace(business_name, business_type, currency):
    """Create and open a completely empty business workspace."""
    profile = workspace_manager.create_workspace(
        business_name=business_name.strip(),
        business_type=business_type.strip(),
        currency=currency,
    )
    DatabaseManager(workspace_manager.get_database_path(profile["workspace_id"])).create_tables()
    log.info("Workspace created: %s", profile["workspace_id"])
    open_workspace(profile)
    return profile


if active_workspace_id is None:
    _, mid, _ = st.columns([1, 1.6, 1])
    with mid:
        st.markdown('<div class="onboard-logo">Business<span>Ops</span></div>'
                    '<div class="onboard-sub">Run your business in one place</div>',
                    unsafe_allow_html=True)
        tab_new, tab_existing = st.tabs(["Create your business", "Open existing business"])

        with tab_new:
            with st.container(border=True):
                panel_title = "Set up your business"
                st.markdown(f'<p class="panel-title" style="font-size:20px">{panel_title}</p>'
                            '<p class="panel-desc">You start with a clean, empty workspace. '
                            'Add your data by importing files in BusinessOps.</p>',
                            unsafe_allow_html=True)
                with st.form("new_business_form", border=False):
                    business_name = st.text_input("Business name", placeholder="e.g. ABC Traders")
                    business_type = st.text_input("Business type",
                                                  placeholder="e.g. Retail, Service, E-commerce")
                    currency = st.selectbox("Currency", list(SYMBOLS))
                    submitted = st.form_submit_button("Create business workspace",
                                                      type="primary", use_container_width=True)
                if submitted:
                    if not business_name.strip():
                        st.error("Enter your business name to continue.")
                    elif not business_type.strip():
                        st.error("Enter your business type to continue.")
                    else:
                        try:
                            create_new_workspace(business_name, business_type, currency)
                            st.rerun()
                        except Exception as error:
                            log.exception("Workspace creation failed")
                            st.error(f"The workspace could not be created: {error}")

        with tab_existing:
            if not existing_workspaces:
                st.info("No businesses yet. Create your first one in the other tab.")
            for ws in existing_workspaces:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.markdown(f"**{ws['business_name']}**  \n"
                                f"{ws['business_type']} · {ws['currency']}")
                    if c2.button("Open", key=f"open_{ws['workspace_id']}",
                                 use_container_width=True):
                        open_workspace(ws)
                        st.rerun()
    st.stop()


# ------------------------------------------------------------------
# ACTIVE WORKSPACE
# ------------------------------------------------------------------
workspace_id = active_workspace_id
workspace_profile = workspace_manager.get_workspace_profile(workspace_id)

if workspace_profile is None:
    st.session_state.pop("workspace_id", None)
    st.error("This business could not be found. Refresh the page and pick another one.")
    st.stop()

st.session_state["workspace_id"] = workspace_id
st.session_state["workspace_profile"] = workspace_profile
SYM = SYMBOLS.get(workspace_profile.get("currency"), f"{workspace_profile.get('currency', '')} ")

workspace_path = workspace_manager.get_workspace_path(workspace_id)
database_path = workspace_manager.get_database_path(workspace_id)
input_folder = workspace_path / "input"
processed_folder = workspace_path / "processed"
archive_folder = workspace_path / "archive"
backup_folder = workspace_path / "backup"


# ------------------------------------------------------------------
# SERVICES (created once per business, reused on every click)
# ------------------------------------------------------------------
@st.cache_resource
def load_services(workspace_id, database_path, input_folder, processed_folder,
                  archive_folder, backup_folder):
    db = DatabaseManager(database_path)
    db.create_tables()
    auto = AutomationService(
        input_folder=input_folder, processed_folder=processed_folder,
        archive_folder=archive_folder, database_path=database_path,
        backup_folder=backup_folder,
    )
    return {
        "db": db,
        "automation": auto,
        "backup": BackupService(database_path=database_path, backup_folder=backup_folder),
        "scheduler": AutomationScheduler(automation_service=auto),
        "reports": ReportGenerator(database_manager=db),
    }


def get_services(wid):
    """Services for ONE business. Every path is derived from the workspace id."""
    base = workspace_manager.get_workspace_path(wid)
    return load_services(wid, str(workspace_manager.get_database_path(wid)),
                         str(base / "input"), str(base / "processed"),
                         str(base / "archive"), str(base / "backup"))


S = get_services(workspace_id)
db = S["db"]


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------
def money(v):
    try:
        return f"{SYM}{float(v):,.0f}"
    except (ValueError, TypeError):
        return f"{SYM}0"


def esc(v):
    return html.escape(str(v))


def greeting():
    h = datetime.now().hour
    return "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"


@st.cache_data(ttl=10, show_spinner=False)
def load_data(workspace_id):
    """Read everything once and work out every number the UI needs.

    The database is looked up from workspace_id itself, so the cache key and
    the data source can never disagree (no cross-business leakage)."""
    wdb = get_services(workspace_id)["db"]
    customers, products = wdb.get_customers(), wdb.get_products()
    orders, invoices, payments = wdb.get_orders(), wdb.get_invoices(), wdb.get_payments()

    cust = {c[0]: c for c in customers}
    prod = {p[0]: p for p in products}

    order_rows, product_sales, customer_sales = [], {}, {}
    for oid, cid, pid, qty in orders:
        p = prod.get(pid)
        amount = float(p[2]) * int(qty) if p else 0
        pname = p[1] if p else "Unknown product"
        cname = cust[cid][1] if cid in cust else "Unknown customer"
        order_rows.append({"Order": oid, "Customer": cname, "Product": pname,
                           "Quantity": qty, "Amount": amount})
        product_sales[pname] = product_sales.get(pname, 0) + amount
        customer_sales[cname] = customer_sales.get(cname, 0) + amount

    paid_by_invoice = {}
    for _, inv_id, amt in payments:
        paid_by_invoice[inv_id] = paid_by_invoice.get(inv_id, 0) + float(amt)

    order_customer = {r["Order"]: r["Customer"] for r in order_rows}
    invoice_rows = []
    for inv_id, oid, total in invoices:
        total = float(total)
        paid = paid_by_invoice.get(inv_id, 0)
        left = max(total - paid, 0)
        status = "Paid" if left <= 0 else "Partly paid" if paid > 0 else "Unpaid"
        invoice_rows.append({"Invoice": inv_id, "Order": oid,
                             "Customer": order_customer.get(oid, "Unknown customer"),
                             "Total": total, "Paid": paid, "Remaining": left,
                             "Status": status})

    revenue = sum(r["Amount"] for r in order_rows)
    invoiced = sum(r["Total"] for r in invoice_rows)
    received = sum(float(p[2]) for p in payments)
    return {
        "customers": customers, "products": products, "orders": order_rows,
        "invoices": invoice_rows, "payments": payments,
        "revenue": revenue, "invoiced": invoiced, "received": received,
        "outstanding": sum(r["Remaining"] for r in invoice_rows),
        "collected_pct": ((invoiced - sum(r["Remaining"] for r in invoice_rows))
                          / invoiced * 100) if invoiced else 0,
        "avg_order": revenue / len(order_rows) if order_rows else 0,
        "product_sales": product_sales, "customer_sales": customer_sales,
    }


try:
    D = load_data(workspace_id)
except Exception:
    log.exception("Could not load data for workspace %s", workspace_id)
    st.error("We couldn't open this business's data. Refresh the page. If it keeps "
             "happening, create a backup copy of the business and contact support.")
    st.stop()


# ------------------------------------------------------------------
# UI PIECES
# ------------------------------------------------------------------
def page_header(title, desc):
    st.markdown(f'<h1 class="page-title">{esc(title)}</h1>'
                f'<p class="page-desc">{esc(desc)}</p>', unsafe_allow_html=True)


def kpi(icon, color, label, value, hint, spark="", tone="", chip=""):
    chip_html = f'<span class="chip">{esc(chip)}</span>' if chip else ""
    st.markdown(
        f'<div class="kpi {tone}"><div class="kpi-top"><span>{esc(label)}</span>'
        f'<span class="kpi-icon" style="background:{color}22;color:{color}">{icon}</span></div>'
        f'<div class="kpi-row"><span class="kpi-value">{esc(value)}</span>{chip_html}</div>'
        f'<div class="kpi-hint">{esc(hint)}</div>{spark}</div>', unsafe_allow_html=True)


def panel_head(title, desc):
    st.markdown(f'<p class="panel-title">{esc(title)}</p>'
                f'<p class="panel-desc">{esc(desc)}</p>', unsafe_allow_html=True)


def empty(msg, action=None):
    st.info(msg + (f"  \n{action}" if action else ""), icon="ℹ️")


def table(df, key, money_cols=()):
    """Searchable, downloadable table."""
    if df.empty:
        return
    c1, c2 = st.columns([3, 1])
    q = c1.text_input("Search", key=f"q_{key}", placeholder="Type to filter this table…",
                      label_visibility="collapsed")
    c2.download_button("Download CSV", df.to_csv(index=False), f"{key}.csv", "text/csv",
                       use_container_width=True, key=f"dl_{key}")
    if q:
        mask = df.astype(str).apply(lambda col: col.str.contains(q, case=False, na=False))
        df = df[mask.any(axis=1)]
    shown = df.copy()
    for c in money_cols:
        shown[c] = shown[c].map(money)
    st.dataframe(shown, use_container_width=True, hide_index=True)
    st.caption(f"Showing {len(df)} record(s)")


def add_manual_customer():
    with st.form("manual_customer_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        customer_name = c1.text_input("Customer name")
        customer_email = c2.text_input("Email address")
        saved = st.form_submit_button("Add customer", type="primary")
    if saved:
        name = customer_name.strip()
        email = customer_email.strip()
        if not name or not email:
            st.error("Customer name and email are required.")
            return
        if "@" not in email:
            st.error("Enter a valid email address.")
            return
        try:
            CustomerRepository(db).save_customers([{"name": name, "email": email}])
            st.success(f"Customer '{name}' added.")
            st.rerun()
        except Exception as exc:
            st.error(f"Unable to add customer: {exc}")


def add_manual_product():
    with st.form("manual_product_form", clear_on_submit=True):
        name = st.text_input("Product name")
        price = st.number_input("Price", min_value=0.0, step=1.0, format="%.2f")
        saved = st.form_submit_button("Add product", type="primary")
    if saved:
        product_name = name.strip()
        if not product_name:
            st.error("Product name is required.")
            return
        try:
            ProductRepository(db).save_products([{"name": product_name, "price": float(price)}])
            st.success(f"Product '{product_name}' added.")
            st.rerun()
        except Exception as exc:
            st.error(f"Unable to add product: {exc}")


def add_manual_order():
    customers = db.get_customers()
    products = db.get_products()
    if not customers or not products:
        st.info("Add at least one customer and one product before creating an order.")
        return
    with st.form("manual_order_form", clear_on_submit=True):
        customer_id = st.selectbox("Customer", [c[0] for c in customers], format_func=lambda cid: next(c[1] for c in customers if c[0] == cid))
        product_id = st.selectbox("Product", [p[0] for p in products], format_func=lambda pid: next(p[1] for p in products if p[0] == pid))
        quantity = st.number_input("Quantity", min_value=1, step=1)
        saved = st.form_submit_button("Add order", type="primary")
    if saved:
        try:
            OrderRepository(db).save_order({"customer_id": int(customer_id), "product_id": int(product_id), "quantity": int(quantity)})
            st.success("Order added.")
            st.rerun()
        except Exception as exc:
            st.error(f"Unable to add order: {exc}")


def add_manual_invoice():
    orders = db.get_orders()
    if not orders:
        st.info("Add at least one order before creating an invoice.")
        return
    with st.form("manual_invoice_form", clear_on_submit=True):
        order_id = st.selectbox("Order", [o[0] for o in orders], format_func=lambda oid: f"Order #{oid}")
        total_amount = st.number_input("Invoice total", min_value=0.0, step=1.0, format="%.2f")
        saved = st.form_submit_button("Add invoice", type="primary")
    if saved:
        try:
            InvoiceRepository(db).save_invoice({"order_id": int(order_id), "total_amount": float(total_amount)})
            st.success("Invoice added.")
            st.rerun()
        except Exception as exc:
            st.error(f"Unable to add invoice: {exc}")


def add_manual_payment():
    invoices = db.get_invoices()
    if not invoices:
        st.info("Add at least one invoice before recording a payment.")
        return
    with st.form("manual_payment_form", clear_on_submit=True):
        invoice_id = st.selectbox("Invoice", [i[0] for i in invoices], format_func=lambda iid: f"Invoice #{iid}")
        amount = st.number_input("Amount received", min_value=0.01, step=1.0, format="%.2f")
        saved = st.form_submit_button("Add payment", type="primary")
    if saved:
        try:
            PaymentRepository(db).save_payment({"invoice_id": int(invoice_id), "amount": float(amount)})
            st.success("Payment added.")
            st.rerun()
        except Exception as exc:
            st.error(f"Unable to add payment: {exc}")


# ------------------------------------------------------------------
# IMPORT (upload -> save into THIS business's input folder -> existing pipeline)
# ------------------------------------------------------------------
ALLOWED_UPLOADS = ["csv", "xlsx", "xls", "json"]
MAX_UPLOAD_MB = 50
IMPORT_HINT = "Add data from the Automation page, under Import your data."
FILE_KINDS = {"Detect from the file name": None, "Customers": "customers",
              "Products or services": "products", "Orders": "orders",
              "Invoices": "invoices", "Payments": "payments"}


def record_counts(wdb):
    return {"customers": len(wdb.get_customers()), "products": len(wdb.get_products()),
            "orders": len(wdb.get_orders()), "invoices": len(wdb.get_invoices()),
            "payments": len(wdb.get_payments())}


def save_upload(uploaded, kind=None):
    """Save one uploaded file into the active business's input folder.

    kind: optional record type chosen by the client; the file is stored under the
    standard name for that type (e.g. customers.csv) so the processors recognise it."""
    name = Path(uploaded.name).name
    suffix = Path(name).suffix.lower()
    if suffix.lstrip(".") not in ALLOWED_UPLOADS:
        raise ValueError("this file type is not supported. Use CSV, Excel or JSON")
    if uploaded.size == 0:
        raise ValueError("the file is empty")
    if uploaded.size > MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError(f"the file is larger than {MAX_UPLOAD_MB} MB")
    safe = f"{kind}{suffix}" if kind else re.sub(r"[^\w.\- ]", "_", name).strip(" .")
    if not safe:
        raise ValueError("the file name is not valid")
    input_folder.mkdir(parents=True, exist_ok=True)
    target = (input_folder / safe).resolve()
    if target.parent != input_folder.resolve():
        raise ValueError("the file name is not valid")
    replaced = target.exists()
    target.write_bytes(uploaded.getbuffer())
    log.info("Upload saved: %s (workspace %s, %d bytes)", safe, workspace_id, uploaded.size)
    return safe, replaced


def result_row(result):
    """Turn whatever the processor returned for one file into a flat table row."""
    data = result if isinstance(result, dict) else (
        vars(result) if hasattr(result, "__dict__") else {"result": result})
    return {str(k): (v if isinstance(v, (str, int, float, bool)) or v is None else str(v))
            for k, v in data.items()}


def attention_notes(rows):
    """Pick out anything the processor reported as an error, invalid row or rejection."""
    notes = []
    for row in rows:
        for key, value in row.items():
            if any(w in key.lower() for w in ("error", "invalid", "reject", "fail", "skip")) \
                    and value not in (None, "", 0, "0", False, "False", "[]", "{}"):
                text = str(value)
                notes.append(f"{key.replace('_', ' ').capitalize()}: "
                             f"{text[:300]}{'…' if len(text) > 300 else ''}")
    return notes


def run_import(files, kinds):
    """Save each uploaded file and run the existing processing pipeline for it."""
    summary = {"workspace": workspace_id, "saved": [], "replaced": [], "problems": [],
               "processed": 0, "added": {}, "rows": [], "failed": False, "detail": ""}
    before = record_counts(db)

    for i, f in enumerate(files):
        try:
            name, replaced = save_upload(f, kinds.get(i))
        except ValueError as problem:
            log.warning("Upload rejected (%s): %s", f.name, problem)
            summary["problems"].append(f"{f.name}: {problem}.")
            continue
        except OSError as problem:
            log.exception("Could not save upload %s", f.name)
            summary["problems"].append(f"{f.name}: the file could not be saved.")
            summary["detail"] += f"{problem}\n"
            continue
        summary["saved"].append(name)
        if replaced:
            summary["replaced"].append(name)
        try:
            with st.spinner(f"Checking, cleaning and saving {name}…"):
                results = S["automation"].process_pending_files()
            summary["processed"] += len(results) if results else 0
            summary["rows"] += [result_row(r) for r in (results or [])]
        except Exception as error:
            log.exception("Import failed for %s in workspace %s", name, workspace_id)
            summary["failed"] = True
            summary["detail"] += f"{name}: {error}\n"

    load_data.clear()
    after = record_counts(db)
    summary["added"] = {k: after[k] - before[k] for k in after if after[k] != before[k]}
    log.info("Import finished for %s: processed=%s added=%s", workspace_id,
             summary["processed"], summary["added"])
    st.session_state["import_summary"] = summary


def show_import_summary(sm):
    for problem in sm["problems"]:
        st.error(problem, icon="🚫")
    for name in sm["replaced"]:
        st.info(f"{name} was already waiting, so it was replaced with your new upload.")

    if sm["failed"]:
        st.error("A file was uploaded, but it could not be imported. Nothing was lost: "
                 "it is still waiting, and you can try again with Process files now below.",
                 icon="⚠️")
    if sm["saved"] and sm["processed"] > 0:
        st.success(f"Import complete. {sm['processed']} file(s) processed and saved to this "
                   "business.", icon="✅")
        if sm["added"]:
            labels = {"customers": "Customers", "products": "Products", "orders": "Orders",
                      "invoices": "Invoices", "payments": "Payments"}
            for key, change in sm["added"].items():
                st.markdown(f'<div class="row"><div>{labels[key]} '
                            f'{"added" if change > 0 else "removed"}</div>'
                            f'<b>{change:+,}</b></div>', unsafe_allow_html=True)
        else:
            st.info("No new records were added. The file may only contain records you already "
                    "have, or rows that did not pass the checks. See the details below.")
    elif sm["saved"] and not sm["failed"]:
        st.info("Your file was uploaded, but there was nothing new to process. "
                "Check that it contains your records and that you chose the right type.")

    notes = attention_notes(sm["rows"])
    if notes:
        st.warning("Some rows or files need your attention:\n\n" +
                   "\n".join(f"- {n}" for n in notes))
    if sm["rows"]:
        with st.expander("File details"):
            st.dataframe(pd.DataFrame(sm["rows"]), use_container_width=True, hide_index=True)
    if sm["detail"]:
        with st.expander("Technical details (for support)"):
            st.code(sm["detail"])


def import_panel():
    nonce = st.session_state.get("upload_nonce", 0)
    with st.container(border=True):
        panel_head("Import your data",
                   "Upload your CSV, Excel or JSON files. BusinessOps checks and cleans "
                   "them, then saves the records to this business only.")
        files = st.file_uploader("Choose one or more files", type=ALLOWED_UPLOADS,
                                 accept_multiple_files=True,
                                 key=f"upload_{workspace_id}_{nonce}",
                                 label_visibility="collapsed")
        kinds = {}
        if files:
            st.caption("What does each file contain?")
            for i, f in enumerate(files):
                n1, n2 = st.columns([2, 1.4])
                n1.markdown(f"**{f.name}**")
                choice = n2.selectbox("Contains", list(FILE_KINDS),
                                      key=f"kind_{workspace_id}_{nonce}_{i}",
                                      label_visibility="collapsed")
                kinds[i] = FILE_KINDS[choice]
        if st.button("Check and import", type="primary", use_container_width=True,
                     disabled=not files):
            run_import(files, kinds)
            st.session_state["upload_nonce"] = nonce + 1
            st.rerun()
        summary = st.session_state.get("import_summary")
        if summary and summary.get("workspace") == workspace_id:
            show_import_summary(summary)


# ------------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------------
NAV = {"Overview": "🏠", "Customers": "👥", "Products": "📦", "Orders": "🧾",
       "Invoices": "📄", "Payments": "💳", "Reports": "📊",
       "AI Copilot": "✨", "Automation": "⚙️"}

with st.sidebar:
    st.markdown('<div class="brand">Business<span>Ops</span></div>'
                '<div class="brand-sub">Run your business in one place</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="business-box"><div class="business-name">'
                f'{esc(workspace_profile["business_name"])}</div><div class="business-type">'
                f'{esc(workspace_profile["business_type"])} · {esc(workspace_profile["currency"])}'
                f'</div></div>', unsafe_allow_html=True)
    page = st.radio("Go to", list(NAV), format_func=lambda n: f"{NAV[n]}  {n}",
                    label_visibility="collapsed")
    st.markdown('<div class="status">● Everything is running</div>', unsafe_allow_html=True)
    if st.button("Refresh data", use_container_width=True):
        load_data.clear()
        st.rerun()
    if st.button("Switch business", use_container_width=True):
        log.info("Workspace closed: %s", workspace_id)
        schedule.clear()  # a schedule belongs to one business; never carry it over
        for key in ("workspace_id", "workspace_profile"):
            st.session_state.pop(key, None)
        reset_session_data()
        load_data.clear()
        st.rerun()


# ==================================================================
# OVERVIEW
# ==================================================================
from itertools import accumulate

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


def sparkline(vals, color):
    """Small smooth area line drawn as SVG (no extra library needed)."""
    vals = [float(v) for v in vals]
    if len(vals) > 40:
        step = len(vals) / 40
        vals = [vals[int(i * step)] for i in range(40)] + [vals[-1]]
    if len(vals) < 2 or max(vals) == min(vals):
        return ""
    w, h, pad = 240, 54, 4
    lo, hi = min(vals), max(vals)
    pts = [(i * w / (len(vals) - 1), h - pad - (v - lo) / (hi - lo) * (h - 2 * pad))
           for i, v in enumerate(vals)]
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    gid = "g" + color.strip("#")
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none"><defs>'
            f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{color}" stop-opacity=".35"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>'
            f'<path d="{d} L{w},{h} L0,{h} Z" fill="url(#{gid})"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.2" '
            f'stroke-linecap="round"/></svg>')


def style_fig(fig, height):
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=10, b=0), showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9b94a8", family="Plus Jakarta Sans, sans-serif"),
        hoverlabel=dict(bgcolor="#1c1924", bordercolor="#4b3473", font_color="#f4f1fa"))
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#2a2633")
    fig.update_yaxes(gridcolor="#2a2633", zeroline=False)
    return fig


def show(fig):
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


if page == "Overview":
    page_header(f"{greeting()} 👋",
                f"{workspace_profile['business_name']} · {datetime.now():%d %B %Y}")

    if not D["customers"] and not D["orders"]:
        st.info("This business is empty. Open the **Automation** page and upload your "
                "first file under **Import your data**.", icon="👋")

    if not HAS_PLOTLY:
        st.error("The charts need one extra package. Run `pip install plotly` "
                 "in your terminal, then restart the app.")
        st.stop()

    orders = sorted(D["orders"], key=lambda r: r["Order"])
    amounts = [r["Amount"] for r in orders]
    running = list(accumulate(amounts))
    pay_run = list(accumulate(float(p[2]) for p in D["payments"]))
    owed_run = list(accumulate(i["Remaining"] for i in D["invoices"]))
    open_inv = sum(1 for i in D["invoices"] if i["Remaining"] > 0)

    # ---------------- KPI row ----------------
    k = st.columns(4)
    with k[0]:
        kpi(SYM, "#a78bfa", "Total sales", money(D["revenue"]), "Value of all orders",
            sparkline(running, "#a78bfa"), "tone-purple", f"avg {money(D['avg_order'])}")
    with k[1]:
        buyers = len({r["Customer"] for r in orders})
        kpi("🧾", "#22d3ee", "Orders", str(len(orders)),
            f"Placed by {buyers} of {len(D['customers'])} customers",
            sparkline(range(1, len(orders) + 1), "#22d3ee"), "tone-teal",
            "order" if len(orders) == 1 else "orders")
    with k[2]:
        kpi("✅", "#818cf8", "Money collected", f"{D['collected_pct']:.0f}%",
            f"of {money(D['invoiced'])} invoiced", sparkline(pay_run, "#818cf8"), "tone-indigo",
            f"{money(D['received'])} in")
    with k[3]:
        kpi("⏳", "#c084fc", "Waiting to be paid", money(D["outstanding"]),
            "Still owed on invoices", sparkline(owed_run, "#c084fc"), "tone-violet",
            f"{open_inv} unpaid invoice" + ("" if open_inv == 1 else "s"))

    st.write("")

    # ---------------- Growth + donut ----------------
    left, right = st.columns([2.1, 1])

    with left, st.container(border=True):
        h1, h2 = st.columns([2, 1.3])
        with h1:
            panel_head("Sales growth", "How your sales build up, order by order.")
        with h2:
            view = st.radio("View", ["Running total", "Per order"], horizontal=True,
                            label_visibility="collapsed")
        if orders:
            ys = running if view == "Running total" else amounts
            xs = [r["Order"] for r in orders]
            top_i = ys.index(max(ys))
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode="lines", fill="tozeroy",
                line=dict(color="#a78bfa", width=3, shape="spline", smoothing=1),
                fillcolor="rgba(139,92,246,.20)",
                hovertemplate="Order #%{x}<br><b>" + SYM + "%{y:,.0f}</b><extra></extra>"))
            fig.add_trace(go.Scatter(
                x=[xs[top_i]], y=[ys[top_i]], mode="markers", hoverinfo="skip",
                marker=dict(size=12, color="#22d3ee", line=dict(color="#fff", width=2))))
            style_fig(fig, 330)
            fig.update_yaxes(tickprefix=SYM, tickformat="~s")
            fig.update_xaxes(title_text="Order number", dtick=1 if len(xs) < 12 else None)
            show(fig)
        else:
            empty("No sales yet.", "Add your first order and this chart will fill in.")

    with right, st.container(border=True):
        panel_head("Sales by product", "Which products earn the most.")
        if D["product_sales"]:
            ranked = sorted(D["product_sales"].items(), key=lambda x: x[1], reverse=True)
            labels = [n for n, _ in ranked[:4]]
            vals = [v for _, v in ranked[:4]]
            if len(ranked) > 4:
                labels.append("Other")
                vals.append(sum(v for _, v in ranked[4:]))
            fig = go.Figure(go.Pie(
                labels=labels, values=vals, hole=0.68, sort=False, textinfo="percent",
                marker=dict(colors=["#22d3ee", "#8b5cf6", "#6366f1", "#c084fc", "#475569"],
                            line=dict(color="#18161e", width=3)),
                hovertemplate="%{label}<br>" + SYM + "%{value:,.0f}<extra></extra>"))
            style_fig(fig, 330)
            fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.05,
                                                           font=dict(size=11)))
            show(fig)
        else:
            empty("No product sales yet.")

    st.write("")

    # ---------------- Customers bar + top customers table ----------------
    b1, b2 = st.columns([1, 1.25])

    with b1, st.container(border=True):
        panel_head("Sales by customer", "Your biggest buyers.")
        if D["customer_sales"]:
            top = sorted(D["customer_sales"].items(), key=lambda x: x[1], reverse=True)[:7]
            fig = go.Figure(go.Bar(
                x=[n[:12] for n, _ in top], y=[v for _, v in top],
                marker=dict(color=[v for _, v in top],
                            colorscale=[[0, "#4f46e5"], [1, "#c084fc"]], line_width=0),
                customdata=[n for n, _ in top],
                hovertemplate="%{customdata}<br><b>" + SYM + "%{y:,.0f}</b><extra></extra>"))
            style_fig(fig, 300)
            fig.update_yaxes(tickprefix=SYM, tickformat="~s")
            show(fig)
        else:
            empty("No customer sales yet.")

    with b2, st.container(border=True):
        panel_head("Top customers", "Who buys the most, and whether they have paid.")
        if D["customer_sales"]:
            owed = {}
            for i in D["invoices"]:
                owed[i["Customer"]] = owed.get(i["Customer"], 0) + i["Remaining"]
            top = sorted(D["customer_sales"].items(), key=lambda x: x[1], reverse=True)[:5]
            rows = ""
            for name, amt in top:
                share = amt / D["revenue"] * 100 if D["revenue"] else 0
                left_amt = owed.get(name, 0)
                badge = (f'<span class="badge b-warn">Owes {esc(money(left_amt))}</span>'
                         if left_amt > 0 else '<span class="badge b-good">Paid up</span>')
                if share >= 25:
                    badge = '<span class="badge b-key">Key account</span> ' + badge
                initials = "".join(w[0] for w in name.split()[:2]).upper()
                rows += (f'<tr><td><span class="av">{esc(initials)}</span>{esc(name)}</td>'
                         f'<td>{esc(money(amt))}</td><td>{share:.0f}%</td><td>{badge}</td></tr>')
            st.markdown(
                '<div style="overflow-x:auto"><table class="perf"><thead><tr>'
                '<th>Customer</th><th>Sales</th><th>Share</th><th>Status</th></tr></thead>'
                f'<tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)
        else:
            empty("No customers with sales yet.")

    st.write("")

    # ---------------- Attention + latest orders ----------------
    c1, c2 = st.columns([1, 1.6])

    with c1, st.container(border=True):
        panel_head("Needs your attention", "Largest unpaid invoices. Follow these up first.")
        due = sorted([i for i in D["invoices"] if i["Remaining"] > 0],
                     key=lambda i: i["Remaining"], reverse=True)[:5]
        if due:
            for i in due:
                slug = {"Unpaid": "pill-unpaid", "Partly paid": "pill-partly"}.get(
                    i["Status"], "pill-paid")
                st.markdown(
                    '<div class="attn-row">'
                    '<div class="attn-left">'
                    f'<div class="attn-name">{esc(i["Customer"])}</div>'
                    f'<div class="attn-sub">Invoice #{esc(i["Invoice"])}</div></div>'
                    '<div class="attn-right">'
                    f'<div class="attn-amt">{esc(money(i["Remaining"]))}</div>'
                    f'<span class="pill {slug}">{esc(i["Status"])}</span></div>'
                    '</div>', unsafe_allow_html=True)
        else:
            st.success("All invoices are paid. Nothing to chase.", icon="✅")

    with c2, st.container(border=True):
        panel_head("Latest orders", "Your 8 most recent orders.")
        if orders:
            df = pd.DataFrame(orders).sort_values("Order", ascending=False).head(8)
            df["Amount"] = df["Amount"].map(money)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            empty("No orders recorded yet.")


# ==================================================================
# LIST PAGES
# ==================================================================
elif page == "Customers":
    page_header("Customers", "Everyone you do business with.")
    with st.container(border=True):
        panel_head("Add customer manually", "Create a new customer record one at a time.")
        add_manual_customer()
    rows = [{"ID": c[0], "Name": c[1], "Email": c[2]} for c in D["customers"]]
    table(pd.DataFrame(rows), "customers") if rows else empty("No customers yet.", IMPORT_HINT)

elif page == "Products":
    page_header("Products", "What you sell and what it costs.")
    with st.container(border=True):
        panel_head("Add product manually", "Create a new product or service record one at a time.")
        add_manual_product()
    rows = [{"ID": p[0], "Name": p[1], "Price": float(p[2])} for p in D["products"]]
    table(pd.DataFrame(rows), "products", ["Price"]) if rows else empty("No products yet.", IMPORT_HINT)

elif page == "Orders":
    page_header("Orders", "Every sale you have recorded.")
    with st.container(border=True):
        panel_head("Add order manually", "Sell one product to one customer in a single step.")
        add_manual_order()
    table(pd.DataFrame(D["orders"]), "orders", ["Amount"]) if D["orders"] else empty("No orders yet.", IMPORT_HINT)

elif page == "Invoices":
    page_header("Invoices", "See what has been paid and what is still owed.")
    with st.container(border=True):
        panel_head("Add invoice manually", "Create an invoice for an existing order.")
        add_manual_invoice()
    if D["invoices"]:
        df = pd.DataFrame(D["invoices"])
        f = st.segmented_control("Show", ["All", "Unpaid", "Partly paid", "Paid"],
                                 default="All")
        if f and f != "All":
            df = df[df["Status"] == f]
        table(df, "invoices", ["Total", "Paid", "Remaining"])
    else:
        empty("No invoices yet.", IMPORT_HINT)

elif page == "Payments":
    page_header("Payments", "Money you have received.")
    with st.container(border=True):
        panel_head("Add payment manually", "Record a payment against an invoice.")
        add_manual_payment()
    if D["payments"]:
        c = st.columns(2)
        with c[0]:
            kpi("✅", "#10b981", "Total received", money(D["received"]), "All recorded payments")
        with c[1]:
            kpi("⏳", "#f59e0b", "Still owed", money(D["outstanding"]), "Across all invoices")
        st.write("")
        rows = [{"Payment": p[0], "Invoice": p[1], "Amount": float(p[2])} for p in D["payments"]]
        table(pd.DataFrame(rows), "payments", ["Amount"])
    else:
        empty("No payments yet.", IMPORT_HINT)


# ==================================================================
# REPORTS
# ==================================================================
elif page == "Reports":
    page_header("Reports", "Create a sales report you can save or share.")
    c1, c2 = st.columns(2)
    with c1, st.container(border=True):
        panel_head("Sales report", "A text summary of your current sales.")
        if st.button("Create sales report", type="primary", use_container_width=True):
            try:
                reports_folder = workspace_path / "reports"
                reports_folder.mkdir(parents=True, exist_ok=True)
                path = reports_folder / "sales_report.txt"
                with st.spinner("Creating your report…"):
                    S["reports"].save_report(path)
                log.info("Report created for %s", workspace_id)
                st.session_state["report_text"] = path.read_text(encoding="utf-8")
                st.success("Your sales report is ready.")
            except Exception:
                log.exception("Report generation failed for %s", workspace_id)
                st.error("The report could not be created. Please try again. If it keeps "
                         "happening, contact support.")
        if st.session_state.get("report_text"):
            st.download_button("Download report", st.session_state["report_text"],
                               "sales_report.txt", "text/plain", use_container_width=True)
    with c2:
        kpi(SYM, "#10b981", "Sales so far", money(D["revenue"]),
            f"From {len(D['orders'])} orders")


# ==================================================================
# AI COPILOT
# ==================================================================
elif page == "AI Copilot":
    page_header("AI Copilot", "Ask questions about your business in plain language.")
    st.session_state.setdefault("chat", [])

    if not st.session_state.chat:
        st.markdown('<div class="tip">Try asking:</div>', unsafe_allow_html=True)
        ex = ["Who are my top customers?", "How much money is still unpaid?",
              "Which product sells best?"]
        cols = st.columns(len(ex))
        for col, text in zip(cols, ex):
            if col.button(text, use_container_width=True):
                st.session_state["pending_q"] = text
                st.rerun()

    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    q = st.chat_input("Ask anything about your sales, customers or payments…")
    q = q or st.session_state.pop("pending_q", None)

    if q:
        st.session_state.chat.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        with st.chat_message("assistant"):
            if not any(D[k] for k in ("customers", "products", "orders", "invoices", "payments")):
                ans = ("This business has no data yet, so there is nothing for me to answer "
                       "from. Upload your files under Automation, in Import your data, "
                       "then ask me again.")
                st.markdown(ans)
            else:
                try:
                    with st.spinner("Looking through your records…"):
                        ans = BusinessAssistant(db).ask(q)
                except Exception as exc:
                    log.exception("AI assistant failed for %s", workspace_id)
                    msg = str(exc).lower()
                    if "groq_api_key" in msg or "not configured" in msg:
                        ans = ("AI Copilot is not configured yet. Add GROQ_API_KEY to the "
                               "environment or .env file, then refresh the page.")
                    else:
                        ans = ("I couldn't answer that right now. Check that your AI "
                               "key or model is set up, then try again.")
                    st.error(ans)
                else:
                    st.markdown(ans)
        st.session_state.chat.append({"role": "assistant", "content": ans})

    if st.session_state.chat and st.button("Clear conversation"):
        st.session_state.chat = []
        st.rerun()


# ==================================================================
# AUTOMATION
# ==================================================================
elif page == "Automation":
    page_header("Automation", "Let the system handle repeat work for you.")
    import_panel()
    st.write("")
    c1, c2 = st.columns(2)

    with c1, st.container(border=True):
        panel_head("Process new files", "Reads new business files, saves the records, "
                   "creates reports and archives the originals.")
        st.caption("Use this for files that are already waiting. To add new data, use "
                   "Import your data above.")
        if st.button("Process files now", type="primary", use_container_width=True):
            try:
                with st.spinner("Processing files…"):
                    res = S["automation"].process_pending_files()
                if res:
                    load_data.clear()
                    st.success(f"Done. {len(res)} file(s) processed.")
                else:
                    st.info("There are no new files waiting.")
            except Exception:
                log.exception("File processing failed for %s", workspace_id)
                st.error("Processing failed. Your files are still waiting. Try again, "
                         "or contact support if it keeps happening.")

    with c2, st.container(border=True):
        panel_head("Back up your data", "Saves a dated copy of your database so you "
                   "can restore it later.")
        if st.button("Create backup", type="primary", use_container_width=True):
            try:
                with st.spinner("Backing up…"):
                    p = S["backup"].backup_database()
                log.info("Backup created for %s: %s", workspace_id, Path(p).name)
                st.success(f"Backup saved as {Path(p).name}")
            except Exception:
                log.exception("Backup failed for %s", workspace_id)
                st.error("The backup could not be created. Please try again, or contact "
                         "support if it keeps happening.")

    st.write("")
    with st.container(border=True):
        panel_head("Repeat automatically", "Choose how often files are processed.")
        labels = {1: "Every minute", 5: "Every 5 minutes", 15: "Every 15 minutes",
                  30: "Every 30 minutes", 60: "Every hour", 1440: "Every day"}
        interval = st.selectbox("How often?", list(labels), index=2,
                                format_func=labels.get)
        b1, b2 = st.columns(2)
        if b1.button("Turn on schedule", use_container_width=True):
            try:
                S["scheduler"].clear_schedule()
                S["scheduler"].setup_schedule(interval_minutes=interval)
                log.info("Schedule set for %s: every %s min", workspace_id, interval)
                st.success(f"Schedule saved: {labels[interval].lower()}.")
            except Exception:
                log.exception("Could not set schedule for %s", workspace_id)
                st.error("The schedule could not be saved. Please try again.")
        if b2.button("Turn off schedule", use_container_width=True):
            S["scheduler"].clear_schedule()
            st.success("Schedule turned off.")
        n = len(schedule.get_jobs())
        st.caption(f"{n} repeating task(s) active." if n else "No repeating tasks are active.")
