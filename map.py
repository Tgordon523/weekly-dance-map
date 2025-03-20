import pandas as pd
import numpy as np
import streamlit as st
import pathlib

import plotly.express as px
import leafmap.foliumap as leafmap

# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="Only Weeklies", layout="wide", initial_sidebar_state="expanded"
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
    "Monday": "#3288bd",
    "Tuesday": "#66c2a5",
    "Wednesday": "#abdda4",
    "Thursday": "#e6f598",
    "Friday": "#fee08b",
    "Saturday": "#fdae61",
    "Sunday": "#f46d43",
    "Multiple": "#d53e4f",
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
df["size"] = 40

# col1, _, _ = st.columns(3)
with st.sidebar:
    default_city_selection = (
        df[df.City.isin(st.session_state.City)].City.unique()
        if "City" in st.session_state
        else None
    )
    city_filter = st.multiselect(
        label="select cities",
        options=df.City.unique(),
        default=default_city_selection,
        key="City",
    )


    if city_filter:
        # print(df.day.nunique())
        city_mask = df["City"].isin(city_filter)
        df = df.loc[city_mask]
    # t = df.days.unique()
    # subdict = {x: day_palette_dict[x] for x in t if x in day_palette_dict}
    # new_colors = [k for k in subdict.values()]
    # st.write(day_palette_dict, new_colors)
    # day_palette = new_colors
    # st.write(day_palette)

# st.dataframe(df)
# m = leafmap.Map(center=(36, -80),zoom=4, measure_control=False, draw_control=False)
# cities = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_cities.csv"
# regions = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_regions.geojson"
states = "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json"

# m.add_geojson(states, layer_name="US States")
# Cities points
grouped_days_df = (
    (df.groupby("Venue")["Title"].count().reset_index())
    .merge(
        (df.groupby("Venue")["days"].apply(lambda x: "%s" % ", ".join(x)).reset_index())
    )
    .merge(
        (df.groupby("Venue")["Time"].apply(lambda x: "%s" % ", ".join(x)).reset_index())
    )
)

grouped_days_df_complete = grouped_days_df.merge(
    df[["Venue", "City", "Latitude", "Longitude", "size", "weekday"]], on="Venue", how="left"
).drop_duplicates(subset="Venue")

grouped_days_df_complete["Marker"] = np.where(
    grouped_days_df_complete.Title > 1, "Multiple", grouped_days_df_complete.days
)
grouped_days_df_complete["weekday"] = np.where(
    grouped_days_df_complete.Title > 1, 8, grouped_days_df_complete.weekday
)
grouped_days_df_complete.sort_values(by="weekday", inplace=True)
# st.dataframe(grouped_days_df_complete)

df.sort_values(by="weekday", inplace=True)
grouped_days_df_complete["color"] = grouped_days_df_complete["Marker"].map(
    day_palette_dict
)

fig = px.scatter_map(
    grouped_days_df_complete,
    lat="Latitude",
    lon="Longitude",
    color="Marker",
    size="size",
    labels={"City": "City", "Address": "Address"},
    size_max=40,
    hover_name="Venue",
    color_discrete_sequence=px.colors.qualitative.G10,
    # color_continuous_scale=["green", "blue"],
    # hover_data={'value': True, 'day': True, 'lat': False, 'lon': False},
    zoom=4.5,
    title="North America Weeklies",
)
fig.update_traces(cluster=dict(enabled=True))

fig.update_layout(
    legend=dict(
        x=0,
        y=1,
        # traceorder="reversed",
        # title_font_family="Times New Roman",
        font=dict(family="Courier", size=12, color="black"),
        bgcolor="LightSteelBlue",
        bordercolor="Black",
        borderwidth=2,
    )
)
fig.update_geos(fitbounds="locations")
fig.update_layout(map_style="open-street-map")
fig.update_layout(height=700, margin={"r": 0, "t": 0, "l": 0, "b": 0})

st.plotly_chart(fig, height=700)
st.text("")
st.text("")
st.text("")
# st.plotly_chart(fig)
# st.plotly_chart(fig,height=1200, zoom=5)
# m.to_streamlit(height=700)
# st.write(df.columns)
col1_bar, col2_bar = st.columns(2)

col1_bar.bar_chart(
    df.days.value_counts().reset_index().sort_values(by="days"),
    x="days",
    y="count",
    x_label="Events per Day",
    horizontal=True,
)
col2_bar.bar_chart(
    df.City.value_counts().reset_index().sort_values(by="City"),
    x="City",
    y="count",
    x_label="Events per Day",
    horizontal=True,
)

st.write(df[["days", "Time", "Venue", "Address"]])

st.markdown("---")
st.markdown("Created with Python to consolidate weekly latin dance social events")
# streamlit run test_map.py
