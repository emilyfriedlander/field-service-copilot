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
    .metric-card {
        background: #1e2130;
        border-radius: 10px;
        padding: 16px 20px;
        border-left: 4px solid #4f8ef7;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        padding: 0 20px;
        border-radius: 6px 6px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

@st.cache_data
def get_data() -> pd.DataFrame:
    return load_jobs()

df_full = get_data()

# ---------------------------------------------------------------------------
# Sidebar — filters
# ---------------------------------------------------------------------------

with st.sidebar:
    st.image("https://img.icons8.com/fluency/48/maintenance.png", width=48)
    st.title("Apex Home Services")
    st.caption("HVAC Field Service Copilot")
    st.divider()

    all_statuses = ["Completed", "Dispatched", "Parts Ordered", "Pending Revisit",
                    "Incomplete", "On Hold", "Cancelled", "No Access"]
    statuses = st.multiselect(
        "Job Status",
        options=all_statuses,
        default=["Completed"],
    )

    tech_levels = st.multiselect(
        "Technician Level",
        options=["Junior", "Mid", "Senior"],
        default=["Junior", "Mid", "Senior"],
    )

    date_min = df_full["scheduled_date"].min().date()
    date_max = df_full["scheduled_date"].max().date()
    date_range = st.date_input(
        "Date Range",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    st.divider()
    st.caption("Filters apply to both the dashboard and the copilot.")

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------

df = df_full.copy()
if statuses:
    df = df[df["status"].isin(statuses)]
if tech_levels:
    df = df[df["technician_level"].isin(tech_levels)]
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

    st.markdown("### Key Metrics")

    completed = df[df["status"] == "Completed"]
    total_jobs   = len(df)
    total_rev    = df["total_cost_usd"].sum()
    avg_ticket   = df["total_cost_usd"].mean()
    avg_csat     = completed["csat_score"].mean()
    ftf_rate     = df["first_time_fix"].mean()
    revisit_rate = df["revisit_required"].mean() if "revisit_required" in df.columns else 0.0

    # Call booking rate: completed + parts-ordered jobs from inbound calls / all inbound call jobs
    if "call_source" in df.columns:
        inbound = df[df["call_source"] == "Inbound Call"]
        booked_statuses = {"Completed", "Parts Ordered", "Dispatched", "Pending Revisit"}
        call_booking_rate = (
            len(inbound[inbound["status"].isin(booked_statuses)]) / len(inbound)
            if len(inbound) > 0 else 0.0
        )
    else:
        call_booking_rate = None

    # Membership conversion rate
    if "membership_offered" in df.columns:
        offered = df[df["membership_offered"] == True]
        mem_conv_rate = (
            df["membership_converted"].sum() / len(offered)
            if len(offered) > 0 else 0.0
        )
    else:
        mem_conv_rate = None

    # Lead turnover (system replacement close rate)
    if "replacement_opportunity" in df.columns:
        opps = df[df["replacement_opportunity"] == True]
        lead_turnover = (
            df["replacement_sold"].sum() / len(opps)
            if len(opps) > 0 else 0.0
        )
    else:
        lead_turnover = None

    # Row 1 KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Jobs",       f"{total_jobs:,}")
    c2.metric("Total Revenue",    f"${total_rev:,.0f}")
    c3.metric("Avg Ticket Size",  f"${avg_ticket:,.0f}")
    c4.metric("Call Booking Rate",
              f"{call_booking_rate:.1%}" if call_booking_rate is not None else "—")

    # Row 2 KPIs
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("First-Time Fix Rate",       f"{ftf_rate:.1%}")
    c6.metric("Avg CSAT",                  f"{avg_csat:.2f} / 5" if not pd.isna(avg_csat) else "—")
    c7.metric("Membership Conv. Rate",     f"{mem_conv_rate:.1%}" if mem_conv_rate is not None else "—")
    c8.metric("Lead Turnover Rate",        f"{lead_turnover:.1%}" if lead_turnover is not None else "—")

    st.divider()

    # ---- Row 1: Avg ticket by job type | Jobs by status ----
    row1_l, row1_r = st.columns([3, 2])

    with row1_l:
        st.markdown("#### Avg Ticket Size by Job Type")
        ticket_by_type = (
            df.groupby("job_type")["total_cost_usd"]
            .agg(avg_ticket="mean", job_count="count")
            .reset_index()
            .sort_values("avg_ticket", ascending=True)
        )
        fig = px.bar(
            ticket_by_type,
            x="avg_ticket",
            y="job_type",
            orientation="h",
            color="avg_ticket",
            color_continuous_scale="Blues",
            labels={"avg_ticket": "Avg Ticket ($)", "job_type": ""},
            text=ticket_by_type["avg_ticket"].apply(lambda v: f"${v:,.0f}"),
            custom_data=["job_count"],
        )
        fig.update_traces(
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Avg Ticket: $%{x:,.0f}<br>Jobs: %{customdata[0]}<extra></extra>",
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False,
                          margin=dict(l=0, r=60, t=0, b=0), height=340)
        st.plotly_chart(fig, use_container_width=True)

    with row1_r:
        st.markdown("#### Jobs by Status")
        status_order = ["Completed", "Dispatched", "Parts Ordered", "Pending Revisit",
                        "Incomplete", "On Hold", "Cancelled", "No Access"]
        status_colors = {
            "Completed":       "#52c97a",
            "Dispatched":      "#4f8ef7",
            "Parts Ordered":   "#a78bfa",
            "Pending Revisit": "#f7d34f",
            "Incomplete":      "#f7824f",
            "On Hold":         "#94a3b8",
            "Cancelled":       "#e05252",
            "No Access":       "#cbd5e1",
        }
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        fig = px.pie(
            status_counts,
            names="status",
            values="count",
            hole=0.55,
            color="status",
            color_discrete_map=status_colors,
            category_orders={"status": status_order},
        )
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=340,
                          legend=dict(orientation="v", x=1.0, y=0.5))
        fig.update_traces(textposition="inside", textinfo="percent")
        st.plotly_chart(fig, use_container_width=True)

    # ---- Row 2: Monthly job volume & revenue ----
    st.markdown("#### Monthly Job Volume & Revenue")
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
        name="Jobs", marker_color="#4f8ef7",
        yaxis="y1",
    ))
    fig.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["revenue"],
        name="Revenue ($)", mode="lines+markers",
        line=dict(color="#f7d34f", width=2),
        marker=dict(size=5),
        yaxis="y2",
    ))
    fig.update_layout(
        yaxis=dict(title="Jobs"),
        yaxis2=dict(title="Revenue ($)", overlaying="y", side="right",
                    tickformat="$,.0f"),
        legend=dict(orientation="h", y=1.08),
        margin=dict(l=0, r=0, t=10, b=0),
        height=260,
        barmode="group",
    )
    fig.update_xaxes(tickangle=-45, tickfont_size=10)
    st.plotly_chart(fig, use_container_width=True)

    # ---- Row 3: FTF by technician | CSAT by technician ----
    row3_l, row3_r = st.columns(2)

    with row3_l:
        st.markdown("#### First-Time Fix Rate by Technician")
        ftf_by_tech = (
            df.groupby(["technician_name", "technician_level"])["first_time_fix"]
            .agg(ftf_rate="mean", job_count="count")
            .reset_index()
            .sort_values("ftf_rate", ascending=True)
        )
        ftf_by_tech["color"] = ftf_by_tech["ftf_rate"].apply(
            lambda x: "#e05252" if x < 0.60 else ("#f7d34f" if x < 0.75 else "#52c97a")
        )
        fig = go.Figure(go.Bar(
            x=ftf_by_tech["ftf_rate"],
            y=ftf_by_tech["technician_name"],
            orientation="h",
            marker_color=ftf_by_tech["color"],
            text=[f"{r:.1%}" for r in ftf_by_tech["ftf_rate"]],
            textposition="outside",
            customdata=ftf_by_tech[["technician_level", "job_count"]],
            hovertemplate="<b>%{y}</b><br>Level: %{customdata[0]}<br>FTF: %{x:.1%}<br>Jobs: %{customdata[1]}<extra></extra>",
        ))
        fig.add_vline(x=0.75, line_dash="dot", line_color="white",
                      annotation_text="75% target", annotation_position="top right")
        fig.update_layout(margin=dict(l=0, r=60, t=10, b=0), height=280,
                          xaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    with row3_r:
        st.markdown("#### Avg CSAT by Technician")
        csat_by_tech = (
            completed.groupby("technician_name")["csat_score"]
            .mean()
            .reset_index()
            .sort_values("csat_score", ascending=True)
        )
        csat_by_tech["color"] = csat_by_tech["csat_score"].apply(
            lambda x: "#e05252" if x < 3.8 else ("#f7d34f" if x < 4.2 else "#52c97a")
        )
        fig = go.Figure(go.Bar(
            x=csat_by_tech["csat_score"],
            y=csat_by_tech["technician_name"],
            orientation="h",
            marker_color=csat_by_tech["color"],
            text=[f"{s:.2f}" for s in csat_by_tech["csat_score"]],
            textposition="outside",
        ))
        fig.add_vline(x=4.2, line_dash="dot", line_color="white",
                      annotation_text="4.2 target", annotation_position="top right")
        fig.update_layout(margin=dict(l=0, r=40, t=10, b=0), height=280,
                          xaxis_range=[0, 5.5])
        st.plotly_chart(fig, use_container_width=True)

    # ---- Row 4: Revenue per tech | Membership conversion by tech ----
    row4_l, row4_r = st.columns(2)

    with row4_l:
        st.markdown("#### Revenue per Technician")
        rev_by_tech = (
            completed.groupby(["technician_name", "technician_level"])["total_cost_usd"]
            .agg(total_rev="sum", avg_ticket="mean", job_count="count")
            .reset_index()
            .sort_values("total_rev", ascending=True)
        )
        fig = go.Figure(go.Bar(
            x=rev_by_tech["total_rev"],
            y=rev_by_tech["technician_name"],
            orientation="h",
            marker_color="#4f8ef7",
            text=[f"${r:,.0f}" for r in rev_by_tech["total_rev"]],
            textposition="outside",
            customdata=rev_by_tech[["technician_level", "avg_ticket", "job_count"]],
            hovertemplate=(
                "<b>%{y}</b><br>Level: %{customdata[0]}<br>"
                "Total Rev: $%{x:,.0f}<br>Avg Ticket: $%{customdata[1]:,.0f}<br>"
                "Jobs: %{customdata[2]}<extra></extra>"
            ),
        ))
        fig.update_layout(margin=dict(l=0, r=80, t=10, b=0), height=280)
        st.plotly_chart(fig, use_container_width=True)

    with row4_r:
        st.markdown("#### Membership Conversion Rate by Technician")
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
                x=mem_by_tech["conv_rate"],
                y=mem_by_tech["technician_name"],
                orientation="h",
                marker_color=mem_by_tech["color"],
                text=[f"{r:.1%}" for r in mem_by_tech["conv_rate"]],
                textposition="outside",
                customdata=mem_by_tech[["offered", "converted"]],
                hovertemplate="<b>%{y}</b><br>Conv. Rate: %{x:.1%}<br>Offered: %{customdata[0]}<br>Converted: %{customdata[1]}<extra></extra>",
            ))
            fig.add_vline(x=0.30, line_dash="dot", line_color="white",
                          annotation_text="30% target", annotation_position="top right")
            fig.update_layout(margin=dict(l=0, r=60, t=10, b=0), height=280,
                              xaxis_tickformat=".0%", xaxis_range=[0, 0.65])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Membership data not available in this dataset.")

    # ---- Row 5: Job type by revisit rate (scatter) ----
    st.markdown("#### Job Type Quality Matrix — Revisit Rate vs. CSAT (min. 10 jobs)")
    revisit_by_type = (
        df.groupby("job_type")
        .agg(
            total=("job_id", "count"),
            revisits=("revisit_required", "sum"),
            avg_csat=("csat_score", "mean"),
            avg_value=("total_cost_usd", "mean"),
        )
        .reset_index()
    )
    revisit_by_type = revisit_by_type[revisit_by_type["total"] >= 10].copy()
    revisit_by_type["revisit_rate"] = revisit_by_type["revisits"] / revisit_by_type["total"]

    fig = px.scatter(
        revisit_by_type,
        x="revisit_rate",
        y="avg_csat",
        size="total",
        color="avg_value",
        text="job_type",
        color_continuous_scale="RdYlGn_r",
        labels={
            "revisit_rate": "Revisit Rate",
            "avg_csat": "Avg CSAT",
            "avg_value": "Avg Job Value ($)",
            "total": "Job Count",
        },
        hover_data={"total": True, "revisits": True},
    )
    fig.update_traces(textposition="top center", textfont_size=10)
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=340,
                      xaxis_tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Bubble size = job volume · Color = avg job value (green = higher) · Top-left = ideal (high CSAT, low revisits)")


# ===========================================================================
# TAB 2 — COPILOT
# ===========================================================================

with tab_copilot:

    st.markdown("### Ask anything about your field service data")

    # Show active filter context
    filter_summary = []
    if statuses != ["Completed"]:
        filter_summary.append(f"Status: {', '.join(statuses)}")
    if tech_levels != ["Junior", "Mid", "Senior"]:
        filter_summary.append(f"Level: {', '.join(tech_levels)}")

    if filter_summary:
        st.info(f"Active filters — {' | '.join(filter_summary)} — copilot answers reflect filtered data ({len(df):,} jobs).")
    else:
        st.info(f"Showing all {len(df):,} jobs. Use sidebar filters to scope the copilot's answers.")

    # Suggested prompts
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

    # Chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"], avatar="🧑‍💼" if msg["role"] == "user" else "🔧"):
            st.markdown(msg["content"])

    # Handle suggestion button clicks
    if "pending_query" in st.session_state:
        query = st.session_state.pop("pending_query")
        with st.chat_message("assistant", avatar="🔧"):
            with st.spinner("Querying data..."):
                response = ask(query, df)
            st.markdown(response)
        st.session_state["messages"].append({"role": "assistant", "content": response})
        st.rerun()

    # Chat input
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

