"""Field Service Reporting Copilot — Streamlit dashboard + natural language Q&A."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_jobs
from copilot import ask

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Apex Field Service Copilot",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 4rem; padding-bottom: 2rem; }

    /* Section labels */
    .section-label {
        font-size: 10.5px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #475569;
        margin-top: 6px;
        margin-bottom: 10px;
        padding-bottom: 6px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }

    /* KPI cards */
    .kpi-card {
        background: linear-gradient(160deg, #181d32 0%, #1c2245 100%);
        border-radius: 10px;
        padding: 14px 16px 12px;
        border: 1px solid rgba(79, 142, 247, 0.1);
        box-shadow: 0 2px 12px rgba(0,0,0,0.3);
        margin-bottom: 2px;
        min-height: 90px;
    }
    .kpi-label {
        font-size: 10px;
        font-weight: 600;
        color: #4f6380;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 23px;
        font-weight: 700;
        color: #e2e8f0;
        line-height: 1.25;
    }
    .kpi-sub {
        font-size: 9.5px;
        color: #334155;
        margin-top: 2px;
    }
    .badge {
        font-size: 9.5px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 20px;
        display: inline-block;
        margin-top: 5px;
        letter-spacing: 0.02em;
    }
    .badge-green  { background: rgba(52,211,153,0.12); color: #34d399; border: 1px solid rgba(52,211,153,0.2); }
    .badge-yellow { background: rgba(251,191,36,0.12);  color: #fbbf24; border: 1px solid rgba(251,191,36,0.2); }
    .badge-red    { background: rgba(248,113,113,0.12); color: #f87171; border: 1px solid rgba(248,113,113,0.2); }
    .badge-blue   { background: rgba(79,142,247,0.12);  color: #4f8ef7; border: 1px solid rgba(79,142,247,0.2); }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] { height: 40px; padding: 0 20px; border-radius: 6px 6px 0 0; font-weight: 500; }

    h4 { font-size: 13px !important; font-weight: 600 !important; margin-bottom: 2px !important; color: #94a3b8 !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CAT_COLORS = {"Installation": "#4f8ef7", "Repair": "#f7824f", "Maintenance": "#52c97a"}


def kpi(label: str, value: str, badge_text: str = "", badge_cls: str = "badge-blue", sub: str = "") -> str:
    badge = f'<span class="badge {badge_cls}">{badge_text}</span>' if badge_text else ""
    sub_div = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {badge}{sub_div}
    </div>
    """


def bench_cls(val: float, good: float, warn: float, higher_is_better: bool = True) -> str:
    if higher_is_better:
        return "badge-green" if val >= good else ("badge-yellow" if val >= warn else "badge-red")
    else:
        return "badge-green" if val <= good else ("badge-yellow" if val <= warn else "badge-red")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600)
def get_data() -> pd.DataFrame:
    return load_jobs()


df_full = get_data()

# Ensure job_category exists even if data_loader version on server is older
if "job_category" not in df_full.columns:
    _INSTALL = {
        "Zone Control Installation", "Mini-Split Installation", "Heat Pump Installation",
        "Indoor Air Quality Install", "Furnace Replacement", "Air Handler Replacement",
        "AC Replacement", "Thermostat Installation",
    }
    _REPAIR = {
        "AC Repair", "Furnace Repair", "Heat Pump Repair", "Mini-Split Repair",
        "Blower Motor Replacement", "Duct Repair", "Refrigerant Recharge",
    }
    df_full["job_category"] = df_full["job_type"].map(
        lambda t: "Installation" if t in _INSTALL else ("Repair" if t in _REPAIR else "Maintenance")
    )

# ---------------------------------------------------------------------------
# Sidebar — filters
# ---------------------------------------------------------------------------

