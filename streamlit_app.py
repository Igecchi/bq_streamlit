import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from google.oauth2 import service_account
from google.cloud import bigquery
from datetime import time, datetime

st.title('Test Streamlit')

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

st.header("Test Line Chart")

chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c']
    )

st.table(chart_data)

st.write(chart_data, chart_data.head(), chart_data.tail())
st.line_chart(chart_data)
