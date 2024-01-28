import streamlit as st
import plotly.express as px
import pandas as pd

def display_map(location_data:pd.DataFrame):

    fig = px.scatter_mapbox(location_data, lat="latitude", lon="longitude", zoom=12, 
                            hover_name='Name', hover_data=['Desc'], center=dict(lat= 32.83, lon= -79.82))

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0),
                  width=1500, 
                  height=1200,
                  )
    return fig


# Setup streamlit page to be wide by default
st.set_page_config(layout='wide')

st.header('Mount Pleasant Projects')

#Grab CSVs
town_projects = pd.read_csv("https://nopian.github.io/govquery/projects.csv",
                            usecols=['Name', 'Group', 'Agenda', 'latitude', 'longitude'])

town_projects = town_projects[town_projects["Group"].str.contains("Old Village Historic District") == False]
town_projects = town_projects[town_projects["Group"].str.contains("Board of Zoning Appeals") == False]
town_projects = town_projects[town_projects["Group"].str.contains("Planning Commission") == False]

town_projects = town_projects.drop(columns=['Group'])
town_projects.columns = ['Name', 'Desc', 'latitude', 'longitude']


mpw_projects = pd.read_csv("https://nopian.github.io/govquery/mpw_projects.csv",
                           usecols=['PROJECT NAME', 'WebsiteDesc', 'latitude', 'longitude'])
mpw_projects.columns = ['Name', 'Desc', 'latitude', 'longitude']


dhec_permits = pd.read_csv("https://nopian.github.io/govquery/dhec_permits.csv",
                           usecols=['siteName', 'siteProfileUrl', 'latitude', 'longitude'])
dhec_permits.columns = ['latitude', 'longitude', 'Name', 'Desc' ]

town_stormwater = pd.read_csv("https://nopian.github.io/govquery/stormwater.csv",
                              usecols=['ProjectName', 'URL', 'latitude', 'longitude'])
town_stormwater.columns = ['Name', 'Desc', 'latitude', 'longitude']


#Choose Data
option = st.selectbox(
    'Choose projects source:',
    ('All', 'Town Projects', 'MPW Projects', 'Town Stormwater', 'DHEC Permits'))

if option == "All":
    
    frames = [town_projects, mpw_projects, dhec_permits, town_stormwater]
    all_frames = pd.concat(frames)
    
    #Display Map
    px_map = display_map(all_frames)

    st.plotly_chart(px_map, use_container_width=True)
    
if option == "Town Projects":
    
    #Display Map
    px_map = display_map(town_projects)

    st.plotly_chart(px_map, use_container_width=True)
    
if option == "MPW Projects":
    
    #Display Map
    px_map = display_map(mpw_projects)

    st.plotly_chart(px_map, use_container_width=True)
    
if option == "Town Stormwater":
    
    #Display Map
    px_map = display_map(town_stormwater)

    st.plotly_chart(px_map, use_container_width=True)
    
if option == "DHEC Permits":
    
    #Display Map
    px_map = display_map(dhec_permits)

    st.plotly_chart(px_map, use_container_width=True)