with st.sidebar:
    st.image("https://img.icons8.com/fluency/48/maintenance.png", width=48)
    st.title("Apex Home Services")
    st.caption("HVAC Field Service Copilot")
    st.divider()

    date_min = df_full["scheduled_date"].min().date()
    date_max = df_full["scheduled_date"].max().date()
    date_range = st.date_input(
        "Date Range",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    st.divider()
    st.markdown("**Job Filters**")

    all_statuses = ["Completed", "Dispatched", "Parts Ordered", "Pending Revisit",
                    "Incomplete", "On Hold", "Cancelled", "No Access"]
    statuses = st.multiselect("Job Status", options=all_statuses, default=["Completed"])

    all_categories = sorted(df_full["job_category"].unique().tolist())
    job_categories = st.multiselect("Job Category", options=all_categories, default=all_categories)

    all_customer_types = sorted(df_full["customer_type"].unique().tolist())
    customer_types = st.multiselect("Customer Type", options=all_customer_types, default=all_customer_types)

    all_priorities = ["Emergency", "High", "Medium", "Low"]
    priorities = st.multiselect("Priority", options=all_priorities, default=all_priorities)

    st.divider()
    st.caption("Filters apply to both the dashboard and the copilot.")

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------

df = df_full.copy()
if statuses:
    df = df[df["status"].isin(statuses)]
if job_categories:
    df = df[df["job_category"].isin(job_categories)]
if customer_types:
    df = df[df["customer_type"].isin(customer_types)]
if priorities:
    df = df[df["priority"].isin(priorities)]
if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    df = df[(df["scheduled_date"] >= start) & (df["scheduled_date"] <= end)]

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_dash, tab_copilot = st.tabs(["📊  Dashboard", "💬  Copilot"])

# ===========================================================================
# TAB 1 — DASHBOARD
# ===========================================================================

with tab_dash:
    completed = df[df["status"] == "Completed"]

    # ---- Derived metrics ----
    total_jobs = len(df)
    total_rev = completed["total_cost_usd"].sum()
    avg_ticket = completed["total_cost_usd"].mean() if len(completed) > 0 else 0.0
    avg_csat = completed["csat_score"].mean()
    ftf_rate = df["first_time_fix"].mean() if len(df) > 0 else 0.0
    callback_rate = df["revisit_required"].mean() if len(df) > 0 else 0.0

    # Revenue / truck / day
    if len(completed) > 0:
        _daily_rev = (
            completed.assign(_date=completed["scheduled_date"].dt.date)
            .groupby(["technician_name", "_date"])["total_cost_usd"].sum()
        )
        rev_per_truck_day = _daily_rev.mean()
    else:
        rev_per_truck_day = 0.0

    # Jobs / day / technician
    if len(df) > 0:
        _daily_jobs = (
            df.assign(_date=df["scheduled_date"].dt.date)
            .groupby(["technician_name", "_date"])["job_id"].count()
        )
        jobs_per_day = _daily_jobs.mean()
    else:
        jobs_per_day = 0.0

    # Labor efficiency
    total_labor_hrs = completed["labor_hours"].sum() if len(completed) > 0 else 0
    labor_eff = total_rev / total_labor_hrs if total_labor_hrs > 0 else 0.0

    # Billed efficiency (labor cost % of ticket)
    billed_eff = (
        completed["labor_cost_usd"].sum() / total_rev
        if len(completed) > 0 and total_rev > 0 else 0.0
    )

    # Call booking rate
    call_book_rate = None
    if "call_source" in df.columns:
        inbound = df[df["call_source"] == "Inbound Call"]
        _booked = {"Completed", "Parts Ordered", "Dispatched", "Pending Revisit"}
        call_book_rate = (
            len(inbound[inbound["status"].isin(_booked)]) / len(inbound)
            if len(inbound) > 0 else None
        )

    # Membership conversion rate
    mem_conv_rate = None
    if "membership_offered" in df.columns:
        _offered = df[df["membership_offered"] == True]
        mem_conv_rate = (
            df["membership_converted"].sum() / len(_offered)
            if len(_offered) > 0 else None
        )

    # Lead turnover (replacement close rate)
    lead_turnover = None
    if "replacement_opportunity" in df.columns:
        _opps = df[df["replacement_opportunity"] == True]
        lead_turnover = (
            df["replacement_sold"].sum() / len(_opps)
            if len(_opps) > 0 else None
        )

    # =========================================================================
    # Section 1 — Business Overview
    # =========================================================================
    st.markdown('<div class="section-label">Business Overview</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(kpi("Total Jobs", f"{total_jobs:,}", "All statuses", "badge-blue"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi("Total Revenue", f"${total_rev:,.0f}", "Completed jobs", "badge-blue"), unsafe_allow_html=True)
    with c3:
        if avg_ticket > 0:
            st.markdown(kpi(
                "Avg Ticket", f"${avg_ticket:,.0f}",
                "Above $500" if avg_ticket >= 500 else "Below $500",
                bench_cls(avg_ticket, 500, 300),
            ), unsafe_allow_html=True)
        else:
            st.markdown(kpi("Avg Ticket", "—"), unsafe_allow_html=True)
    with c4:
        if rev_per_truck_day > 0:
            badge = "On Target" if rev_per_truck_day >= 2000 else ("Near Target" if rev_per_truck_day >= 1500 else "Below Target")
            st.markdown(kpi(
                "Rev / Truck / Day", f"${rev_per_truck_day:,.0f}",
                badge, bench_cls(rev_per_truck_day, 2000, 1500),
                sub="Target: $2,000–$3,000",
            ), unsafe_allow_html=True)
        else:
            st.markdown(kpi("Rev / Truck / Day", "—"), unsafe_allow_html=True)
    with c5:
        if jobs_per_day > 0:
            badge = "On Target" if jobs_per_day >= 2 else "Below Target"
            st.markdown(kpi(
                "Jobs / Day / Tech", f"{jobs_per_day:.1f}",
                badge, bench_cls(jobs_per_day, 3, 2),
                sub="Target: 2–4 jobs",
            ), unsafe_allow_html=True)
        else:
            st.markdown(kpi("Jobs / Day / Tech", "—"), unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    c6, c7, c8, c9, c10 = st.columns(5)
    with c6:
        badge = "Leading" if ftf_rate >= 0.90 else ("On Track" if ftf_rate >= 0.77 else "Below Avg")
        st.markdown(kpi(
            "First-Time Fix Rate", f"{ftf_rate:.1%}",
            badge, bench_cls(ftf_rate, 0.90, 0.77),
            sub="Avg ≥77% · Leading ≥90%",
        ), unsafe_allow_html=True)
    with c7:
        badge = "Excellent" if callback_rate <= 0.01 else ("Acceptable" if callback_rate <= 0.02 else "High — Review")
        st.markdown(kpi(
            "Callback / Recall Rate", f"{callback_rate:.1%}",
            badge, bench_cls(callback_rate, 0.01, 0.02, higher_is_better=False),
            sub="Target: ≤1%",
        ), unsafe_allow_html=True)
    with c8:
        if call_book_rate is not None:
            badge = "On Target" if call_book_rate >= 0.70 else ("Near Target" if call_book_rate >= 0.60 else "Below Target")
            st.markdown(kpi(
                "Call Book Rate", f"{call_book_rate:.1%}",
                badge, bench_cls(call_book_rate, 0.70, 0.60),
                sub="Target: ≥70%",
            ), unsafe_allow_html=True)
        else:
            st.markdown(kpi("Call Book Rate", "—"), unsafe_allow_html=True)
    with c9:
        if mem_conv_rate is not None:
            badge = "On Target" if mem_conv_rate >= 0.30 else ("Near Target" if mem_conv_rate >= 0.15 else "Below Target")
            st.markdown(kpi(
                "Membership Conv.", f"{mem_conv_rate:.1%}",
                badge, bench_cls(mem_conv_rate, 0.30, 0.15),
                sub="Target: ≥30%",
            ), unsafe_allow_html=True)
        else:
            st.markdown(kpi("Membership Conv.", "—"), unsafe_allow_html=True)
    with c10:
        if not pd.isna(avg_csat):
            badge = "Excellent" if avg_csat >= 4.5 else ("Good" if avg_csat >= 4.0 else "Needs Work")
            st.markdown(kpi(
                "Avg CSAT", f"{avg_csat:.2f} / 5",
                badge, bench_cls(avg_csat, 4.5, 4.0),
                sub="Customer satisfaction",
            ), unsafe_allow_html=True)
        else:
            st.markdown(kpi("Avg CSAT", "—"), unsafe_allow_html=True)

    # =========================================================================
    # Section 2 — Invoicing & Revenue
    # =========================================================================
    st.markdown('<div class="section-label" style="margin-top:20px">Invoicing & Revenue</div>', unsafe_allow_html=True)

    rev_l, rev_m, rev_r = st.columns([1, 1, 2])

    with rev_l:
        st.markdown("#### Revenue by Category")
        if len(completed) > 0 and "job_category" in completed.columns:
            rev_cat = completed.groupby("job_category")["total_cost_usd"].sum().reset_index()
            fig = px.pie(
                rev_cat, names="job_category", values="total_cost_usd", hole=0.55,
                color="job_category", color_discrete_map=_CAT_COLORS,
            )
            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0), height=260,
                legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center", font_size=11),
            )
            fig.update_traces(textposition="inside", textinfo="percent+label", textfont_size=10)
            st.plotly_chart(fig, use_container_width=True)

    with rev_m:
        st.markdown("#### Avg Ticket by Category")
        if len(completed) > 0 and "job_category" in completed.columns:
            ticket_cat = (
                completed.groupby("job_category")
                .agg(avg_ticket=("total_cost_usd", "mean"), job_count=("job_id", "count"))
                .reset_index()
                .sort_values("avg_ticket", ascending=True)
            )
            fig = px.bar(
                ticket_cat, x="avg_ticket", y="job_category", orientation="h",
                color="job_category", color_discrete_map=_CAT_COLORS,
                text=ticket_cat["avg_ticket"].apply(lambda v: f"${v:,.0f}"),
                labels={"avg_ticket": "Avg Ticket ($)", "job_category": ""},
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False, margin=dict(l=0, r=70, t=0, b=0), height=260)
            st.plotly_chart(fig, use_container_width=True)

    with rev_r:
        st.markdown("#### Monthly Revenue & Job Volume")
        monthly = (
            df.assign(month=df["scheduled_date"].dt.to_period("M").astype(str))
            .groupby("month")
            .agg(jobs=("job_id", "count"), revenue=("total_cost_usd", "sum"))
            .reset_index()
            .sort_values("month")
        )
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=monthly["month"], y=monthly["jobs"],
            name="Jobs", marker_color="#4f8ef7", opacity=0.8, yaxis="y1",
        ))
        fig.add_trace(go.Scatter(
            x=monthly["month"], y=monthly["revenue"],
            name="Revenue ($)", mode="lines+markers",
            line=dict(color="#f7d34f", width=2), marker=dict(size=5), yaxis="y2",
        ))
        fig.update_layout(
            yaxis=dict(title="Jobs", title_font_size=11),
            yaxis2=dict(title="Revenue ($)", overlaying="y", side="right",
                        tickformat="$,.0f", title_font_size=11),
            legend=dict(orientation="h", y=1.1, x=0, font_size=11),
            margin=dict(l=0, r=0, t=10, b=0), height=260,
        )
        fig.update_xaxes(tickangle=-45, tickfont_size=9)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Revenue by Customer Type")
    if len(completed) > 0:
        rev_cust = (
            completed.groupby("customer_type")
            .agg(revenue=("total_cost_usd", "sum"), jobs=("job_id", "count"),
                 avg_ticket=("total_cost_usd", "mean"))
            .reset_index()
        )
        fig = px.bar(
            rev_cust, x="customer_type", y="revenue",
            color="customer_type",
            color_discrete_map={"Residential": "#4f8ef7", "Commercial": "#a78bfa"},
            text=rev_cust["revenue"].apply(lambda v: f"${v:,.0f}"),
            custom_data=["jobs", "avg_ticket"],
            labels={"revenue": "Total Revenue ($)", "customer_type": ""},
        )
        fig.update_traces(
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<br>Jobs: %{customdata[0]}<br>Avg Ticket: $%{customdata[1]:,.0f}<extra></extra>",
        )
        fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0), height=260)
        st.plotly_chart(fig, use_container_width=True)

    # =========================================================================
    # Section 3 — Field Operations
    # =========================================================================
    st.markdown('<div class="section-label" style="margin-top:20px">Field Operations</div>', unsafe_allow_html=True)

    tp_l, tp_r = st.columns(2)

    with tp_l:
        st.markdown("#### Revenue / Truck / Day")
        if len(completed) > 0:
            rtd = (
                completed.assign(_date=completed["scheduled_date"].dt.date)
                .groupby(["technician_name", "_date"])["total_cost_usd"].sum()
                .reset_index()
                .groupby("technician_name")["total_cost_usd"].mean()
                .reset_index()
                .rename(columns={"total_cost_usd": "rev_per_day"})
                .sort_values("rev_per_day", ascending=True)
            )
            rtd["color"] = rtd["rev_per_day"].apply(
                lambda x: "#e05252" if x < 1500 else ("#f7d34f" if x < 2000 else "#52c97a")
            )
            fig = go.Figure(go.Bar(
                x=rtd["rev_per_day"], y=rtd["technician_name"],
                orientation="h", marker_color=rtd["color"],
                text=[f"${r:,.0f}" for r in rtd["rev_per_day"]], textposition="outside",
            ))
            fig.add_vline(x=2000, line_dash="dot", line_color="#94a3b8",
                          annotation_text="$2,000 target", annotation_font_size=10,
                          annotation_position="top right")
            fig.update_layout(margin=dict(l=0, r=90, t=10, b=0), height=240,
                              xaxis_tickformat="$,.0f")
            st.plotly_chart(fig, use_container_width=True)

    with tp_r:
        st.markdown("#### Jobs / Day by Technician")
        if len(df) > 0:
            jpd = (
                df.assign(_date=df["scheduled_date"].dt.date)
                .groupby(["technician_name", "_date"])["job_id"].count()
                .reset_index()
                .groupby("technician_name")["job_id"].mean()
                .reset_index()
                .rename(columns={"job_id": "jobs_per_day"})
                .sort_values("jobs_per_day", ascending=True)
            )
            jpd["color"] = jpd["jobs_per_day"].apply(
                lambda x: "#e05252" if x < 2 else ("#52c97a" if x <= 4 else "#4f8ef7")
            )
            fig = go.Figure(go.Bar(
                x=jpd["jobs_per_day"], y=jpd["technician_name"],
                orientation="h", marker_color=jpd["color"],
                text=[f"{j:.1f}" for j in jpd["jobs_per_day"]], textposition="outside",
            ))
            fig.add_vline(x=2, line_dash="dot", line_color="#94a3b8",
                          annotation_text="2/day min", annotation_font_size=10,
                          annotation_position="top right")
            fig.update_layout(margin=dict(l=0, r=50, t=10, b=0), height=240)
            st.plotly_chart(fig, use_container_width=True)

    tp2_l, tp2_r = st.columns(2)

    with tp2_l:
        st.markdown("#### First-Time Fix Rate by Technician")
        if len(df) > 0:
            ftf_by_tech = (
                df.groupby(["technician_name", "technician_level"])["first_time_fix"]
                .agg(ftf_rate="mean", job_count="count")
                .reset_index()
                .sort_values("ftf_rate", ascending=True)
            )
            ftf_by_tech["color"] = ftf_by_tech["ftf_rate"].apply(
                lambda x: "#e05252" if x < 0.60 else ("#f7d34f" if x < 0.77 else "#52c97a")
            )
            fig = go.Figure(go.Bar(
                x=ftf_by_tech["ftf_rate"], y=ftf_by_tech["technician_name"],
                orientation="h", marker_color=ftf_by_tech["color"],
                text=[f"{r:.1%}" for r in ftf_by_tech["ftf_rate"]], textposition="outside",
                customdata=ftf_by_tech[["technician_level", "job_count"]],
                hovertemplate="<b>%{y}</b><br>Level: %{customdata[0]}<br>FTF: %{x:.1%}<br>Jobs: %{customdata[1]}<extra></extra>",
            ))
            fig.add_vline(x=0.77, line_dash="dot", line_color="#94a3b8",
                          annotation_text="77% avg", annotation_font_size=10,
                          annotation_position="top right")
            fig.add_vline(x=0.90, line_dash="dot", line_color="#52c97a",
                          annotation_text="90% leading", annotation_font_size=10,
                          annotation_position="bottom right")
            fig.update_layout(margin=dict(l=0, r=70, t=10, b=0), height=240,
                              xaxis_tickformat=".0%")
            st.plotly_chart(fig, use_container_width=True)

    with tp2_r:
        st.markdown("#### Avg CSAT by Technician")
        if len(completed) > 0:
            csat_by_tech = (
                completed.groupby("technician_name")["csat_score"]
                .mean().reset_index()
                .sort_values("csat_score", ascending=True)
            )
            csat_by_tech["color"] = csat_by_tech["csat_score"].apply(
                lambda x: "#e05252" if x < 3.8 else ("#f7d34f" if x < 4.2 else "#52c97a")
            )
            fig = go.Figure(go.Bar(
                x=csat_by_tech["csat_score"], y=csat_by_tech["technician_name"],
                orientation="h", marker_color=csat_by_tech["color"],
                text=[f"{s:.2f}" for s in csat_by_tech["csat_score"]], textposition="outside",
            ))
            fig.add_vline(x=4.2, line_dash="dot", line_color="#94a3b8",
                          annotation_text="4.2 target", annotation_font_size=10,
                          annotation_position="top right")
            fig.update_layout(margin=dict(l=0, r=40, t=10, b=0), height=240,
                              xaxis_range=[0, 5.5])
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Labor Efficiency (Revenue / Labor Hour)")
    if len(completed) > 0:
        leff = (
            completed.groupby("technician_name")
            .agg(revenue=("total_cost_usd", "sum"), labor_hours=("labor_hours", "sum"))
            .reset_index()
        )
        leff["rev_per_hr"] = leff["revenue"] / leff["labor_hours"]
        leff = leff.sort_values("rev_per_hr", ascending=True)
        fig = px.bar(
            leff, x="rev_per_hr", y="technician_name", orientation="h",
            color="rev_per_hr", color_continuous_scale="Teal",
            text=leff["rev_per_hr"].apply(lambda v: f"${v:,.0f}/hr"),
            labels={"rev_per_hr": "Revenue per Labor Hour ($)", "technician_name": ""},
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(coloraxis_showscale=False,
                          margin=dict(l=0, r=100, t=10, b=0), height=240,
                          xaxis_tickformat="$,.0f")
        st.plotly_chart(fig, use_container_width=True)

    # =========================================================================
    # Section 4 — Marketing & Lead Generation
    # =========================================================================
    st.markdown('<div class="section-label" style="margin-top:20px">Marketing & Lead Generation</div>', unsafe_allow_html=True)

    mkt_l, mkt_r = st.columns(2)

    with mkt_l:
        st.markdown("#### Job Source Breakdown")
        if "call_source" in df.columns:
            source_counts = df["call_source"].value_counts().reset_index()
            source_counts.columns = ["source", "jobs"]
            source_rev = (
                completed.groupby("call_source")["total_cost_usd"].sum()
                .reset_index()
                .rename(columns={"call_source": "source", "total_cost_usd": "revenue"})
            )
            source_df = source_counts.merge(source_rev, on="source", how="left").fillna(0)
            source_df = source_df.sort_values("jobs", ascending=True)
            source_colors = {
                "Inbound Call": "#4f8ef7", "Google Ads": "#f7824f",
                "Website": "#a78bfa", "Repeat Customer": "#52c97a", "Referral": "#f7d34f",
            }
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=source_df["jobs"], y=source_df["source"],
                orientation="h",
                marker_color=[source_colors.get(s, "#94a3b8") for s in source_df["source"]],
                text=source_df["jobs"], textposition="outside",
                name="Jobs",
                customdata=source_df["revenue"],
                hovertemplate="<b>%{y}</b><br>Jobs: %{x}<br>Revenue: $%{customdata:,.0f}<extra></extra>",
            ))
            fig.update_layout(margin=dict(l=0, r=50, t=10, b=0), height=260)
            st.plotly_chart(fig, use_container_width=True)

    with mkt_r:
        st.markdown("#### Membership Conversion by Technician")
        if "membership_offered" in df.columns:
            mem_by_tech = (
                df[df["membership_offered"] == True]
                .groupby("technician_name")
                .agg(offered=("membership_offered", "count"),
                     converted=("membership_converted", "sum"))
                .reset_index()
            )
            mem_by_tech["conv_rate"] = mem_by_tech["converted"] / mem_by_tech["offered"]
            mem_by_tech = mem_by_tech.sort_values("conv_rate", ascending=True)
            mem_by_tech["color"] = mem_by_tech["conv_rate"].apply(
                lambda x: "#e05252" if x < 0.15 else ("#f7d34f" if x < 0.30 else "#52c97a")
            )
            fig = go.Figure(go.Bar(
                x=mem_by_tech["conv_rate"], y=mem_by_tech["technician_name"],
                orientation="h", marker_color=mem_by_tech["color"],
                text=[f"{r:.1%}" for r in mem_by_tech["conv_rate"]], textposition="outside",
                customdata=mem_by_tech[["offered", "converted"]],
                hovertemplate="<b>%{y}</b><br>Conv: %{x:.1%}<br>Offered: %{customdata[0]}<br>Converted: %{customdata[1]}<extra></extra>",
            ))
            fig.add_vline(x=0.30, line_dash="dot", line_color="#94a3b8",
                          annotation_text="30% target", annotation_font_size=10,
                          annotation_position="top right")
            fig.update_layout(margin=dict(l=0, r=60, t=10, b=0), height=260,
                              xaxis_tickformat=".0%", xaxis_range=[0, 0.65])
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Lead Turnover (Replacement Close Rate by Technician)")
    if "replacement_opportunity" in df.columns:
        lt = (
            df[df["replacement_opportunity"] == True]
            .groupby("technician_name")
            .agg(opportunities=("replacement_opportunity", "count"),
                 sold=("replacement_sold", "sum"))
            .reset_index()
        )
        lt["close_rate"] = lt["sold"] / lt["opportunities"]
        lt = lt.sort_values("close_rate", ascending=True)
        lt["color"] = lt["close_rate"].apply(
            lambda x: "#e05252" if x < 0.15 else ("#f7d34f" if x < 0.30 else "#52c97a")
        )
        fig = go.Figure(go.Bar(
            x=lt["close_rate"], y=lt["technician_name"],
            orientation="h", marker_color=lt["color"],
            text=[f"{r:.1%}" for r in lt["close_rate"]], textposition="outside",
            customdata=lt[["opportunities", "sold"]],
            hovertemplate="<b>%{y}</b><br>Close Rate: %{x:.1%}<br>Opportunities: %{customdata[0]}<br>Sold: %{customdata[1]}<extra></extra>",
        ))
        fig.add_vline(x=0.30, line_dash="dot", line_color="#94a3b8",
                      annotation_text="30% target", annotation_font_size=10,
                      annotation_position="top right")
        fig.update_layout(margin=dict(l=0, r=60, t=10, b=0), height=240,
                          xaxis_tickformat=".0%", xaxis_range=[0, 0.75])
        st.plotly_chart(fig, use_container_width=True)



