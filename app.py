import streamlit as st
import pandas as pd
import plotly.express as px

# set up page
st.set_page_config(
    page_title="FEMA TSA Eligibility Dashboard",
    layout="wide"
)

st.title("FEMA TSA Eligibility Dashboard")

# load data
@st.cache_data
def load_data(path="fema_sample_stratified.csv"):
    # read csv
    df = pd.read_csv(
        path,
        low_memory=False,
        na_values=["", " ", "NA", "NaN", "nan"]
    )

    # clean repair amount
    df["repairAmount"] = pd.to_numeric(df["repairAmount"], errors="coerce").fillna(0)

    # clean tsa eligibility
    df["tsaEligible"] = (
        df["tsaEligible"]
        .astype(str)
        .str.strip()
        .replace({"1": 1, "0": 0, "Yes": 1, "No": 0})
    )
    df["tsaEligible"] = pd.to_numeric(df["tsaEligible"], errors="coerce").fillna(0).astype(int)

    # clean state codes
    df["damagedStateAbbreviation"] = df["damagedStateAbbreviation"].astype(str).str.strip()

    # return cleaned data
    return df

# load dataframe
df = load_data()

# show preview
st.subheader("Data Preview")
st.write(df.head())

# sidebar filters
st.sidebar.header("Filters")
state_filter = st.sidebar.multiselect(
    "Filter by damaged state",
    options=sorted(df["damagedStateAbbreviation"].dropna().unique())
)

# apply state filter
if state_filter:
    df_filtered = df[df["damagedStateAbbreviation"].isin(state_filter)]
else:
    df_filtered = df.copy()

st.markdown(f"### Records after filters: {len(df_filtered):,}")

# histogram of repair amount
st.subheader("Repair Amount Distribution")
fig_hist = px.histogram(
    df_filtered,
    x="repairAmount",
    nbins=40,
    title="Distribution of Repair Amount"
)
st.plotly_chart(fig_hist, use_container_width=True)

# boxplot for tsa eligibility
st.subheader("Repair Amount by TSA Eligibility")
fig_box = px.box(
    df_filtered,
    x="tsaEligible",
    y="repairAmount",
    labels={"tsaEligible": "TSA Eligible (1 yes, 0 no)", "repairAmount": "Repair Amount"},
    title="Repair Amount by TSA Eligibility"
)
st.plotly_chart(fig_box, use_container_width=True)

# bar chart for tsa rate by state
st.subheader("TSA Eligibility Rate by State")
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
    title="TSA Eligibility Rate by State or Territory"
)
st.plotly_chart(fig_state, use_container_width=True)

# text summary
st.markdown(
    """
The histogram shows the distribution of repair amounts.
The boxplot compares repair amounts for people who were TSA eligible.
The bar chart shows how TSA eligibility rates changed across states.
"""
)

st.write("Authors: Aidan Gantt")
