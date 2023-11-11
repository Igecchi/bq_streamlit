import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from google.oauth2 import service_account
from google.cloud import bigquery
from datetime import time, datetime

st.title('Connect Streamlit to Google Bigquery')

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=6000)
def run_query(query):
    query_job = client.query(query)
    rows_raw = query_job.result()
    # Convert to list of dicts. Required for st.cache_data to hash the return value.
    rows = [dict(row) for row in rows_raw]
    return rows

query ="""
    SELECT word
    FROM `bigquery-public-data.samples.shakespeare`
    LIMIT 10
"""

# rows = run_query(query)

# # Print results.
# st.write("Some wise words from Shakespeare:")
# for row in rows:
#     st.write("✍️ " + row['word'])
# st.balloons()

st.header("Test st.slider()")

# ex.1
st.subheader("Slider")

age = st.slider("How old are you?", 0, 130, 33)
st.write("I'm ", age, "years old")

# ex.2
st.subheader("Range Slider")

values = st.slider(
    "select a range of values",
    0.0, 100.0, (25.0, 75.0)
    )
st.write("Valus:", values)

# ex.3
st.subheader("Range time slider")

appointment = st.slider(
    "Schedule your appointment:",
    value = (time(11, 30), time(12, 45))
    )
st.write("You're schedule for:", appointment)

# ex.4
st.subheader("Datetime slider")

start_time = st.slider(
    "When do you start?",
    value = datetime(2020, 1, 1, 9, 30),
    format = "YYYY/MM/DD - hh:mm"
    # format = "MM/DD/YY - hh:mm"
    )
st.write("Start time:", start_time)
