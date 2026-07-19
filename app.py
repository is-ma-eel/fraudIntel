"""
Ghana Fraud Intelligence Repository
----------------------------------
A beginner-friendly Streamlit prototype dashboard.

This is a PROTOTYPE only:
- No machine learning / NLP
- No authentication
- No live APIs, databases, or web scraping
- All data is hardcoded sample data for demonstration purposes

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# DESIGN TOKENS
# A small, named color/type system so every chart, card, and
# badge in the app pulls from the same palette instead of
# scattering hex codes throughout the code.
#
# The palette is inspired by Ghana's flag (gold, red, green)
# kept muted and desaturated for a "monitoring room" feel,
# plus two neutral accents (blue, purple) for variety in
# charts with more than three categories.
# ============================================================

COLORS = {
    "bg": "#0B1220",            # app background (deep navy-black)
    "surface": "#111B2E",       # card background
    "surface_alt": "#0E1728",   # slightly darker surface (hero banner)
    "border": "#223148",        # card/section borders
    "text": "#EAF0F7",          # primary text
    "muted": "#8FA0BB",         # secondary / caption text
    "gold": "#E7B23C",          # Ghana gold
    "red": "#E1585B",           # Ghana red (softened)
    "green": "#2FAE7C",         # Ghana green (muted)
    "blue": "#4C8DFF",          # neutral accent
    "purple": "#9B7EDE",        # neutral accent
}

# Ordered color sequence used across all charts so categories
# line up visually wherever they appear.
CHART_COLORWAY = [
    COLORS["gold"], COLORS["red"], COLORS["green"],
    COLORS["blue"], COLORS["purple"], "#F2A65A",
]

FONT_DISPLAY = "Sora"          # headings, KPI labels, nav
FONT_BODY = "Inter"            # paragraphs, captions
FONT_MONO = "JetBrains Mono"   # numbers, data, badges


# ============================================================
# PAGE CONFIGURATION
# ============================================================
def configure_page():
    st.set_page_config(
        page_title="Ghana Fraud Intelligence Repository",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )


# ============================================================
# GLOBAL STYLING
# Injects Google Fonts + CSS so the app has a consistent dark,
# "monitoring room" look. Kept in one place so it's easy to
# tweak later without hunting through the rest of the file.
# ============================================================
def inject_custom_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: '{FONT_BODY}', sans-serif;
        }}

        /* App background */
        .stApp {{
            background-color: {COLORS['bg']};
            color: {COLORS['text']};
        }}

        /* Default Streamlit toolbar/header (hamburger menu, Deploy button) —
           transparent so it blends into the dark background instead of
           showing as a white bar at the top of the page. */
        header[data-testid="stHeader"] {{
            background-color: transparent;
        }}

        /* Trim the default top padding so the hero banner sits close to
           the top of the page instead of leaving empty space above it. */
        div[data-testid="stAppViewBlockContainer"] {{
            padding-top: 1.5rem;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: {COLORS['surface_alt']};
            border-right: 1px solid {COLORS['border']};
        }}
        section[data-testid="stSidebar"] * {{
            color: {COLORS['text']};
        }}
        section[data-testid="stSidebar"] label {{
            font-family: '{FONT_DISPLAY}', sans-serif;
            font-size: 0.92rem;
        }}

        /* Headings */
        h1, h2, h3 {{
            font-family: '{FONT_DISPLAY}', sans-serif !important;
            letter-spacing: -0.01em;
        }}

        /* Restyle Streamlit's info/warning boxes to match the dark theme */
        div[data-testid="stAlert"] {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 10px;
            color: {COLORS['text']};
        }}

        /* Bordered containers used as "cards" */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']} !important;
            border-radius: 14px !important;
            transition: border-color 0.2s ease, transform 0.2s ease;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
            border-color: {COLORS['gold']} !important;
        }}

        /* KPI card hover lift */
        .kpi-card {{
            transition: transform 0.15s ease, border-color 0.15s ease;
        }}
        .kpi-card:hover {{
            transform: translateY(-3px);
            border-color: var(--accent);
        }}

        /* Hero banner */
        .hero {{
            background: linear-gradient(135deg, {COLORS['surface_alt']} 0%, #142236 55%, #16241c 130%);
            border: 1px solid {COLORS['border']};
            border-radius: 16px;
            padding: 28px 32px;
            margin-bottom: 22px;
        }}
        .hero-eyebrow {{
            font-family: '{FONT_DISPLAY}', sans-serif;
            font-size: 0.78rem;
            letter-spacing: 0.14em;
            color: {COLORS['gold']};
            text-transform: uppercase;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .hero-title {{
            font-family: '{FONT_DISPLAY}', sans-serif;
            font-size: 2.1rem;
            font-weight: 700;
            color: {COLORS['text']};
            margin: 0 0 6px 0;
        }}
        .hero-sub {{
            color: {COLORS['muted']};
            font-size: 0.95rem;
        }}

        /* Live pulse dot (signature element) */
        .pulse-dot {{
            width: 8px; height: 8px;
            border-radius: 50%;
            background-color: {COLORS['green']};
            display: inline-block;
            box-shadow: 0 0 0 0 rgba(47, 174, 124, 0.7);
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%   {{ box-shadow: 0 0 0 0 rgba(47, 174, 124, 0.6); }}
            70%  {{ box-shadow: 0 0 0 8px rgba(47, 174, 124, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(47, 174, 124, 0); }}
        }}

        /* KPI cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 14px;
            margin-bottom: 24px;
        }}
        .kpi-card {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-left: 4px solid var(--accent);
            border-radius: 12px;
            padding: 16px 18px;
        }}
        .kpi-icon {{ font-size: 1.3rem; margin-bottom: 6px; }}
        .kpi-label {{
            font-family: '{FONT_DISPLAY}', sans-serif;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {COLORS['muted']};
        }}
        .kpi-value {{
            font-family: '{FONT_MONO}', monospace;
            font-size: 1.55rem;
            font-weight: 600;
            color: {COLORS['text']};
            margin: 4px 0 2px 0;
        }}
        .kpi-context {{
            font-size: 0.75rem;
            color: {COLORS['muted']};
        }}
        .kpi-delta {{
            font-family: '{FONT_MONO}', monospace;
            font-size: 0.78rem;
            font-weight: 600;
            margin-left: 6px;
        }}

        /* Section header (eyebrow + title) */
        .section-eyebrow {{
            font-family: '{FONT_DISPLAY}', sans-serif;
            font-size: 0.72rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: {COLORS['blue']};
            margin-bottom: 2px;
        }}
        .section-title {{
            font-family: '{FONT_DISPLAY}', sans-serif;
            font-size: 1.15rem;
            font-weight: 600;
            color: {COLORS['text']};
            margin-bottom: 10px;
        }}

        /* Badges used in the case detail popup */
        .badge {{
            display: inline-block;
            font-family: '{FONT_MONO}', monospace;
            font-size: 0.78rem;
            padding: 3px 10px;
            border-radius: 999px;
            border: 1px solid var(--badge-color);
            color: var(--badge-color);
            background-color: color-mix(in srgb, var(--badge-color) 15%, transparent);
        }}

        /* Alert cards on the Alerts page */
        .alert-card {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-left: 4px solid {COLORS['red']};
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 10px;
            color: {COLORS['text']};
        }}

        /* Tabs */
        button[data-baseweb="tab"] {{
            font-family: '{FONT_DISPLAY}', sans-serif;
            color: {COLORS['muted']};
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {COLORS['gold']};
        }}
        div[data-baseweb="tab-highlight"] {{
            background-color: {COLORS['gold']};
        }}
        div[data-baseweb="tab-border"] {{
            background-color: {COLORS['border']};
        }}

        /* Footer note */
        .footer-note {{
            color: {COLORS['muted']};
            font-size: 0.8rem;
            text-align: center;
            margin-top: 18px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_chart_theme(fig, height=380):
    """Applies the shared color/font theme to a Plotly figure so every
    chart in the app looks like part of the same product."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_BODY, color=COLORS["text"], size=13),
        title_font=dict(family=FONT_DISPLAY, color=COLORS["text"], size=15),
        legend=dict(font=dict(color=COLORS["muted"])),
        margin=dict(l=10, r=10, t=40, b=10),
        height=height,
        colorway=CHART_COLORWAY,
    )
    fig.update_xaxes(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"])
    fig.update_yaxes(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"])
    return fig


def badge(text, color_hex):
    """Returns a small colored pill (HTML) used inside the case detail popup."""
    return (
        f'<span class="badge" style="--badge-color:{color_hex};">{text}</span>'
    )


def section_header(title):
    """Renders a small uppercase eyebrow label above a section title,
    used to give each chart/table its own clearly labeled 'card'."""
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SAMPLE DATA
# All data below is fake/demo data hardcoded directly in the
# script. Replace these with real data sources later.
# ============================================================

def get_kpi_data():
    """Returns a dictionary of top-level summary KPI numbers."""
    return {
        "total_frauds": 1284,
        "total_amount_lost": 5_430_000,   # in GHS
        "average_amount_lost": 4_228,     # in GHS
        "arrests_made": 97,
        "sources_monitored": 7,
    }


def get_kpi_deltas():
    """Returns sample month-over-month percentage changes for each KPI.
    Positive is not always 'good' (e.g. more frauds reported is bad news,
    more arrests is good news) — direction/color is decided in the UI."""
    return {
        "total_frauds": 6.4,
        "total_amount_lost": 9.1,
        "average_amount_lost": -2.3,
        "arrests_made": 14.0,
        "sources_monitored": 0.0,
    }


def get_response_rate_data():
    """Returns sample response/resolution rate percentages for gauge charts."""
    return {
        "resolution_rate": 42,       # % of cases resolved or closed
        "response_within_48h": 68,   # % of cases acknowledged within 48 hours
    }


def get_monthly_trend_data():
    """Returns sample monthly fraud case counts (Jan - Jul)."""
    data = {
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
        "Fraud Cases": [120, 145, 160, 190, 210, 230, 229],
    }
    return pd.DataFrame(data)


def get_fraud_category_data():
    """Returns sample fraud category distribution (percentages)."""
    data = {
        "Category": [
            "Mobile Money Fraud",
            "Investment Scam",
            "Romance Scam",
            "Identity Theft",
            "Business Email Compromise",
            "Payroll & Procurement Fraud",
        ],
        "Percentage": [35, 20, 15, 12, 10, 8],
    }
    return pd.DataFrame(data)


def get_fraud_methods_data():
    """Returns sample data for the top fraud methods used by scammers."""
    data = {
        "Method": [
            "Fake MoMo Reversal",
            "Phishing Links",
            "Fake Investment Platform",
            "SIM Swap Fraud",
            "Email Compromise",
        ],
        "Cases": [320, 275, 210, 150, 95],
    }
    return pd.DataFrame(data)


# def get_recent_cases_data():
#     """Returns a sample table of recent fraud cases using the full case schema."""
#     data = {
#         "Date": [
#             "2025-12-11", "Not disclosed", "2025-08-01", "May-July, 2025",
#             "2025", "2025-05-27", "2025-05-27",
#         ],
#         "Location": ["Ghana", "Ghana", "Ghana", "Ghana", "Volta", "Central", "Central"],
#         "Fraud_Category": [
#             "Romance Scam", 
#             "Cyber-enabled Financial Fraud / Payment Card Fraud", "Cyber Fraud/Online Financial Scam",
#             "Online Scam/Cyber-enabled Fraud", "Business Email Compromise", "Payroll & Procurement Fraud", "Payroll & Procurement Fraud",
#         ],
#         "Fraud_Method": [
#             "AI-generated fake identities, online relationship deception", "Fraudulent Point of Sale (POS) transactions using compromised United States banking cards", 
#             "Not disclosed",
#             "Online scams; impersonation scams; cyber-enabled fraud schemes; victims coerced into carrying out cybercrime", 
#             "Email Compromise", "Fake Invoice", "Fake Invoice",
#         ],
#         "Amount_Lost_USD": [8000000, 000, 000, 000, 1540, 510, 510],
#         # "Amount_Lost_GHS": [4500, 12000, 25000, 3200, 18500, 6100],
#         "Number_of_Victims": ["Multiple elderly victims", "Not disclosed", "Not disclosed", 23, 2, 4, 3],
#         "Victim_Type": ["Elderly", 
#                         "Financial institutions / banking card holders (United States banking card users)", 
#                         "Not disclosed", "Foreign nationals", 
#                         "Business", "Civil Servant", "Civil Servant"],
#         "Charges": ["Wire Fraud & Money Laundering", 
#                     "Cyber-enabled financial crimes; fraudulent POS transactions; possession of ammunition (15 rounds of live 9mm ammunition and one empty shell casing)", 
#                     "Suspect to be processed for court", 
#                     "Suspected online fraud, cyber-enabled crimes, impersonation-related offences, and related criminal activities (specific charges not disclosed)", 
#                     "Under Investigation", 
#                     "Fraud", "Fraud"],
#         "Victim_Country": ["United States", "United States", "Undisclosed", "Multiple foreign nationals", "Ghana", "Ghana", "Ghana"],
#         "Platform_Used": ["Social Media, Online Dating Platforms", 
#                           "POS terminals at multiple fuel stations in Ghana", 
#                           "Not disclosed", 
#                           "Not disclosed", 
#                           "Email", "Email", "Email"],
#         "Suspect_Name": ["Frederick Kumi (a.k.a Abu Trica)", 
#                          "Aderinsola Oluwanifemi Adeleye", 
#                          "Multiple suspects (not named)", 
#                          "Multiple suspects (not named)", "Unknown", "Unknown", "Unknown"],
#         "Investigating_Agencies": [
#             "CSA, NACOC, NIB, CID", 
#             "Cyber Security Authority (CSA); Ghana Police Service; INTERPOL; United States Federal Bureau of Investigation (FBI)", 
#             "CSA, CID, GPS",
#             "CSA, CID, GPS", 
#             "Cyber Security Authority", "EOCO", "EOCO",
#         ],
#         "Criminal_Network": ["Yes", "International cyber fraud syndicate", "Unknown", "Unknown", "Suspected Network", "Unknown", "Unknown"],
#         "Cross_Border_Fraud": ["Yes", "Yes", "Yes", "No", "Yes", "No", "No"],
#         "Fraud_Technique": [
#             "Romance Scam using AI-generated fake identities", 
#             "Compromised banking cards; unauthorized POS transactions; cyber-enabled financial crime", 
#             "Not disclosed",
#             "Online impersonation", 
#             "Business Impersonation", 
#             "Fake Invoicing", "Fake Invoicing",
#         ],
#         "Money_Laundering_Involved": ["Yes", "Yes", "undisclosed", "undisclosed", "Yes", "No", "No"],
#         "Court_Status": ["Indicted by U.S Federal Grand Jury", 
#                          "Arrested, arraigned before court, formally charged; case pending before the judiciary", "Pending processing", "Being processed for repatriation", "N/A", "Ongoing", "Ongoing"],
#         "Source_Name": [
#             "Cyber Security Authority (CSA)", 
#             "Cyber Security Authority (CSA)", 
#             "Cyber Security Authority (CSA)",
#             "Cyber Security Authority (CSA)", 
#             "BBC Africa", 
#             "News Website", "News Website",
#         ],
#         "Source_Type": ["Official Security Agency", 
#                         "Official Government Agency", 
#                         "Official Government", 
#                         "Official Government", "Government", 
#                         "Media", "Media"],
#         "Source_URL": [
#             "https://www.csa.gov.gh/cybersecurityauthority-has-cracked-down-on-abu-trica-and-others.php",
#             "https://www.csa.gov.gh/csa-intelligence-leads-to-arrest-of-high-Interest-nigerian-suspect-in-international-cyber-fraud-investigation.php", 
#             "https://www.csa.gov.gh/cyber-security-authority-cid-arrest-39-suspects-in-joint-cybercrime-raid-at-adom-city-estate.php",
#             "https://www.csa.gov.gh/csa-uncovers-rising-involvement-of-foreign-nationals-in-local-online-scams.php", 
#             "https://example.com/case5", 
#             "https://example.com/case6", "https://example.com/case6",
#         ],
#         "Summary": [
#             "Ghanaian suspect and two accomplices arrested for involvement in an international romance scam network that allegedly defrauded elderly U.S. victims of approximately USD 8 million using AI-generated identities and online relationship manipulation.",
#             "The Cyber Security Authority, together with the Ghana Police Service and international law enforcement partners, arrested Nigerian national Aderinsola Oluwanifemi Adeleye over alleged involvement in an international cyber-enabled financial fraud scheme involving compromised US banking cards. Investigations revealed fraudulent POS transactions conducted at fuel stations in Ghana. Authorities also identified assets allegedly acquired from proceeds of the fraud, including a building, cement block factory, and vehicle. Further investigations are ongoing to uncover other members of the criminal network and trace additional illicit assets.",
#             "The Cyber Security Authority and the Criminal Investigations Department conducted an intelligence-led raid at Adom City Estate, Tema Community 25, resulting in the arrest of 39 individuals suspected of operating a cyber fraud hub. Three suspected minors were among those arrested. Authorities seized laptops, digital devices, and other materials for forensic examination. The suspects remain in police custody pending further processing and possible prosecution as part of Ghana's efforts to combat online fraud and cyber-enabled crimes.",
#             "The Cyber Security Authority revealed increasing involvement of foreign nationals in online scams and cyber-enabled human trafficking operations in Ghana. Four joint operations with the CID between May and July 2025 resulted in the arrest of 65 suspects, including 49 foreign nationals. Several suspects were identified as victims of trafficking who had been forced into cybercrime activities. Operations in Dodowa, Bortianor-Ngleshie Amanfro, Teshie-Nungua, Sogakope and Sege led to the seizure of laptops, mobile phones and Starlink equipment. Investigations continue into organized cybercrime networks, impersonation scams and other online fraud activities.",
#             "Ghanaian social media influencer Frederick Kumi, popularly known as Abu Trica, was extradited to the United States to face charges over an alleged romance scam that defrauded elderly Americans of more than $8 million. US prosecutors allege that he used AI-generated fake identities on social media and dating platforms to gain victims' trust before requesting money for fake emergencies, travel expenses, or investment opportunities. The funds were allegedly transferred through co-conspirators in Ghana and the US. Kumi was arrested through a joint Ghana-US operation and faces charges of conspiracy to commit wire fraud and money laundering.",
#             "Ghanaian national Joseph Kwadwo Badu Boateng, also known as Dada Joe Remix, pleaded guilty in the United States to conspiracy to commit wire fraud linked to a romance and inheritance scam targeting elderly victims across Arizona and the wider United States. From 2013 to March 2023, Boateng and his co-conspirators allegedly created fake romantic relationships through online platforms and electronic communication, later deceiving victims with false claims of inherited gold and jewels that required payment of taxes and fees before release. Boateng was arrested in Ghana in May 2025, extradited to the US in June 2025, and agreed to pay approximately $4.4 million in restitution.", 
#             "htehre",
#         ],
#     }
#     return pd.DataFrame(data)


def get_victim_demographics_data():
    """Returns sample victim demographic distribution."""
    data = {
        "Group": ["Traders", "Students", "Civil Servants", "Businesses", "Unemployed", "Others"],
        "Value": [28, 22, 18, 15, 12, 5],
    }
    return pd.DataFrame(data)


def get_data_sources():
    """Returns a list of (name, type) example data sources monitored."""
    return [
        ("Ghana Police Service", "Government"),
        ("Cyber Security Authority", "Government"),
        ("Bank of Ghana", "Government"),
        ("News Websites", "Media"),
        ("EOCO (Economic and Organised Crime Office)", "Government"),
        ("INTERPOL", "International"),
        ("FBI IC3 (Internet Crime Complaint Center)", "International"),
    ]








# Path to your Excel file — adjust this to wherever your file actually lives.
# A relative path like this assumes the Excel file sits in the same folder as app.py.
DATA_FILE_PATH = "fraud_cases.xlsx"
# DATA_FILE_PATH = "\\fraud_cases.xlsx"


@st.cache_data
def get_recent_cases_data():
    """Loads fraud case records from an Excel file instead of hardcoded
    sample data. Cached so the file is only read once per session unless
    it changes (Streamlit's cache_data auto-detects file changes too if
    you pass the path in, since it's part of the function's inputs)."""
    try:
        df = pd.read_excel(DATA_FILE_PATH, sheet_name=0)
    except FileNotFoundError:
        st.error(
            f"Could not find '{DATA_FILE_PATH}'. Make sure the Excel file "
            "is in the same folder as app.py, or update DATA_FILE_PATH."
        )
        return pd.DataFrame()

    # Excel dates sometimes come in as Timestamp objects — convert to a
    # plain string so the rest of the app (which expects strings) still works.
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

    return df







# ============================================================
# UI COMPONENTS
# Each function below renders one section of the dashboard.
# ============================================================

def render_sidebar():
    """Renders the sidebar navigation menu and returns the selected page."""
    st.sidebar.markdown(
        """
        <div style="padding: 4px 0 14px 0;">
            <div style="font-family:'Sora',sans-serif; font-size:1.05rem; font-weight:700;">
                🛡️ GFIR
            </div>
            <div style="font-size:0.78rem; color:#8FA0BB;">
                Ghana Fraud Intelligence Repository
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    menu_items = {
        "Dashboard": "🧭 Dashboard",
        "Fraud Cases": "🗂️ Fraud Cases",
        "Fraud Methods": "🧩 Fraud Methods",
        "Analytics": "📊 Analytics",
        "Victim Profiles": "👥 Victim Profiles",
        # "Reports": "📑 Reports",
        # "Alerts": "🚨 Alerts",
        "Sources": "🌐 Sources",
    }
    labels = list(menu_items.values())
    selected_label = st.sidebar.radio("Navigate", labels, label_visibility="collapsed")
    # Map the chosen label back to its plain page key
    selection = [key for key, val in menu_items.items() if val == selected_label][0]

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "This is an unfinished prototype — figures shown are sample data, "
        "not live case records. "
        "Developed by Ahuofe Mango"
    )
    return selection


def render_hero(subtitle):
    """Renders the top hero banner with title, eyebrow, and a live-monitoring
    pulse indicator (the dashboard's signature visual element)."""
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-eyebrow">
                <span class="pulse-dot"></span> LIVE MONITORING from 7 CREDIBLE SOURCES
            </div>
            <div class="hero-title">🛡️ Ghana Fraud Intelligence Repository</div>
            <div class="hero-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_cards():
    """Renders the top KPI summary cards as a styled HTML grid, each with
    a colored month-over-month trend arrow for a quick sense of direction."""
    k = get_kpi_data()
    deltas = get_kpi_deltas()

    # Whether a rising number is good news or bad news, per KPI —
    # decides whether the arrow renders green or red.
    rising_is_good = {
        "total_frauds": False,
        "total_amount_lost": False,
        "average_amount_lost": False,
        "arrests_made": True,
        "sources_monitored": True,
    }

    def delta_html(key):
        pct = deltas[key]
        if pct == 0:
            return f'<span class="kpi-delta" style="color:{COLORS["muted"]};">– steady</span>'
        arrow = "▲" if pct > 0 else "▼"
        is_good = (pct > 0) == rising_is_good[key]
        color = COLORS["green"] if is_good else COLORS["red"]
        return f'<span class="kpi-delta" style="color:{color};">{arrow} {abs(pct):.1f}%</span>'

    cards = [
        ("total_frauds", "📈", "Total Frauds", f"{k['total_frauds']:,}", "vs last month", COLORS["blue"]),
        ("total_amount_lost", "💸", "Total Amount Lost", f"USD {k['total_amount_lost']:,}", "vs last month", COLORS["red"]),
        ("average_amount_lost", "📉", "Average Amount Lost", f"USD {k['average_amount_lost']:,}", "vs last month", COLORS["gold"]),
        ("arrests_made", "🚓", "Arrests Made", f"{k['arrests_made']}", "vs last month", COLORS["green"]),
        ("sources_monitored", "🌐", "Sources Monitored", f"{k['sources_monitored']}", "vs last month", COLORS["purple"]),
    ]
    cards_html = "".join(
        f'<div class="kpi-card" style="--accent:{color};">'
        f'<div class="kpi-icon">{icon}</div>'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-context">{context} {delta_html(key)}</div>'
        f'</div>'
        for key, icon, label, value, context, color in cards
    )
    st.markdown(f'<div class="kpi-grid">{cards_html}</div>', unsafe_allow_html=True)


def _gauge_figure(value, title):
    """Builds a single themed gauge chart (Plotly Indicator) used to show
    a rate/percentage at a glance — a different chart shape from the
    lines/bars/pies used elsewhere, for visual variety."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": "%", "font": {"family": FONT_MONO, "color": COLORS["text"], "size": 30}},
        title={"text": title, "font": {"family": FONT_DISPLAY, "color": COLORS["muted"], "size": 13}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": COLORS["muted"], "tickfont": {"color": COLORS["muted"]}},
            "bar": {"color": COLORS["gold"]},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 50], "color": "rgba(225,88,91,0.18)"},
                {"range": [50, 80], "color": "rgba(231,178,60,0.18)"},
                {"range": [80, 100], "color": "rgba(47,174,124,0.18)"},
            ],
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_BODY, color=COLORS["text"]),
        margin=dict(l=20, r=20, t=40, b=10),
        height=220,
    )
    return fig


def render_response_gauges():
    """Renders two gauge charts summarizing case resolution and response speed."""
    with st.container(border=True):
        section_header("Resolution & Response Rates")
        rates = get_response_rate_data()
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(_gauge_figure(rates["resolution_rate"], "Cases Resolved"), use_container_width=True)
        with col2:
            st.plotly_chart(_gauge_figure(rates["response_within_48h"], "Acknowledged Within 48h"), use_container_width=True)


def render_monthly_trend_chart():
    """Renders a line/area chart of monthly fraud case trends."""
    with st.container(border=True):
        section_header("Monthly Fraud Cases (Jan – Jul)")
        df = get_monthly_trend_data()
        fig = px.area(
            df, x="Month", y="Fraud Cases", markers=True,
        )
        fig.update_traces(line_color=COLORS["gold"], fillcolor="rgba(231,178,60,0.15)")
        apply_chart_theme(fig)
        st.plotly_chart(fig, use_container_width=True)


def render_fraud_category_pie():
    """Renders a donut chart of fraud category distribution."""
    with st.container(border=True):
        section_header("Fraud Categories")
        df = get_fraud_category_data()
        fig = px.pie(
            df, names="Category", values="Percentage", hole=0.55,
        )
        fig.update_traces(textinfo="percent", textfont_color=COLORS["text"])
        apply_chart_theme(fig)
        fig.update_layout(legend=dict(orientation="v", font=dict(size=11)))
        st.plotly_chart(fig, use_container_width=True)


def render_fraud_methods_chart():
    """Renders a horizontal bar chart of the top fraud methods."""
    with st.container(border=True):
        section_header("Top Fraud Methods")
        df = get_fraud_methods_data().sort_values("Cases", ascending=True)
        fig = px.bar(
            df, x="Cases", y="Method", orientation="h", text="Cases",
            color="Method", color_discrete_sequence=CHART_COLORWAY,
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(showlegend=False)
        apply_chart_theme(fig)
        st.plotly_chart(fig, use_container_width=True)


def render_recent_cases_table():
    """Renders a table of recent sample fraud cases.

    The full schema has 21 columns, which is too wide to read comfortably
    in one table. By default we show a compact summary view, with a
    checkbox to reveal every field. Clicking a row opens a popup dialog
    with full case details via `show_case_details`.
    """
    with st.container(border=True):
        section_header("Recent Fraud Cases")
        st.caption("Click a row to view full case details, including sources and summary.")
        df = get_recent_cases_data()

        summary_columns = [
            "Date", "Fraud_Category", "Fraud_Method", "Suspect_Name",
            "Victim_Type", "Amount_Lost_USD",
        ]

        show_all = st.checkbox("Show all fields", value=False)
        # st.write(df.columns.tolist())
        display_df = df if show_all else df[summary_columns]

        event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="cases_table",
        )

        selected_rows = event.selection.rows if event and event.selection else []
        if selected_rows:
            show_case_details(df.iloc[selected_rows[0]], table_key="cases_table")


@st.dialog("Fraud Case Details")
def show_case_details(case, table_key):
    """Renders a popup dialog with the full details of a selected fraud case,
    including colored status badges, the source URL, and the summary.

    `table_key` is the key of the underlying st.dataframe — its row
    selection persists across reruns, so Closing must explicitly clear
    it, otherwise the same row stays "selected" and the dialog would
    reopen immediately."""
    st.markdown(f"### {case['Fraud_Category']} — {case['Location']}")
    st.caption(case["Date"])

    yes_no_color = lambda v: COLORS["red"] if v == "Yes" else COLORS["green"]
    badges_html = " ".join([
        badge(f"Cross-border: {case['Cross_Border_Fraud']}", yes_no_color(case["Cross_Border_Fraud"])),
        badge(f"Money laundering: {case['Money_Laundering_Involved']}", yes_no_color(case["Money_Laundering_Involved"])),
        badge(f"Charges: {case['Charges']}", COLORS["gold"]),
        badge(f"Court: {case['Court_Status']}", COLORS["blue"]),
    ])
    st.markdown(badges_html, unsafe_allow_html=True)
    st.markdown("")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Fraud Method:** {case['Fraud_Method']}")
        st.write(f"**Fraud Technique:** {case['Fraud_Technique']}")
        # st.write(f"**Amount Lost:** USD {case['Amount_Lost_USD']:,}")
        st.write(f"**Number of Victims:** {case['Number_of_Victims']}")
        st.write(f"**Victim Type:** {case['Victim_Type']}")
        st.write(f"**Victim Country:** {case['Victim_Country']}")
    with col2:
        st.write(f"**Platform Used:** {case['Platform_Used']}")
        st.write(f"**Suspect Name:** {case['Suspect_Name']}")
        st.write(f"**Criminal Network:** {case['Criminal_Network']}")
        st.write(f"**Investigating Agencies:** {case['Investigating_Agencies']}")
        st.write(f"**Source:** {case['Source_Name']} ({case['Source_Type']})")
        st.write(f"**Source URL:** {case['Source_URL']}")

    st.markdown("---")
    st.markdown("**Summary**")
    st.info(case["Summary"])

    if st.button("Close"):
        st.session_state[table_key] = {"selection": {"rows": [], "columns": []}}
        st.rerun()


def render_victim_demographics_pie():
    """Renders a donut chart of victim demographic groups."""
    with st.container(border=True):
        section_header("Victim Demographics")
        df = get_victim_demographics_data()
        fig = px.pie(df, names="Group", values="Value", hole=0.55)
        fig.update_traces(textinfo="percent", textfont_color=COLORS["text"])
        apply_chart_theme(fig)
        fig.update_layout(legend=dict(orientation="v", font=dict(size=11)))
        st.plotly_chart(fig, use_container_width=True)


def render_data_sources():
    """Renders the list of example data sources monitored, as styled cards."""
    with st.container(border=True):
        section_header("Data Sources Monitored")
        sources = get_data_sources()
        type_color = {"Government": COLORS["green"], "Media": COLORS["blue"], "International": COLORS["purple"]}
        rows_html = "".join(
            f'<div style="display:flex; justify-content:space-between; align-items:center; '
            f'padding:8px 4px; border-bottom:1px solid {COLORS["border"]};">'
            f'<span>{name}</span>'
            f'{badge(source_type, type_color.get(source_type, COLORS["blue"]))}'
            f'</div>'
            for name, source_type in sources
        )
        st.markdown(rows_html, unsafe_allow_html=True)


# ============================================================
# PAGE LAYOUTS
# ============================================================

def page_dashboard():
    render_hero("A national overview of reported fraud activity across Ghana.")
    render_kpi_cards()

    tab_overview, tab_cases, tab_sources = st.tabs(["📊 Overview", "🗂️ Case Log", "🌐 Sources & Alerts"])

    with tab_overview:
        col1, col2 = st.columns([1.3, 1])
        with col1:
            render_monthly_trend_chart()
        with col2:
            render_fraud_category_pie()

        render_fraud_methods_chart()
        render_response_gauges()

    with tab_cases:
        render_recent_cases_table()
        render_victim_demographics_pie()

    with tab_sources:
        render_data_sources()
        sample_alerts = [
            # "Spike in Mobile Money Fraud reported in Greater Accra region.",
            # "New phishing campaign impersonating a major bank detected.",
        ]
        with st.container(border=True):
            section_header("Active Alerts")
            for alert in sample_alerts:
                st.markdown(f'<div class="alert-card">⚠️ {alert}</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="footer-note">Ghana Fraud Intelligence Repository — (c) Ahuofe Mango · '
        "2026.</div>",
        unsafe_allow_html=True,
    )


def page_fraud_cases():
    render_hero("Browse recently reported fraud cases. Click any row for full details.")
    render_recent_cases_table()


def page_analytics():
    render_hero("A high-level analytics overview of fraud activity trends and categories.")
    render_kpi_cards()
    col1, col2 = st.columns([1.3, 1])
    with col1:
        render_monthly_trend_chart()
    with col2:
        render_fraud_category_pie()
    render_response_gauges()


def page_fraud_methods():
    render_hero("The most common techniques fraudsters use to defraud victims.")
    render_fraud_methods_chart()


def page_victim_profiles():
    render_hero("An overview of who is most affected by frauds in Ghana.")
    render_victim_demographics_pie()


# def page_reports():
#     render_hero("Generate and export summary reports.")
#     with st.container(border=True):
#         section_header("Report Exports")
        # st.info("Downloadable PDF and Excel reports will appear here in a future version.")


def page_alerts():
    render_hero("Recent alerts and emerging fraud patterns worth watching.")
    sample_alerts = [
        # "Spike in Mobile Money Fraud reported in Greater Accra region.",
        # "New phishing campaign impersonating a major bank detected.",
        # "Increase in fake investment platform complaints this week.",
    ]
    with st.container(border=True):
        section_header("Active Alerts")
        for alert in sample_alerts:
            st.markdown(f'<div class="alert-card">⚠️ {alert}</div>', unsafe_allow_html=True)


def page_sources():
    render_hero("Organizations and platforms monitored for fraud intelligence.")
    render_data_sources()


# ============================================================
# MAIN APP ENTRY POINT
# ============================================================

def main():
    configure_page()
    inject_custom_css()
    selection = render_sidebar()

    pages = {
        "Dashboard": page_dashboard,
        "Fraud Cases": page_fraud_cases,
        "Fraud Methods": page_fraud_methods,
        "Analytics": page_analytics,
        "Victim Profiles": page_victim_profiles,
        # "Reports": page_reports,
        # "Alerts": page_alerts,
        "Sources": page_sources,
    }
    pages[selection]()


if __name__ == "__main__":
    main()