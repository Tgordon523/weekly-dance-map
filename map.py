import pandas as pd
import numpy as np
import streamlit as st
import pathlib

import leafmap.foliumap as leafmap

# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="Only Weeklies",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add Title
st.title("Only Weeklies")

# Week Color Palettes
# day_palette = [
#     "#3288bd",
#     "#66c2a5",
#     "#abdda4",
#     "#e6f598",
#     "#fee08b",
#     "#fdae61",
#     "#f46d43",
#     # '#d53e4f'
# ]

day_palette = [
    "darkred",
    "red",
    "orange",
    "green",
    "darkgreen",
    "blue",
    "darkblue",
    #    '#d53e4f'
]

day_palette_dict = {
    "Monday":"darkred",
    "Tuesday":"red",
    "Wednesday":"orange",
    "Thursday":"green",
    "Friday":"darkgreen",
    "Saturday":"blue",
    "Sunday":"darkblue",
    #    '#d53e4f'
}


# Load example data
@st.cache_data
def fetch_data():
    p = pathlib.Path.cwd() / "data" / "full_output.csv"
    df = pd.read_csv(p)
    # df = pd.read_clipboard()
    # df[["latitude", "longitude"]] = df.Lat_long.str.split(",", expand=True)
    # df["latitude"] = df["latitude"].astype(float)
    # df["longitude"] = df["longitude"].astype(float)
    # df["city"] = df["Address"].str.split(",", expand=True)[1]
    df["state"] = (
        df["Address"]
        .str.extractall(r"(\s[A-Z]{2},)")
        .reset_index()
        .drop_duplicates(subset=["level_0"], keep="last")
        .set_index("level_0")[0]
        .str[:3]
    )
    df.sort_values(by="weekday", inplace=True)
    return df


df = fetch_data()
st.dataframe(df)
# df.sort_values(by="", inplace=True)
# Setup two filters (will change set-up later)
col1, col2 = st.columns(2)

default_city_selection = (
    df[df.City.isin(st.session_state.City)].City.unique()
    if "City" in st.session_state
    else None
)
city_filter = col1.multiselect(
    label="select cities",
    options=df.City.unique(),
    default=default_city_selection,
    key="City",
)



if city_filter:
    # print(df.day.nunique())
    city_mask = df["City"].isin(city_filter)
    df = df.loc[city_mask]
    t = df.days.unique()
    subdict = {x: day_palette_dict[x] for x in t if x in day_palette_dict}
    new_colors = [k for k in subdict.values()]
    st.write(day_palette_dict, new_colors)
    day_palette = new_colors
    # st.write(day_palette)

# st.dataframe(df)
m = leafmap.Map(center=(36, -80),zoom=4, measure_control=False, draw_control=False)
# cities = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_cities.csv"
# regions = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_regions.geojson"
states = "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json"

# m.add_geojson(states, layer_name="US States")
# Cities points
df.sort_values(by="weekday", inplace=True)
m.add_points_from_xy(
    df[["days", "Time", "Title", "Venue", "Address", "Cost", "Longitude", "Latitude"]],
    x="Longitude",
    y="Latitude",
    color_column="days",
    prefix='glyphicon',
    marker_colors=day_palette,
    add_legend=True,
)

# st.cache_resource
m.to_streamlit(height=700)

col1_bar, col2_bar = st.columns(2)
st.write()

col1_bar.bar_chart(df.days.value_counts().reset_index().sort_values(by="days"), x="days", y='count', x_label="Events per Day", horizontal=True)
col2_bar.bar_chart(df.City.value_counts().reset_index().sort_values(by="City"), x="days", y='count', x_label="Events per Day", horizontal=True)
# st.write(df.groupby("Venue")["Title"].count())

st.write(
    (df.groupby("Venue")["Title"].count().reset_index()).merge(
        (df.groupby("Venue")["days"].apply(lambda x: "%s" % ", ".join(x)).reset_index())
    )
)

# st.write(df.groupby("Venue")["days"].apply(lambda x: "%s" % ", ".join(x)))

st.write(df[["days", "Time", "Venue", "Address"]])

st.markdown("---")
st.markdown("Created with Python to consolidate weekly latin dance social events")
# streamlit run test_map.py
