import io
import hashlib
import time
import xmlrpc.client
from datetime import datetime, timedelta

import altair as alt
import pandas as pd
import streamlit as st

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except Exception:
    HAS_PLOTLY = False

st.set_page_config(page_title="SWAG Sales & Purchase Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*{box-sizing:border-box}
html,body,[class*="css"]{font-family:'Inter',sans-serif}
body{background:#0a0c10}
.stApp{
  background:
    radial-gradient(circle at top right, rgba(52,152,219,.10), transparent 22%),
    radial-gradient(circle at bottom left, rgba(46,204,113,.08), transparent 22%),
    linear-gradient(135deg,#07090d 0%,#0d1117 55%,#10151d 100%);
  min-height:100vh;
}
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#0d1117 0%,#090b0f 100%) !important;
  border-right:1px solid rgba(255,255,255,.06);
}
section[data-testid="stSidebar"] *{color:#e8edf2 !important}
section[data-testid="stSidebar"] .stButton button{
  background:linear-gradient(135deg,#16202b,#111722)!important;
  border:1px solid rgba(52,152,219,.28)!important;
  border-radius:14px!important;
  color:#e8edf2!important;
}
.stTextInput input,.stDateInput input,.stNumberInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"]>div{
  background:#181d26!important;
  color:#e8edf2!important;
  border:1px solid rgba(255,255,255,.10)!important;
  border-radius:14px!important;
}
.stButton button{
  background:linear-gradient(90deg,#3498db,#2ecc71)!important;
  color:white!important;
  border:none!important;
  border-radius:14px!important;
  font-weight:700!important;
}
.stDownloadButton button{
  background:linear-gradient(135deg,#16202b,#111722)!important;
  color:#e8edf2!important;
  border:1px solid rgba(52,152,219,.25)!important;
  border-radius:14px!important;
}
.hero{
  display:grid;grid-template-columns:1.15fr .85fr;gap:24px;align-items:center;
  margin:8px 0 24px;padding:30px;border:1px solid rgba(255,255,255,.06);
  border-radius:28px;background:linear-gradient(135deg,rgba(17,23,34,.96),rgba(8,11,16,.98));
  box-shadow:0 20px 50px rgba(0,0,0,.28);
}
.hero h1{margin:0 0 12px;font-size:3rem;line-height:1.02;color:#f3f7fb;font-weight:800;letter-spacing:-1.4px}
.hero h1 span{background:linear-gradient(90deg,#3498db,#2ecc71);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero p{margin:0;color:#94a3b8;line-height:1.85;font-size:1rem;max-width:64ch}
.badge{display:inline-block;padding:8px 14px;border-radius:999px;background:rgba(52,152,219,.10);border:1px solid rgba(52,152,219,.24);color:#9fd4ff;font-size:.76rem;font-weight:700;letter-spacing:.08em;margin-bottom:16px}
.system-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
.system-chip{padding:10px 14px;border-radius:14px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);color:#c7d2de;font-size:.84rem;font-weight:700}
.preview{background:linear-gradient(135deg,#161b24,#10151c);border:1px solid rgba(255,255,255,.08);border-radius:24px;padding:20px}
.preview-top{display:flex;align-items:center;gap:8px;margin-bottom:16px}.dot{width:10px;height:10px;border-radius:50%}.r{background:#ff5f57}.y{background:#febc2e}.g{background:#28c840}
.preview-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:14px}
.preview-stat{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:16px;padding:14px}.preview-stat .v{font-size:1.15rem;font-weight:800;color:#60a5fa}.preview-stat .l{font-size:.76rem;color:#8ea0b4;margin-top:4px}
.preview-bars{height:120px;display:flex;align-items:flex-end;gap:8px;padding-top:8px}.preview-bars span{flex:1;border-radius:10px 10px 0 0;background:linear-gradient(180deg,#3498db,#2ecc71)}
.login-shell{max-width:460px;margin:20px auto 0}.login-card{background:rgba(14,18,25,.88);border:1px solid rgba(255,255,255,.08);border-radius:28px;padding:30px;box-shadow:0 22px 55px rgba(0,0,0,.30)}
.login-orb{width:82px;height:82px;border-radius:22px;background:linear-gradient(135deg,#1f4c7a,#3498db);display:flex;align-items:center;justify-content:center;font-size:2rem;margin:0 auto 16px;box-shadow:0 10px 30px rgba(52,152,219,.24)}
.login-title{text-align:center;font-size:1.9rem;font-weight:800;color:#f3f7fb;margin-bottom:6px}.login-sub{text-align:center;color:#8fa1b5;font-size:.92rem;margin-bottom:18px}
.panel{background:linear-gradient(135deg,#161b24,#111722);border:1px solid rgba(255,255,255,.06);border-radius:22px;padding:18px;margin-bottom:18px}
.panel-title{font-size:.95rem;font-weight:700;color:#dce6f2;margin-bottom:14px}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px;margin:20px 0 24px}
.kpi{background:linear-gradient(135deg,#171d27,#11161e);border:1px solid rgba(255,255,255,.07);border-radius:22px;padding:20px;position:relative;overflow:hidden}.kpi:before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#3498db,#2ecc71)}
.kpi .v{font-size:1.8rem;font-weight:800;color:#f8fbff}.kpi .l{font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;color:#8ea0b4;margin-top:8px}.kpi .t{font-size:.76rem;color:#2ecc71;margin-top:8px}
.section-title{background:linear-gradient(135deg,#171d27,#11161e);border-left:4px solid #3498db;border-radius:14px;padding:12px 18px;margin:26px 0 18px;color:#e8edf2;font-weight:700}
.table-wrap{overflow:auto;border-radius:22px;background:linear-gradient(135deg,#171d27,#11161e);border:1px solid rgba(255,255,255,.06);margin-top:14px}
.table-wrap table{width:100%;border-collapse:collapse}.table-wrap th{background:#0e141c;color:#60a5fa;padding:14px 16px;font-size:.78rem;text-transform:uppercase;letter-spacing:.05em}.table-wrap td{padding:12px 16px;color:#e8edf2;border-top:1px solid rgba(255,255,255,.05);font-size:.84rem;text-align:center}.table-wrap tr:hover td{background:rgba(52,152,219,.08)}
.info{background:rgba(52,152,219,.10);border-left:3px solid #3498db;border-radius:12px;padding:12px 16px;color:#b7cadc;font-size:.84rem}
.foot{text-align:center;padding:22px 0 10px;color:#627489;font-size:.76rem}
@media (max-width: 980px){.hero{grid-template-columns:1fr}.hero h1{font-size:2.3rem}}
</style>
""", unsafe_allow_html=True)

SYSTEM_KEYS = ["SWAG"]
COOKIE_SECRET = "swag2025secure"


def get_lang():
    return st.session_state.get("lang", "EN")


def t(en, ar):
    return ar if get_lang() == "AR" else en


def make_token(email):
    return hashlib.sha256(f"{COOKIE_SECRET}:{email}".encode()).hexdigest()[:32]


def verify_token(email, token):
    return bool(email and token and token == make_token(email))


def restore_session():
    if st.session_state.get("authenticated"):
        return
    try:
        params = st.query_params
        email = params.get("u")
        token = params.get("t")
        if email and token and verify_token(email, token):
            st.session_state.authenticated = True
            st.session_state.useremail = email
    except Exception:
        pass


def proxy(url, ep):
    return xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/{ep}", allow_none=True)


@st.cache_data(ttl=28800, show_spinner=False)
def auth(url, db, user, key):
    try:
        uid = proxy(url, "common").authenticate(db, user, key, {})
        return uid or None
    except Exception:
        return None


def x(url, db, uid, key, model, method, domain, kw):
    return proxy(url, "object").execute_kw(db, uid, key, model, method, domain, kw)


def init_state():
    defaults = {
        "authenticated": False,
        "useremail": "",
        "lang": "EN",
        "analyticsview": "purchase",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def fmt_num(x):
    try:
        return float(pd.to_numeric(pd.Series([x]), errors="coerce").fillna(0).iloc[0])
    except Exception:
        return 0.0


def render_table(df):
    if df is None or df.empty:
        st.info(t("No data available.", "لا توجد بيانات"))
        return
    cols = df.columns.tolist()
    th = "".join([f"<th>{c}</th>" for c in cols])
    rows = []
    for _, r in df.iterrows():
        cells = "".join([f"<td>{v}</td>" for v in r.tolist()])
        rows.append(f"<tr>{cells}</tr>")
    html = f"<div class='table-wrap'><table><thead><tr>{th}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)


def kpi_card(value, label, trend=""):
    trend_html = f"<div class='t'>{trend}</div>" if trend else ""
    return f"<div class='kpi'><div class='v'>{value}</div><div class='l'>{label}</div>{trend_html}</div>"


def render_kpis(cards):
    st.markdown(f"<div class='kpi-grid'>{''.join(cards)}</div>", unsafe_allow_html=True)


def chart_title(title):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)


def to_excel_sales(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="SWAG Sales")
    return buf.getvalue()


def to_excel_purchase(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="SWAG Purchase")
    return buf.getvalue()


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_swag_purchase_history(modelcode, datefrom, dateto):
    cols = [t("Date", "التاريخ"), t("PO", "أمر الشراء"), t("Vendor", "المورد"), t("Brand Category", "فئة العلامة"), t("Category", "الفئة"), t("Model Code", "كود الموديل"), t("Product", "المنتج"), t("Qty", "الكمية"), t("Unit Price", "سعر الوحدة"), t("Subtotal", "الإجمالي")]
    empty = pd.DataFrame(columns=cols)
    cfg = st.secrets.get("SWAG")
    if not cfg:
        return empty
    uid = auth(cfg["url"], cfg["db"], cfg["user"], cfg["apikey"])
    if not uid:
        return empty
    try:
        datefromdt = f"{datefrom} 00:00:00"
        datetodt = f"{dateto} 23:59:59"
        domain = [["order_id.state", "in", ["purchase", "done"]], ["order_id.date_order", ">=", datefromdt], ["order_id.date_order", "<=", datetodt]]
        if modelcode and str(modelcode).strip():
            domain.append(["product_id.default_code", "ilike", str(modelcode).strip()])
        lines = x(cfg["url"], cfg["db"], uid, cfg["apikey"], "purchase.order.line", "search_read", [domain], {"fields": ["order_id", "product_id", "product_qty", "price_unit"], "limit": 10000, "order": "order_id desc"})
        if not lines:
            return empty
        orderids = [l["order_id"][0] for l in lines if isinstance(l.get("order_id"), list)]
        productids = [l["product_id"][0] for l in lines if isinstance(l.get("product_id"), list)]
        orders = x(cfg["url"], cfg["db"], uid, cfg["apikey"], "purchase.order", "search_read", [[["id", "in", orderids]]], {"fields": ["id", "name", "partner_id", "date_order"], "limit": len(orderids) + 10})
        products = x(cfg["url"], cfg["db"], uid, cfg["apikey"], "product.product", "search_read", [[["id", "in", productids]]], {"fields": ["id", "default_code", "display_name", "categ_id", "product_tmpl_id"], "limit": len(productids) + 10})
        ordermap = {o["id"]: o for o in orders}
        prodmap = {p["id"]: p for p in products}
        tmplids = [p["product_tmpl_id"][0] for p in products if isinstance(p.get("product_tmpl_id"), list)]
        tmplmap = {}
        if tmplids:
            try:
                tmpls = x(cfg["url"], cfg["db"], uid, cfg["apikey"], "product.template", "search_read", [[["id", "in", tmplids]]], {"fields": ["id", "x_brand_category_id"], "limit": len(tmplids) + 10})
                tmplmap = {t0["id"]: t0 for t0 in tmpls}
            except Exception:
                tmplmap = {}
        rows = []
        for line in lines:
            oid = line["order_id"][0] if isinstance(line.get("order_id"), list) else None
            pid = line["product_id"][0] if isinstance(line.get("product_id"), list) else None
            order = ordermap.get(oid, {})
            prod = prodmap.get(pid, {})
            rawdate = order.get("date_order") or ""
            try:
                datestr = datetime.strptime(rawdate, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            except Exception:
                datestr = rawdate[:10] if rawdate else ""
            vendor = order.get("partner_id", [None, ""])[1] if isinstance(order.get("partner_id"), list) else ""
            categ = prod.get("categ_id", [None, ""])[1] if isinstance(prod.get("categ_id"), list) else ""
            bc = ""
            tmplref = prod.get("product_tmpl_id")
            if isinstance(tmplref, list) and tmplref:
                tmpl = tmplmap.get(tmplref[0], {})
                xbc = tmpl.get("x_brand_category_id")
                if isinstance(xbc, list):
                    bc = xbc[1] if len(xbc) > 1 else ""
                elif xbc:
                    bc = str(xbc)
            qty = float(line.get("product_qty") or 0)
            unit = float(line.get("price_unit") or 0)
            sub = round(qty * unit, 2)
            rows.append([datestr, str(order.get("name") or ""), vendor, bc, categ, str(prod.get("default_code") or ""), str(prod.get("display_name") or ""), qty, unit, sub])
        df = pd.DataFrame(rows, columns=cols)
        if df.empty:
            return empty
        return df.sort_values(by=cols[0], ascending=False).reset_index(drop=True)
    except Exception:
        return empty


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_swag_sales_history(modelcode, datefrom, dateto):
    cols = [t("Date", "التاريخ"), t("SO", "أمر البيع"), t("Customer", "العميل"), t("Brand Category", "فئة العلامة"), t("Category", "الفئة"), t("Model Code", "كود الموديل"), t("Product", "المنتج"), t("Qty", "الكمية"), t("Unit Price", "سعر الوحدة"), t("Subtotal", "الإجمالي")]
    empty = pd.DataFrame(columns=cols)
    cfg = st.secrets.get("SWAG")
    if not cfg:
        return empty
    uid = auth(cfg["url"], cfg["db"], cfg["user"], cfg["apikey"])
    if not uid:
        return empty
    try:
        datefromdt = f"{datefrom} 00:00:00"
        datetodt = f"{dateto} 23:59:59"
        domain = [["order_id.state", "in", ["sale", "done"]], ["order_id.date_order", ">=", datefromdt], ["order_id.date_order", "<=", datetodt]]
        if modelcode and str(modelcode).strip():
            domain.append(["product_id.default_code", "ilike", str(modelcode).strip()])
        lines = x(cfg["url"], cfg["db"], uid, cfg["apikey"], "sale.order.line", "search_read", [domain], {"fields": ["order_id", "product_id", "product_uom_qty", "price_unit"], "limit": 20000, "order": "order_id desc"})
        if not lines:
            return empty
        orderids = [l["order_id"][0] for l in lines if isinstance(l.get("order_id"), list)]
        productids = [l["product_id"][0] for l in lines if isinstance(l.get("product_id"), list)]
        orders = x(cfg["url"], cfg["db"], uid, cfg["apikey"], "sale.order", "search_read", [[["id", "in", orderids]]], {"fields": ["id", "name", "partner_id", "date_order"], "limit": len(orderids) + 10})
        products = x(cfg["url"], cfg["db"], uid, cfg["apikey"], "product.product", "search_read", [[["id", "in", productids]]], {"fields": ["id", "default_code", "display_name", "categ_id", "product_tmpl_id"], "limit": len(productids) + 10})
        ordermap = {o["id"]: o for o in orders}
        prodmap = {p["id"]: p for p in products}
        tmplids = [p["product_tmpl_id"][0] for p in products if isinstance(p.get("product_tmpl_id"), list)]
        tmplmap = {}
        if tmplids:
            try:
                tmpls = x(cfg["url"], cfg["db"], uid, cfg["apikey"], "product.template", "search_read", [[["id", "in", tmplids]]], {"fields": ["id", "x_brand_category_id"], "limit": len(tmplids) + 10})
                tmplmap = {t0["id"]: t0 for t0 in tmpls}
            except Exception:
                tmplmap = {}
        rows = []
        for line in lines:
            oid = line["order_id"][0] if isinstance(line.get("order_id"), list) else None
            pid = line["product_id"][0] if isinstance(line.get("product_id"), list) else None
            order = ordermap.get(oid, {})
            prod = prodmap.get(pid, {})
            rawdate = order.get("date_order") or ""
            try:
                datestr = datetime.strptime(rawdate, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            except Exception:
                datestr = rawdate[:10] if rawdate else ""
            customer = order.get("partner_id", [None, ""])[1] if isinstance(order.get("partner_id"), list) else ""
            categ = prod.get("categ_id", [None, ""])[1] if isinstance(prod.get("categ_id"), list) else ""
            bc = ""
            tmplref = prod.get("product_tmpl_id")
            if isinstance(tmplref, list) and tmplref:
                tmpl = tmplmap.get(tmplref[0], {})
                xbc = tmpl.get("x_brand_category_id")
                if isinstance(xbc, list):
                    bc = xbc[1] if len(xbc) > 1 else ""
                elif xbc:
                    bc = str(xbc)
            qty = float(line.get("product_uom_qty") or 0)
            unit = float(line.get("price_unit") or 0)
            sub = round(qty * unit, 2)
            rows.append([datestr, str(order.get("name") or ""), customer, bc, categ, str(prod.get("default_code") or ""), str(prod.get("display_name") or ""), qty, unit, sub])
        df = pd.DataFrame(rows, columns=cols)
        if df.empty:
            return empty
        return df.sort_values(by=cols[0], ascending=False).reset_index(drop=True)
    except Exception:
        return empty


def render_login():
    l1, l2 = st.columns([2.4, 1])
    with l2:
        lg = st.radio("", ["EN", "AR"], horizontal=True, index=0 if get_lang() == "EN" else 1, label_visibility="collapsed")
        if lg != get_lang():
            st.session_state.lang = lg
            st.rerun()
    st.markdown("""
    <div class='hero'>
      <div>
        <div class='badge'>SWAG INTELLIGENCE PLATFORM</div>
        <h1>Real-Time <span>Sales & Purchase</span><br>Intelligence</h1>
        <p>Unified analytics for the SWAG Odoo system. Track sales history, purchase history, customer trends, vendor trends, categories, and model-level performance in one premium dashboard.</p>
        <div class='system-row'>
          <div class='system-chip'>📈 Sales Analytics</div>
          <div class='system-chip'>🛒 Purchase Analytics</div>
          <div class='system-chip'>📦 Date-based Records</div>
          <div class='system-chip'>⬇️ Excel / CSV Export</div>
        </div>
        <div class='system-row'>
          <div class='system-chip'>SWAG (Main)</div>
          <div class='system-chip'>Odoo XML-RPC</div>
          <div class='system-chip'>EN / AR</div>
        </div>
      </div>
      <div class='preview'>
        <div class='preview-top'><span class='dot r'></span><span class='dot y'></span><span class='dot g'></span></div>
        <div class='preview-grid'>
          <div class='preview-stat'><div class='v'>Sales</div><div class='l'>History & trends</div></div>
          <div class='preview-stat'><div class='v'>Purchase</div><div class='l'>Vendor visibility</div></div>
          <div class='preview-stat'><div class='v'>Export</div><div class='l'>Excel / CSV</div></div>
          <div class='preview-stat'><div class='v'>AR / EN</div><div class='l'>Bilingual UI</div></div>
        </div>
        <div class='preview-bars'>
          <span style='height:42%'></span><span style='height:68%'></span><span style='height:56%'></span><span style='height:84%'></span>
          <span style='height:52%'></span><span style='height:92%'></span><span style='height:70%'></span><span style='height:80%'></span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='login-shell'><div class='login-card'><div class='login-orb'>📊</div><div class='login-title'>SWAG Dashboard</div><div class='login-sub'>Sign in to access sales and purchase analytics</div>", unsafe_allow_html=True)
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input(t("Email", "البريد الإلكتروني"), placeholder="you@swag.com.sa")
        password = st.text_input(t("Password", "كلمة المرور"), type="password", placeholder="••••••••")
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(t("Sign In", "تسجيل الدخول"), use_container_width=True, type="primary")
    st.markdown("</div></div>", unsafe_allow_html=True)
    if submitted:
        if not email or not password:
            st.error(t("Fill in both fields.", "يرجى تعبئة الحقلين"))
            return
        if "LOGIN" not in st.secrets:
            st.error("LOGIN section missing in secrets.toml")
            return
        cfg = st.secrets["LOGIN"]
        if "url" not in cfg or "db" not in cfg:
            st.error("LOGIN.url or LOGIN.db missing in secrets.toml")
            return
        with st.spinner(t("Signing in...", "جاري تسجيل الدخول...")):
            try:
                uid = proxy(cfg["url"], "common").authenticate(cfg["db"], email, password, {})
                if uid:
                    token = make_token(email)
                    st.query_params["u"] = email
                    st.query_params["t"] = token
                    st.session_state.authenticated = True
                    st.session_state.useremail = email
                    time.sleep(0.2)
                    st.rerun()
                else:
                    st.error(t("Wrong email or password.", "بيانات الدخول غير صحيحة"))
            except Exception as e:
                st.error(f"Connection error: {e}")
    st.markdown("<div class='foot'>2026 SWAG Fashion · Powered by Odoo · Premium Analytics Workspace</div>", unsafe_allow_html=True)


def logout():
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.session_state.authenticated = False
    st.session_state.useremail = ""
    st.rerun()


def alt_bar(df, xfield, yfield, color="#3498db", height=320):
    return alt.Chart(df).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8, opacity=0.92, color=color).encode(
        x=alt.X(f"{xfield}:N", sort='-y', axis=alt.Axis(labelAngle=-28, labelColor="#a9b8c8", title=None)),
        y=alt.Y(f"{yfield}:Q", axis=alt.Axis(grid=True, gridColor="rgba(255,255,255,0.08)", labelColor="#a9b8c8", titleColor="#dce6f2")),
        tooltip=[xfield, yfield],
    ).properties(height=height).configure_view(strokeOpacity=0).configure(background="transparent")


def donut(labels, values, title):
    if not HAS_PLOTLY:
        return
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.56, marker=dict(colors=["#3498db", "#2ecc71", "#f1c40f", "#9b59b6", "#e67e22", "#1abc9c", "#e74c3c", "#95a5a6"]), textinfo="percent+label")])
    fig.update_layout(title=title, title_x=0.5, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e8edf2"), height=360)
    st.plotly_chart(fig, use_container_width=True)


def sales_view():
    st.markdown(f"<div class='badge'>{t('SALES ANALYTICS · SWAG ONLY', 'تحليلات المبيعات · SWAG فقط')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>{t('Sales Dashboard', 'لوحة المبيعات')}</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.2, 1.2, 1])
    with c1:
        date_from = st.date_input(t("From Date", "من تاريخ"), value=datetime.now().date() - timedelta(days=30), key="sales_from")
    with c2:
        date_to = st.date_input(t("To Date", "إلى تاريخ"), value=datetime.now().date(), key="sales_to")
    with c3:
        model = st.text_input(t("Model Code (optional)", "كود الموديل اختياري"), placeholder="e.g. XP6013", key="sales_model")
    df = fetch_swag_sales_history(model, str(date_from), str(date_to))
    if df.empty:
        st.warning(t("No sales data found for the selected range.", "لا توجد بيانات مبيعات في المدة المحددة"))
        return
    qty_col = t("Qty", "الكمية")
    sub_col = t("Subtotal", "الإجمالي")
    cust_col = t("Customer", "العميل")
    cat_col = t("Category", "الفئة")
    brand_col = t("Brand Category", "فئة العلامة")
    kpis = [
        kpi_card(f"{len(df):,}", t("Rows", "الصفوف")),
        kpi_card(f"{df[qty_col].sum():,.0f}", t("Total Qty", "إجمالي الكمية")),
        kpi_card(f"{df[sub_col].sum():,.2f}", t("Total Sales", "إجمالي المبيعات")),
        kpi_card(f"{df[cust_col].nunique():,}", t("Customers", "العملاء")),
    ]
    render_kpis(kpis)
    chart_title(t("Top Customers by Sales", "أعلى العملاء بالمبيعات"))
    top_customers = df.groupby(cust_col, as_index=False)[sub_col].sum().sort_values(sub_col, ascending=False).head(10)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.altair_chart(alt_bar(top_customers, cust_col, sub_col, color="#3498db"), use_container_width=True)
    with c2:
        if HAS_PLOTLY:
            donut(top_customers[cust_col], top_customers[sub_col], t("Customer Share", "حصة العملاء"))
    chart_title(t("Top Categories by Sales", "أعلى الفئات بالمبيعات"))
    top_cat = df.groupby(cat_col, as_index=False)[sub_col].sum().sort_values(sub_col, ascending=False).head(10)
    st.altair_chart(alt_bar(top_cat, cat_col, sub_col, color="#2ecc71"), use_container_width=True)
    chart_title(t("Sales Detail Table", "جدول تفاصيل المبيعات"))
    render_table(df)
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(t("Download CSV", "تحميل CSV"), df.to_csv(index=False).encode("utf-8-sig"), file_name=f"swag_sales_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv", use_container_width=True)
    with d2:
        st.download_button(t("Download Excel", "تحميل Excel"), to_excel_sales(df), file_name=f"swag_sales_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)


def purchase_view():
    st.markdown(f"<div class='badge'>{t('PURCHASE ANALYTICS · SWAG ONLY', 'تحليلات الشراء · SWAG فقط')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>{t('Purchase Dashboard', 'لوحة المشتريات')}</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.2, 1.2, 1])
    with c1:
        date_from = st.date_input(t("From Date", "من تاريخ"), value=datetime.now().date() - timedelta(days=30), key="purchase_from")
    with c2:
        date_to = st.date_input(t("To Date", "إلى تاريخ"), value=datetime.now().date(), key="purchase_to")
    with c3:
        model = st.text_input(t("Model Code (optional)", "كود الموديل اختياري"), placeholder="e.g. XP6013", key="purchase_model")
    df = fetch_swag_purchase_history(model, str(date_from), str(date_to))
    if df.empty:
        st.warning(t("No purchase data found for the selected range.", "لا توجد بيانات شراء في المدة المحددة"))
        return
    qty_col = t("Qty", "الكمية")
    sub_col = t("Subtotal", "الإجمالي")
    ven_col = t("Vendor", "المورد")
    cat_col = t("Category", "الفئة")
    brand_col = t("Brand Category", "فئة العلامة")
    kpis = [
        kpi_card(f"{len(df):,}", t("Rows", "الصفوف")),
        kpi_card(f"{df[qty_col].sum():,.0f}", t("Total Qty", "إجمالي الكمية")),
        kpi_card(f"{df[sub_col].sum():,.2f}", t("Total Purchase", "إجمالي الشراء")),
        kpi_card(f"{df[ven_col].nunique():,}", t("Vendors", "الموردون")),
    ]
    render_kpis(kpis)
    chart_title(t("Top Vendors by Purchase", "أعلى الموردين بالمشتريات"))
    top_v = df.groupby(ven_col, as_index=False)[sub_col].sum().sort_values(sub_col, ascending=False).head(10)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.altair_chart(alt_bar(top_v, ven_col, sub_col, color="#3498db"), use_container_width=True)
    with c2:
        if HAS_PLOTLY:
            donut(top_v[ven_col], top_v[sub_col], t("Vendor Share", "حصة الموردين"))
    chart_title(t("Top Categories by Purchase", "أعلى الفئات بالمشتريات"))
    top_cat = df.groupby(cat_col, as_index=False)[sub_col].sum().sort_values(sub_col, ascending=False).head(10)
    st.altair_chart(alt_bar(top_cat, cat_col, sub_col, color="#2ecc71"), use_container_width=True)
    chart_title(t("Purchase Detail Table", "جدول تفاصيل الشراء"))
    render_table(df)
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(t("Download CSV", "تحميل CSV"), df.to_csv(index=False).encode("utf-8-sig"), file_name=f"swag_purchase_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv", use_container_width=True)
    with d2:
        st.download_button(t("Download Excel", "تحميل Excel"), to_excel_purchase(df), file_name=f"swag_purchase_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)


def dashboard():
    with st.sidebar:
        st.markdown(f"### {t('Settings', 'الإعدادات')}")
        lg = st.radio(t("Language", "اللغة"), ["EN", "AR"], horizontal=True, index=0 if get_lang() == "EN" else 1)
        if lg != get_lang():
            st.session_state.lang = lg
            st.rerun()
        st.divider()
        st.markdown(f"### {t('Analytics', 'التحليلات')}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button(t("Sales", "المبيعات"), use_container_width=True, type="primary" if st.session_state.analyticsview == "sales" else "secondary"):
                st.session_state.analyticsview = "sales"
                st.rerun()
        with c2:
            if st.button(t("Purchase", "المشتريات"), use_container_width=True, type="primary" if st.session_state.analyticsview == "purchase" else "secondary"):
                st.session_state.analyticsview = "purchase"
                st.rerun()
        st.divider()
        st.markdown(st.session_state.useremail)
        if st.button(t("Logout", "تسجيل الخروج"), use_container_width=True):
            logout()

    st.markdown(f"""
    <div class='hero'>
      <div>
        <div class='badge'>{t('LIVE DASHBOARD · SWAG ONLY', 'لوحة مباشرة · SWAG فقط')}</div>
        <h1>{t('Sales & Purchase', 'المبيعات والمشتريات')} <span>{t('Analytics', 'التحليلات')}</span></h1>
        <p>{t('Track SWAG sales and purchase history with date filters, top customers, top vendors, categories, detailed tables, and export-ready reports in one premium workspace.', 'تابع تاريخ المبيعات والمشتريات لنظام SWAG مع فلاتر التاريخ وأعلى العملاء وأعلى الموردين والفئات والجداول التفصيلية والتقارير الجاهزة للتصدير في مساحة عمل احترافية.')}</p>
        <div class='system-row'>
          <div class='system-chip'>SWAG Odoo</div>
          <div class='system-chip'>{t('Sales', 'المبيعات')}</div>
          <div class='system-chip'>{t('Purchase', 'المشتريات')}</div>
          <div class='system-chip'>{t('Exports', 'التصدير')}</div>
        </div>
      </div>
      <div class='preview'>
        <div class='preview-top'><span class='dot r'></span><span class='dot y'></span><span class='dot g'></span></div>
        <div class='preview-grid'>
          <div class='preview-stat'><div class='v'>1</div><div class='l'>SWAG System</div></div>
          <div class='preview-stat'><div class='v'>2</div><div class='l'>Analytics Views</div></div>
          <div class='preview-stat'><div class='v'>CSV</div><div class='l'>Downloads</div></div>
          <div class='preview-stat'><div class='v'>XLSX</div><div class='l'>Reports</div></div>
        </div>
        <div class='preview-bars'>
          <span style='height:45%'></span><span style='height:65%'></span><span style='height:58%'></span><span style='height:88%'></span>
          <span style='height:54%'></span><span style='height:90%'></span><span style='height:74%'></span><span style='height:82%'></span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.analyticsview == "sales":
        sales_view()
    else:
        purchase_view()

    st.markdown("<div class='foot'>2026 SWAG Fashion · Sales & Purchase Dashboard · Powered by Odoo</div>", unsafe_allow_html=True)


init_state()
restore_session()
if st.session_state.authenticated:
    dashboard()
else:
    render_login()
