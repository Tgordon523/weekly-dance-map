import pandas as pd
import numpy as np
import streamlit as st
import pathlib

import leafmap.foliumap as leafmap

# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="Weekly Dance Events",
    layout="wide",
    # initial_sidebar_state="expanded"
)

# Add Title
st.title("Weekly Dance Events")

# Load example data
@st.cache_data
def fetch_data(): 
    df = pd.read_csv(pathlib.Path.cwd()/"dc-triangle.csv")
    df[['latitude', 'longitude']] = df.Lat_long.str.split(",", expand = True)
    df['latitude'] = df['latitude'].astype(dtype=np.float)
    df['longitude'] = df['longitude'].astype(dtype=np.float)
    df["city"] = df["Address"].str.split(",", expand=True)[1]
    df["state"] = df["Address"].str.extractall(r"(\s[A-Z]{2},)").reset_index().drop_duplicates(subset=["level_0"], keep='last').set_index("level_0")[0].str[:3]
    return df


df = fetch_data()

# Setup two filters (will change set-up later)
col1, col2 = st.columns(2)

default_city_selection = df[df.city.isin(st.session_state.city)].city.unique() if "city" in st.session_state else None
default_day_selection = df[df.days.isin(st.session_state.days)].days.unique() if "days" in st.session_state else None

# default_city_selection = df[df.state.isin(st.session_state.get('state', []))].state.unique() 
# default_day_selection = df[df.days.isin(st.session_state.get('days', []))].days.unique()

if 'state' not in st.session_state:
    st.session_state['state'] = default_city_selection
if 'days' not in st.session_state:
    st.session_state['days'] = default_day_selection

# default_city_selection = df[df.city.isin(st.session_state.city)].city.unique() if "city" in st.session_state else None
# default_day_selection = df[df.days.isin(st.session_state.days)].days.unique() if "days" in st.session_state else None

# st.write(default_city_selection, default_day_selection, st.session_state)

city_filter = col1.multiselect(
    label='select cities', 
    options=df.state.unique().tolist(), 
    default=default_city_selection,
    key='state',
    # placeholder="Not available"
    )

day_filter = col2.multiselect(
    label='select days', 
    options=df.days.unique().tolist(), 
    default=default_day_selection,
    key='days'
    # placeholder="Not available"
    )

if city_filter and day_filter:
    city_mask = df['state'].isin(city_filter)
    day_mask = df['days'].isin(day_filter)
    df = df.loc[city_mask & day_mask]
elif city_filter:
    city_mask = df['state'].isin(city_filter)
    df = df.loc[city_mask]
elif day_filter:
    day_mask = df['days'].isin(day_filter)
    df = df.loc[day_mask]


m = leafmap.Map(center=[40, -80], zoom=6, measure_control=False, draw_control=False)
cities = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_cities.csv"
regions = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_regions.geojson"
states = "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json"

m.add_geojson(states, layer_name="US States")
# Cities points 
# m.add_points_from_xy(
#     cities,
#     x="longitude",
#     y="latitude",
#     icon_names=["gear", "map", "leaf", "globe"],
#     spin=True,
#     add_legend=True
# )

m.add_points_from_xy(
    df[["days", "Time", "Title", "Venue", "Address", "Cost", "longitude", "latitude"]],
    x="longitude",
    y="latitude",
    color_column="days",
    add_legend=True
)

# st.cache_resource
m.to_streamlit(height=700)

st.write(df[["days", "Time", "Venue", "Address"]])

st.markdown("---")
st.markdown("Created with Python to consolidate weekly latin dance social events")
# streamlit run test_map.py