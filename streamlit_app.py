import streamlit as st
import pandas as pd
import sqlite3
from google.oauth2 import service_account
from google.cloud import bigquery
from datetime import datetime
from streamlit_elements import elements, dashboard, mui, nivo
from streamlit_elements import dashboard

st.set_page_config(
    page_title="streamlit_app",
    layout="wide"
)

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
df = pd.read_csv('~/Desktop/test_covid19_analysis_japan.csv')
df_dataset = df.reset_index(drop=True)

# Filter dataset by Japan
df_dataset = df_dataset.drop(columns=df_dataset.columns[[0]]) # drop column
df_dataset = df_dataset[(df_dataset['country_name']=='Japan')]
df_dataset = df_dataset.rename({'subregion1_name': 'prefecture_name'}, axis='columns')
prefecture_name_list = df_dataset['prefecture_name'].unique()
column_list = df_dataset.columns.to_list()

## Fill NaN with 0
df_dataset = df_dataset.fillna(0)
df_dataset_all = df_dataset.copy()

## ------------------ Sidebar ------------------ ##
## --- Input box --- ##
## Input box of prefecture_name
prefecture_name = st.sidebar.multiselect(
    'Prefecutre Name'
    , prefecture_name_list
    , default=['Tokyo']
    )

## Input box of Start day
start_date = pd.to_datetime(st.sidebar.date_input('Start date', datetime(2020, 3, 1)))

## Input box of End day
end_date = pd.to_datetime(st.sidebar.date_input('End date', datetime(2021, 12, 31)))

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
df_dataset['date'] = pd.to_datetime(df_dataset['date'])
df_dataset = df_dataset[(df_dataset['date'].dt.day == 1)]
df_dataset = df_dataset[(df_dataset['prefecture_name'].isin(prefecture_name)) & (df_dataset['date'] >= start_date) & (df_dataset['date'] <= end_date)]
df_dataset['date'] = df_dataset['date'].astype(str)

## duplicate dataset 1.for graph, 2.for table
df_dataset_graph = df_dataset.copy()
df_dataset_table = df_dataset.copy()

## If you want to show column list and part of Dataframe, you can use this code.
# st.write('Column Name', column_list)
# st.write("Part of Dataframe", df_dataset_graph.head())



## ------------------ Data Visualization ------------------ ##
st.header('Data Visualization')

### ------------------ Graph Visualization setting ------------------ ###
tmp = df_dataset_graph.groupby(['date']).sum()[['cumulative_confirmed']]
tmp['date'] = tmp.index
tmp = tmp.rename(columns={'date': 'x', 'cumulative_confirmed': 'y'})[['x', 'y']].to_json(orient='records')
tmp_data = [
        {
            "id": prefecture_name,
            "data": eval(tmp)
        }
    ]

## If you want to show detail data, you can use this code.
# st.write(tmp_data)

def create_data(y_data):
    tmp = df_dataset_graph.groupby(['date']).sum()[[y_data]]
    tmp['date'] = tmp.index
    tmp = tmp.rename(columns={'date': 'x', y_data: 'y'})[['x', 'y']].to_json(orient='records')
    return [
                {
                    "id": "+".join(prefecture_name),
                    "data": eval(tmp)
                }
            ]

