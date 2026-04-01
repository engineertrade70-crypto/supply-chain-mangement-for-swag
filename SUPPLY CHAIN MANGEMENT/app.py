Skip to content
sabeya143111-arch
odoo_dashboard
Repository navigation
Code
Issues
Pull requests
Actions
Projects
Wiki
Security and quality
Insights
Settings
Important update
On April 24 we'll start using GitHub Copilot interaction data for AI model training unless you opt out. Review this update and manage your preferences in your GitHub account settings.
Files
Go to file
t
.devcontainer
odoo_dashboard
odoo_dashboard/.streamlit
app.py
requirements.txt
swag_purchase_app.py
odoo_dashboard/odoo_dashboard
/
app.py
in
main

Edit

Preview
Indent mode

Spaces
Indent size

2
Line wrap mode

No wrap
Editing app.py file contents
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
"""
SWAG Product Comparison Dashboard
Version 22.0 — PDF Sequence Preserved + Search + Filters + Sort + Session Login

CHANGES FROM v21:
  1. parse_invoice_pdf_cached() now returns list of dicts:
       [{"sequence": 1, "code": "XP6013"}, ...]
     instead of plain strings — taake PDF order yaad rahe.

  2. get_unique_base_models() updated to read item["code"] and
     carry item["sequence"] forward — base model banate waqt bhi order na toote.

  3. PDF upload block now uses unique_sorted (sorted by sequence)
     and extracts plain unique_codes list for fetch/search.
     Display mein sequence number bhi dikhta hai.

  4. display_df() sort default stays "—" — user jab tak sort na kare,
     PDF wali sequence bani rahe.

  5. No other logic changed.

CHANGES FROM v22 (SWAG Purchase tab):
  6. Added fetch_swag_purchase_history() function to fetch PO history from SWAG.
  7. Added to_excel_purchase() helper for purchase Excel export.
  8. Added "SWAG Purchase" tab to the results section.
"""

import io
import re
import hashlib
import time
import xmlrpc.client
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="SWAG Product Comparison",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
*,html,body,[class*="css"]{font-family:'IBM Plex Sans Arabic',sans-serif;box-sizing:border-box;}
.stApp{background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#1a1a2e 0%,#16213e 100%)!important;border-right:1px solid #ffffff15;}
section[data-testid="stSidebar"] *,section[data-testid="stSidebar"] label,section[data-testid="stSidebar"] span,section[data-testid="stSidebar"] p,section[data-testid="stSidebar"] div{color:#e8e8ff!important;}
section[data-testid="stSidebar"] input{color:#1a1a2e!important;}
@keyframes fadeInUp{from{opacity:0;transform:translateY(40px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeInDown{from{opacity:0;transform:translateY(-30px)}to{opacity:1;transform:translateY(0)}}
@keyframes bounceIn{0%{transform:scale(0.2) rotate(-10deg);opacity:0}60%{transform:scale(1.2) rotate(5deg);opacity:1}80%{transform:scale(0.9)}100%{transform:scale(1);opacity:1}}
@keyframes shimmer{0%{background-position:-400% center}100%{background-position:400% center}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 #7c3aed44}50%{box-shadow:0 0 20px 8px #7c3aed22}}
@keyframes glow{0%,100%{text-shadow:0 0 10px #667eea88}50%{text-shadow:0 0 30px #f093fbcc,0 0 60px #667eea88}}
Use Control + Shift + m to toggle the tab key moving focus. Alternatively, use esc then tab to move to the next interactive element on the page.
 
Copied!