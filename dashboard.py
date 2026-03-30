import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Telecom Customer Risk Dashboard",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("mobitel_dashboard_ready.csv")

df = load_data()

# --------------------------------------------------
# TITLE & DESCRIPTION
# --------------------------------------------------
st.title("📊 Telecom Customer Risk Dashboard")

st.markdown("""
This dashboard provides **model-assisted customer risk insights**.  
Predictions are **decision-support tools** and should not be used for  
fully automated actions.
""")

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("Filter Options")

plan_filter = st.sidebar.multiselect(
    "Plan Type",
    df["plan_type"].unique(),
    default=df["plan_type"].unique()
)

risk_filter = st.sidebar.multiselect(
    "Risk Level",
    df["risk_level"].unique(),
    default=df["risk_level"].unique()
)

filtered_df = df[
    (df["plan_type"].isin(plan_filter)) &
    (df["risk_level"].isin(risk_filter))
]

# --------------------------------------------------
# KPI METRICS
# --------------------------------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Customers", len(filtered_df))
col2.metric(
    "High Risk Customers",
    (filtered_df["risk_level"] == "High Risk").sum()
)
col3.metric(
    "Avg Monthly Bill",
    f"{filtered_df['monthly_bill'].mean():.2f}"
)

# --------------------------------------------------
# FUNCTION: DOWNLOAD PLOT
# --------------------------------------------------
def plot_download(fig, filename):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)

    st.download_button(
        label="⬇ Download Chart",
        data=buf,
        file_name=filename,
        mime="image/png"
    )

# --------------------------------------------------
# ALL CHARTS IN ONE ROW
# --------------------------------------------------
st.subheader("📈 Customer Risk Insights")

# Create 3 equal columns for charts
chart_col1, chart_col2, chart_col3 = st.columns(3)

# -------- Chart 1: Risk Distribution --------
with chart_col1:
    st.markdown("**Risk Distribution**")
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    sns.countplot(
        x="risk_level",
        data=filtered_df,
        order=["Low Risk", "Medium Risk", "High Risk"],
        palette="Set2",
        ax=ax1
    )
    ax1.set_xlabel("Risk Level")
    ax1.set_ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig1)
    plot_download(fig1, "risk_distribution.png")

# -------- Chart 2: Monthly Bill by Risk --------
with chart_col2:
    st.markdown("**Monthly Bill by Risk**")
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    sns.boxplot(
        x="risk_level",
        y="monthly_bill",
        data=filtered_df,
        order=["Low Risk", "Medium Risk", "High Risk"],
        palette="Set2",
        ax=ax2
    )
    ax2.set_xlabel("Risk Level")
    ax2.set_ylabel("Monthly Bill")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig2)
    plot_download(fig2, "monthly_bill_by_risk.png")

# -------- Chart 3: Usage vs Risk --------
with chart_col3:
    st.markdown("**Data Usage vs Monthly Bill**")
    fig3, ax3 = plt.subplots(figsize=(5, 4))
    sns.scatterplot(
        x="data_usage_gb",
        y="monthly_bill",
        hue="risk_level",
        data=filtered_df,
        palette="Set2",
        ax=ax3
    )
    ax3.set_xlabel("Data Usage (GB)")
    ax3.set_ylabel("Monthly Bill")
    ax3.legend(title="Risk Level", loc="best", fontsize=8)
    plt.tight_layout()
    st.pyplot(fig3)
    plot_download(fig3, "usage_vs_risk.png")

# --------------------------------------------------
# DATA PREVIEW
# --------------------------------------------------
st.subheader("📋 Sample Customer Records")
st.dataframe(filtered_df.head(50))

# --------------------------------------------------
# USER INPUT RISK CHECKER
# --------------------------------------------------
st.subheader("🔍 Check Your Risk Level")

with st.form("risk_form"):
    plan_type = st.selectbox(
        "Plan Type",
        df["plan_type"].unique()
    )

    monthly_bill = st.number_input(
        "Monthly Bill",
        min_value=0.0,
        step=100.0
    )

    data_usage = st.number_input(
        "Monthly Data Usage (GB)",
        min_value=0.0,
        step=1.0
    )

    submit = st.form_submit_button("Check Risk")

# --------------------------------------------------
# RISK LOGIC & OUTPUT
# --------------------------------------------------
if submit:
    if monthly_bill > 5000 and data_usage < 5:
        risk = "High Risk"
        emoji = "🔴"
    elif monthly_bill > 3000:
        risk = "Medium Risk"
        emoji = "🟠"
    else:
        risk = "Low Risk"
        emoji = "🟢"

    st.markdown(f"""
    ## {emoji} Risk Assessment Result

    **Predicted Risk Level:** **{risk}**

    ⚠ *This assessment is for decision-support only and should not be used
    for automated customer decisions.*
    """)