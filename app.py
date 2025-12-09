import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="FEMA TSA Eligibility Dashboard",
    layout="wide"
)

st.title("FEMA TSA Eligibility Dashboard")

@st.cache_data
def load_data(path="fema_sample.csv"):
    df = pd.read_csv(
        path,
        low_memory=False,
        na_values=["", " ", "NA", "NaN", "nan"]
    )

    # minimal cleaning so the charts work
    df["repairAmount"] = pd.to_numeric(df["repairAmount"], errors="coerce").fillna(0)

    df["tsaEligible"] = (
        df["tsaEligible"]
        .astype(str)
        .str.strip()
        .replace({"1": 1, "0": 0, "Yes": 1, "No": 0})
    )
    df["tsaEligible"] = pd.to_numeric(df["tsaEligible"], errors="coerce").fillna(0).astype(int)

    return df

df = load_data()

st.subheader("Data preview")
st.write(df.head())

# sidebar filters
st.sidebar.header("Filters")
state_filter = st.sidebar.multiselect(
    "Filter by damaged state",
    options=sorted(df["damagedStateAbbreviation"].dropna().unique()),
)

if state_filter:
    df_filtered = df[df["damagedStateAbbreviation"].isin(state_filter)]
else:
    df_filtered = df.copy()

st.markdown(f"### Records after filters: {len(df_filtered):,}")

# histogram of repair amount
st.subheader("Repair amount distribution")
fig_hist = px.histogram(
    df_filtered,
    x="repairAmount",
    nbins=40,
    title="Distribution of repair amount",
)
st.plotly_chart(fig_hist, use_container_width=True)

# boxplot repair amount by TSA eligibility
st.subheader("Repair amount by TSA eligibility")
fig_box = px.box(
    df_filtered,
    x="tsaEligible",
    y="repairAmount",
    labels={"tsaEligible": "TSA eligible (1 yes, 0 no)", "repairAmount": "Repair amount"},
    title="Repair amount by TSA eligibility",
)
st.plotly_chart(fig_box, use_container_width=True)

# TSA eligibility rate by state
st.subheader("TSA eligibility rate by state")
tsa_rate = (
    df_filtered.groupby("damagedStateAbbreviation")["tsaEligible"]
    .mean()
    .reset_index()
    .rename(columns={"tsaEligible": "tsa_rate"})
)

fig_state = px.bar(
    tsa_rate,
    x="damagedStateAbbreviation",
    y="tsa_rate",
    title="TSA eligibility rate by state or territory",
)
st.plotly_chart(fig_state, use_container_width=True)

st.markdown(
    """
The histogram shows how skewed the repair amounts are.
The boxplot compares damage levels for people who qualify for TSA versus people who do not.
The bar chart shows how TSA eligibility rates change by state and territory.
"""
)

st.write("Authors: Aidan Gantt")
