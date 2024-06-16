import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Set the layout to wide
st.set_page_config(layout="wide")

# Load the JSON data from a URL
@st.cache_data
def load_data():
    url = 'https://nopian.github.io/crime/combined_crime_data.json'
    response = requests.get(url)
    data = response.json()
    return data

data = load_data()

# Create a pandas DataFrame from the JSON data
df = pd.DataFrame(data)

# Convert the 'InfoBoxString' to extract 'Case #', 'Date', and 'Location'
def extract_info(box_string, label):
    prefix = f"<bold>{label}</bold>"
    start = box_string.find(prefix) + len(prefix)
    end = box_string.find('<br>', start)
    return box_string[start:end].strip()

df['Case #'] = df['InfoBoxString'].apply(lambda x: extract_info(x, 'Case # '))
df['Date'] = df['InfoBoxString'].apply(lambda x: extract_info(x, 'Date:'))
df['Location'] = df['InfoBoxString'].apply(lambda x: extract_info(x, 'Location:'))

# Correct the misspelling of "Longitute" to "Longitude"
df.rename(columns={"Longitute": "Longitude"}, inplace=True)

# Convert the 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y %I:%M:%S %p')

# Set the 'Date' column as the index
df.set_index('Date', inplace=True)

# Resample the data to monthly intervals and count the number of occurrences in each 'Group'
group_counts = df.groupby([pd.Grouper(freq='M'), 'Group']).size().unstack(fill_value=0)

# Streamlit app
st.title("Crime Analysis Overview")
st.write("""
This app provides an interactive overview of crime data with various visualizations.
""")

# Monthly Overview of Crime Counts
st.subheader("Monthly Overview of Crime Counts")
group_counts = group_counts.reset_index().melt(id_vars='Date', var_name='Group', value_name='Count')

fig = px.bar(group_counts, x='Date', y='Count', color='Group', barmode='stack', 
             labels={'Date': 'Month', 'Count': 'Crime Count'}, title='Crime Count by Group Over Time',
             width=1400, height=700)
fig.update_layout(xaxis={'categoryorder':'category ascending'})

st.plotly_chart(fig, use_container_width=True)

# Crime Trends Over Time
st.subheader("Crime Trends Over Time")
fig_trend = px.line(group_counts, x='Date', y='Count', color='Group', 
                    labels={'Date': 'Month', 'Count': 'Crime Count'}, title='Crime Trends by Group Over Time')
st.plotly_chart(fig_trend, use_container_width=True)

# Reset index to include 'Date' column for the map plot
df = df.reset_index()

# Map of Crime Locations
st.subheader("Map of Crime Locations")
fig_map = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", color="Group", hover_name="Title", hover_data=["Case #", "Location", "Date"],
                            color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
fig_map.update_layout(mapbox_style="open-street-map")
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig_map, use_container_width=True)

# Crime Heatmap
st.subheader("Crime Heatmap")
fig_heatmap = px.density_mapbox(df, lat='Latitude', lon='Longitude', z=None, radius=10, 
                                hover_name="Title", hover_data=["Case #", "Location", "Date"], 
                                mapbox_style="open-street-map", zoom=10)
fig_heatmap.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig_heatmap, use_container_width=True)

# Crime Distribution by Day of Week
df['DayOfWeek'] = df['Date'].dt.day_name()
day_of_week_counts = df.groupby(['DayOfWeek', 'Group']).size().unstack(fill_value=0)

st.subheader("Crime Distribution by Day of Week")
fig_dow = px.bar(day_of_week_counts.reset_index().melt(id_vars='DayOfWeek', var_name='Group', value_name='Count'), 
                 x='DayOfWeek', y='Count', color='Group', barmode='stack',
                 labels={'DayOfWeek': 'Day of Week', 'Count': 'Crime Count'}, title='Crime Distribution by Day of Week')
st.plotly_chart(fig_dow, use_container_width=True)

# Crime Distribution by Hour
df['Hour'] = df['Date'].dt.hour
hour_counts = df.groupby(['Hour', 'Group']).size().unstack(fill_value=0)

st.subheader("Crime Distribution by Hour")
fig_hour = px.bar(hour_counts.reset_index().melt(id_vars='Hour', var_name='Group', value_name='Count'), 
                  x='Hour', y='Count', color='Group', barmode='stack',
                  labels={'Hour': 'Hour of Day', 'Count': 'Crime Count'}, title='Crime Distribution by Hour')
st.plotly_chart(fig_hour, use_container_width=True)

# Top Crime Locations
top_locations = df['Location'].value_counts().head(10).reset_index()
top_locations.columns = ['Location', 'Count']

# Join top locations with original dataframe to get lat/lon
top_locations_df = top_locations.merge(df[['Location', 'Latitude', 'Longitude']].drop_duplicates(), on='Location')

st.subheader("Top 10 Crime Locations")
fig_top_loc = px.scatter_mapbox(top_locations_df, lat="Latitude", lon="Longitude", size="Count", hover_name="Location", 
                                color="Count", color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
fig_top_loc.update_layout(mapbox_style="open-street-map")
fig_top_loc.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig_top_loc, use_container_width=True)

# Crime Type Summary
st.subheader("Crime Type Summary")
crime_summary = df['Group'].value_counts().reset_index()
crime_summary.columns = ['Crime Type', 'Count']
st.write(crime_summary)

# Data Editor
st.subheader("View Data")
edited_df = st.data_editor(df,hide_index=True, disabled=True, width=1800)


# Option to download data
st.download_button(
    label="Download Data as CSV",
    data=group_counts.to_csv(index=False).encode('utf-8'),
    file_name='monthly_crime_data.csv',
    mime='text/csv',
)