# ===========================================================================
# TAB 2 — COPILOT
# ===========================================================================

with tab_copilot:

    st.markdown("### Ask anything about your field service data")

    filter_summary = []
    if statuses != ["Completed"]:
        filter_summary.append(f"Status: {', '.join(statuses)}")
    if set(job_categories) != set(all_categories):
        filter_summary.append(f"Category: {', '.join(job_categories)}")

    if filter_summary:
        st.info(f"Active filters — {' | '.join(filter_summary)} — copilot answers reflect filtered data ({len(df):,} jobs).")
    else:
        st.info(f"Showing all {len(df):,} jobs. Use sidebar filters to scope the copilot's answers.")

    st.markdown("**Suggested questions:**")
    suggestions = [
        "Which technician has the highest first-time fix rate?",
        "What are the top 5 job types by revenue?",
        "Which city has the most emergency jobs?",
        "Who has the lowest CSAT and what job types are they struggling with?",
        "Compare senior vs. junior technician performance across all key metrics.",
        "Which months had the highest revisit rates?",
    ]
    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        if cols[i % 3].button(suggestion, key=f"sug_{i}", use_container_width=True):
            st.session_state.setdefault("messages", [])
            st.session_state["messages"].append({"role": "user", "content": suggestion})
            st.session_state["pending_query"] = suggestion

    st.divider()

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"], avatar="🧑‍💼" if msg["role"] == "user" else "🔧"):
            st.markdown(msg["content"])

    if "pending_query" in st.session_state:
        query = st.session_state.pop("pending_query")
        with st.chat_message("assistant", avatar="🔧"):
            with st.spinner("Querying data..."):
                response = ask(query, df)
            st.markdown(response)
        st.session_state["messages"].append({"role": "assistant", "content": response})
        st.rerun()

    if prompt := st.chat_input("Ask about jobs, technicians, revenue, CSAT..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💼"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="🔧"):
            with st.spinner("Querying data..."):
                response = ask(prompt, df)
            st.markdown(response)
        st.session_state["messages"].append({"role": "assistant", "content": response})

    if st.session_state.get("messages"):
        if st.button("Clear chat", type="secondary"):
            st.session_state["messages"] = []
            st.rerun()
