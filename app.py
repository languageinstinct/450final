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

# histogram section with log scale
st.subheader("Repair amount distribution")

fig_hist = px.histogram(
    df_filtered,
    x="repairAmount",
    nbins=60,
    height=400,
    title="Distribution of repair amount (log scale)"
)

fig_hist.update_xaxes(type="log")

col1, col2 = st.columns([3, 1])
with col1:
    st.plotly_chart(fig_hist, use_container_width=True)

# boxplot section
st.subheader("Repair amount by TSA eligibility")

fig_box = px.box(
    df_filtered,
    x="tsaEligible",
    y="repairAmount",
    height=430,
    labels={"tsaEligible": "TSA eligible (1 yes, 0 no)", "repairAmount": "Repair amount"},
    title="Repair amount by TSA eligibility"
)

col3, col4 = st.columns([3, 1])
with col3:
    st.plotly_chart(fig_box, use_container_width=True)

# bar chart section
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
    height=450,
    title="TSA eligibility rate by state or territory"
)

col5, col6 = st.columns([3, 1])
with col5:
    st.plotly_chart(fig_state, use_container_width=True)

# text summary
st.markdown(
    """
the histogram uses a log scale on repair amount so the skewed distribution is easier to see.  
the boxplot compares repair amounts for people who were tsa eligible versus not eligible.  
the bar chart shows how tsa eligibility rates change across states in the sample.  
"""
)

st.write("Authors: Aidan Gantt")
