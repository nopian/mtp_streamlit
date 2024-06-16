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
st.title("Monthly Crime Analysis Overview")
st.write("""
This app provides an interactive monthly overview of crime data.
""")

# Monthly Overview of Crime Counts
st.subheader("Monthly Overview of Crime Counts")
group_counts = group_counts.reset_index().melt(id_vars='Date', var_name='Group', value_name='Count')

fig = px.bar(group_counts, x='Date', y='Count', color='Group', barmode='stack', 
             labels={'Date': 'Month', 'Count': 'Crime Count'}, title='Crime Count by Group Over Time',
             width=1400, height=700)  # Set the width and height
fig.update_layout(xaxis={'categoryorder':'category ascending'})

st.plotly_chart(fig, use_container_width=True)  # Use container width for the chart

# Reset index to include 'Date' column for the map plot
df = df.reset_index()

# Map of Crime Locations
st.subheader("Map of Crime Locations")
fig_map = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", color="Group", hover_name="Title", hover_data=["Case #", "Location", "Date"],
                            color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
fig_map.update_layout(mapbox_style="open-street-map")
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig_map, use_container_width=True)  # Use container width for the map

# Show data as table
st.subheader("Data Table")
st.dataframe(group_counts)

# Option to download data
st.download_button(
    label="Download Data as CSV",
    data=group_counts.to_csv(index=False).encode('utf-8'),
    file_name='monthly_crime_data.csv',
    mime='text/csv',
)