def create_chart(KEYNAME, CARD_TITLE, INPUT_DATA):
    with mui.Card(key=KEYNAME, sx={"display": "flex", "flexDirection": "column"}):
                mui.CardHeader(title=CARD_TITLE, className="draggable")
                with mui.CardContent(sx={"flex": 1, "minHeight": 0}):
                    nivo.Line(
                        data=INPUT_DATA,
                        margin={ 'top': 10, 'right': 80, 'bottom': 90, 'left': 80 },
                        xScale={
                            'type': 'point',
                            'min': 'auto',
                            'max': 'auto',
                            'stacked': False,
                            'reverse': False
                        },
                        yScale={
                            'type': 'linear',
                            'min': 'auto',
                            'max': 'auto',
                            'stacked': True,
                            'reverse': False
                        },
                        yFormat=" >-,.2~d",
                        axisTop=None,
                        axisRight=None,
                        axisBottom={
                            'tickSize': 1,
                            'tickPadding': 1,
                            'tickRotation': -70,
                            'legend': '日付',
                            'legendOffset': 80,
                            'legendPosition': 'middle'
                        },
                        axisLeft={
                            'tickSize': 3,
                            'tickPadding': 3,
                            'tickRotation': 0,
                            'legend': 'count',
                            'legendOffset': -60,
                            'legendPosition': 'middle'
                        },
                        enableGridX=False,
                        enableGridY=False,
                        enablePoints=False,
                        pointSize=2,
                        pointColor={ 'theme': 'background' },
                        pointBorderWidth=1,
                        pointBorderColor={ 'from': 'serieColor' },
                        pointLabelYOffset=-7,
                        useMesh=True,
                        # -- 凡例の設定 -- #
                        legends=[
                            {
                                'anchor': 'top-left',
                                'direction': 'column',
                                'justify': False,
                                'translateX': 15,
                                'translateY': 0,
                                'itemsSpacing': 0,
                                'itemDirection': 'left-to-right',
                                'itemWidth': 80,
                                'itemHeight': 10,
                                'itemOpacity': 0.75,
                                'symbolSize': 7,
                                'symbolShape': 'circle',
                                'symbolBorderColor': 'rgba(0, 0, 0, .5)',
                                'effects': [
                                    {
                                        'on': 'hover',
                                        'style': {
                                            'itemBackground': 'rgba(0, 0, 0, .03)',
                                            'itemOpacity': 1
                                        }
                                    }
                                ]
                            }
                        ]
                    )

### ------------------ Graph Visualization ------------------ ###
with elements("dashboard"):
    # First, build a default layout for every element you want to include in your dashboard

    layout = [
        # Parameters: element_identifier, x_pos, y_pos, width, height, [item properties...]
        # for Chart
        dashboard.Item("confirmed_chart", 0, 0, 6, 3.5),
        dashboard.Item("deceased_chart", 6, 0, 6, 3.5),
        dashboard.Item("male_pupulation_chart", 0, 0, 6, 3.5),
        dashboard.Item("female_pupulation_chart", 6, 0, 6, 3.5),
    ]

    with dashboard.Grid(layout, draggableHandle=".draggable"):
        if is_graph_active_confirmed:
            dataset_graph_confirmed = create_data(y_data='cumulative_confirmed')
            create_chart(KEYNAME="confirmed_chart", CARD_TITLE="Confirmed Chart", INPUT_DATA=dataset_graph_confirmed)

        if is_graph_active_deceased:
            dataset_graph_deceased = create_data(y_data='cumulative_deceased')
            create_chart(KEYNAME="deceased_chart", CARD_TITLE="Deceased Chart", INPUT_DATA=dataset_graph_deceased)


        if is_graph_active_male_pupulation:
            dataset_graph_population_male = create_data(y_data='population_male')
            create_chart(KEYNAME="male_pupulation_chart", CARD_TITLE="Male Pupulation Chart", INPUT_DATA=dataset_graph_population_male)

        if is_graph_active_female_pupulation:
            dataset_graph_population_female = create_data(y_data='population_female')
            create_chart(KEYNAME="female_pupulation_chart", CARD_TITLE="Female Pupulation Chart", INPUT_DATA=dataset_graph_population_female)


### ------------------ Table Visualization ------------------ ###
## Check box what index to show(Table)
if is_table_active:
    ## Show result as a table with scroll bar.
    st.dataframe(df_dataset_table[df_dataset_table['prefecture_name'].isin(prefecture_name)].groupby(['date']).sum()[column_list].T)


## ------------------ SQL Editor ------------------ ##
conn = sqlite3.connect('data.db')
conn.commit()
df_dataset_table.to_sql('my_table', conn, if_exists='replace', index=False)

sql_editor_md = """
## SQL Editor
You can use SQL Editor.

Sample Query:
```sql
select * from my_table;
```
### ↓Enter your SQL query below
"""
st.markdown(sql_editor_md)
query = st.text_input('※Table Name is `my_table`')
if query:
    results = pd.read_sql_query(query, conn)
    st.write(results)
