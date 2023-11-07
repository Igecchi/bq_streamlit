import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from google.oauth2 import service_account
from google.cloud import bigquery

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

st.header("Test st.write()")

# ex.1
st.write('Hello, *World!* :sunglasses:')

# ex.2
st.write(1234)

# ex.3
st.write('1 + 1 = ', 2)

# ex.4
df = pd.DataFrame({
    'first column':  [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
    })
st.write(df)

# ex.5
st.write('Below is a Dataframe:', df, 'Above is a Dataframe')

# ex.6
df2 = pd.DataFrame(
    np.random.randn(20, 3)
    , columns=['a', 'b', 'c'])
c = alt.Chart(df2).mark_circle().encode(
    x='a', y='b', size='c', color='c', tooltip=['a', 'b', 'c'])
st.write(df2)
st.write(c)
