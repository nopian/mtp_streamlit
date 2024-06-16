import pandas as pd
import streamlit as st
import plotly.express as px

# Set the layout to wide
st.set_page_config(layout="wide")

# Load the CSV data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y %I:%M:%S %p')
    return df

# Load the combined data
data_url = 'https://nopian.github.io/crime/combined_crime_data.csv'
df = load_data(data_url)

# Streamlit app
st.title("Crime Analysis Overview")
st.write("""
This app provides an interactive overview of crime data with various visualizations.
""")

# Monthly Overview of Crime Counts
st.subheader("Monthly Overview of Crime Counts")
group_counts = df.groupby([pd.Grouper(key='Date', freq='M'), 'Group']).size().unstack(fill_value=0)
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

# Map of Crime Locations
st.subheader("Map of Crime Locations")
fig_map = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", color="Group", hover_name="Group", hover_data=["CaseNumber", "Location", "Date"],
                            color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
fig_map.update_layout(mapbox_style="open-street-map")
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig_map, use_container_width=True)

# Crime Heatmap
st.subheader("Crime Heatmap")
fig_heatmap = px.density_mapbox(df, lat='Latitude', lon='Longitude', z=None, radius=10, 
                                hover_name="Group", hover_data=["CaseNumber", "Location", "Date"], 
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

# Show data as table
st.subheader("Data Table")
st.dataframe(group_counts)

st.subheader("View Data")
edited_df = st.dataframe(df)

# Option to download data
st.download_button(
    label="Download Data as CSV",
    data=group_counts.to_csv(index=False).encode('utf-8'),
    file_name='monthly_crime_data.csv',
    mime='text/csv',
)
