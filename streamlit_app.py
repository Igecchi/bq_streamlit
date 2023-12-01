import streamlit as st
import pandas as pd
import sqlite3
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
def run_query(query):
    query_job = client.query(query)
    return query_job

query ="""
    select
        date
        , location_key
        , country_name
        , subregion1_name
        , subregion2_name
        , population
        , population_male
        , population_female
        , cumulative_confirmed
        , cumulative_deceased
        , cumulative_recovered
    from `bigquery-public-data.covid19_open_data.covid19_open_data`
"""

# Receive result as a pd.DataFrame.
# query_job = run_query(query)
# df_dataset = query_job.to_dataframe()

# ## Save result as a csv file.
# df_dataset.to_csv('~/Desktop/test_covid19_analysis.csv')

## ------------------ Load Data ------------------ ##
# Read local csv file
df_dataset = pd.read_csv('~/Desktop/test_covid19_analysis.csv')
# Filter dataset by Japan
df_dataset = df_dataset.drop(columns=df_dataset.columns[[0]]) # drop column
df_dataset = df_dataset[(df_dataset['country_name']=='Japan')]
df_dataset = df_dataset.rename({'subregion1_name': 'prefecture_name'}, axis='columns')
prefecture_name_list = df_dataset['prefecture_name'].unique()
column_list = df_dataset.columns.to_list()
# .remove('date') # date is must be used for table

## Fill NaN with 0
df_dataset = df_dataset.fillna(0)
df_dataset_all = df_dataset.copy()

## ------------------ Sidebar ------------------ ##
## --- Input box --- ##
## Input box of prefecture_name
# prefecture_name = st.sidebar.selectbox(
prefecture_name = st.sidebar.multiselect(
    'Prefecutre Name'
    , prefecture_name_list
    , default=['Tokyo']
    )

## Input box of Start day
start_date = pd.to_datetime(st.sidebar.date_input('Start date', datetime(2020, 4, 1)))

## Input box of End day
end_date = pd.to_datetime(st.sidebar.date_input('End date', datetime(2021, 5, 31)))

## --- Check box --- ##
st.sidebar.write('Graph Check Box')
is_graph_active_confirmed = st.sidebar.checkbox('Show Confirmed Graph', value=True)
is_graph_active_deceased = st.sidebar.checkbox('Show Deceased Graph', value=True)
# is_graph_active_recovered = st.sidebar.checkbox('Show Recovered Graph', value=True)
# is_graph_active_pupulation = st.sidebar.checkbox('Show Pupulation Graph', value=True)
is_graph_active_male_pupulation = st.sidebar.checkbox('Show Male Pupulation Graph', value=True)
is_graph_active_female_pupulation = st.sidebar.checkbox('Show Female Pupulation Graph', value=True)

st.sidebar.write('------------------')
st.sidebar.write('Table Column Check Box')
is_table_active = st.sidebar.checkbox('Show Table', value=True)
column_list = st.sidebar.multiselect(
    'Show Table'
    , column_list
    , default=['country_name', 'prefecture_name', 'population', 'population_male', 'population_female', 'cumulative_confirmed', 'cumulative_deceased', 'cumulative_recovered']
    )

## ------------------ Dataset processing ------------------ ##

## Filter dataset by Japan prefecture_name
# df_dataset['population'] = df_dataset['population'].astype('int')
# df_dataset['population_male'] = df_dataset['population_male'].astype('int')
# df_dataset['population_female'] = df_dataset['population_female'].astype('int')
df_dataset['date'] = pd.to_datetime(df_dataset['date'])
df_dataset = df_dataset[(df_dataset['prefecture_name'].isin(prefecture_name)) & (df_dataset['date'] > start_date) & (df_dataset['date'] < end_date)]
df_dataset['date'] = df_dataset['date'].dt.date
# df_dataset = df_dataset[(df_dataset['prefecture_name']==prefecture_name)]
# df_dataset = df_dataset[(df_dataset['date'] > start_date)]
# df_dataset = df_dataset[(df_dataset['date'] < end_date)]

## duplicate dataset 1.for graph, 2.for table
df_dataset_graph = df_dataset.copy()
df_dataset_table = df_dataset.copy()

st.write('Column Name', column_list)
st.write("Some values", df_dataset_graph.head())


## ------------------ Column Layout Setting ------------------ ##
# レスポンシブデザインとUIカスタマイズにカラムを使用する例
column1, column2 = st.columns([1, 1])

## ------------------ Visualization ------------------ ##
st.header('Data Visualization')

num = is_graph_active_confirmed + is_graph_active_deceased + is_graph_active_male_pupulation + is_graph_active_female_pupulation

with column1:
    if is_graph_active_confirmed:
        ## Show result as a graph.
        st.line_chart(df_dataset_graph.groupby(['date']).sum()[['cumulative_confirmed']])
    if is_graph_active_deceased:
        ## Show result as a graph.
        st.line_chart(df_dataset_graph.groupby(['date']).sum()[['cumulative_deceased']])
    # if is_graph_active_recovered:
    #     ## Show result as a graph.
    #     st.line_chart(df_dataset_graph.groupby(['date']).sum()[['cumulative_recovered']])
with column2:
    if is_graph_active_male_pupulation:
        ## Show result as a graph.
        st.line_chart(df_dataset_graph.groupby(['date']).sum()[['population_male']])
    if is_graph_active_female_pupulation:
        ## Show result as a graph.
        st.line_chart(df_dataset_graph.groupby(['date']).sum()[['population_female']])

## Check box what index to show(Table)
if is_table_active:
    ## Show result as a table with scroll bar.
    st.dataframe(df_dataset_table[df_dataset_table['prefecture_name'].isin(prefecture_name)].groupby(['date']).sum()[column_list].T)

## ------------------ SQL Editor ------------------ ##
conn = sqlite3.connect('data.db')
conn.commit()
df_dataset_all.to_sql('my_table', conn, if_exists='replace', index=False)

st.header('SQL Editor')
query = st.text_input('Enter your SQL query (Table Name is my_table):')
if query:
    results = pd.read_sql_query(query, conn)
    st.write(results)
