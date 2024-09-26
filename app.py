import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium, folium_static

def display_map(location_data:pd.DataFrame):
    
    m = folium.Map(location=[32.83, -79.82], zoom_start=12)

    for index, location_info in location_data.iterrows():
        
        if str(location_info["Desc"]).startswith("http"):
            desc = f'<a href="{location_info["Desc"]}" target="_blank">{location_info["Desc"]}</a>'
        else:
            desc = location_info["Desc"]
            
        if location_info["source"] == "Town Projects":
            color = 'red'
        elif location_info["source"] == "MPW Projects":
            color = 'blue'
        elif location_info["source"] == "DHEC Permits":
            color = 'green'
        elif location_info["source"] == "Town Stormwater":
            color = 'orange'
        elif location_info["source"] == "CHS Permits":
            color = 'black'

        popup = folium.Popup(
            f"""
                  Name: {location_info["Name"]}<br>
                  <br>
                  Description: {desc}<br>
                  <br>
                  Source: {location_info["source"]}<br>
                  """,
            max_width=500,
        )
        folium.Marker([location_info["latitude"], location_info["longitude"]], popup=popup, icon=folium.Icon(color=color)).add_to(m)

    map_data = folium_static(m, width=1800, height=1200)

st.set_page_config(
    page_title="MT P - Projects",
    layout="wide"
)

st.title('MT P - Projects')

#Grab CSVs
town_projects = pd.read_csv("https://nopian.github.io/govquery/projects.csv",
                            usecols=['Name', 'Group', 'Agenda', 'latitude', 'longitude', 'date'])

town_projects = town_projects[town_projects["Group"].str.contains("Old Village Historic District") == False]
town_projects = town_projects[town_projects["Group"].str.contains("Board of Zoning Appeals") == False]
town_projects = town_projects[town_projects["Group"].str.contains("Planning Commission") == False]

town_projects['date'] = pd.to_datetime(town_projects['date'],format= '%Y-%m-%d')
town_projects = town_projects.drop(columns=['Group'])
town_projects['source'] = "Town Projects"

town_projects.columns = ['Name', 'Desc', 'latitude', 'longitude', 'date', 'source']

####
####
mpw_projects = pd.read_csv("https://nopian.github.io/govquery/mpw_projects.csv",
                           usecols=['PROJECT NAME', 'WebsiteDesc', 'latitude', 'longitude', 'date'])

mpw_projects['date'] = pd.to_datetime(mpw_projects['date'],format= '%Y-%m-%d')
mpw_projects['source'] = "MPW Projects"
mpw_projects.columns = ['Name', 'Desc', 'latitude', 'longitude', 'date', 'source']

####
####
dhec_permits = pd.read_csv("https://nopian.github.io/govquery/dhec_permits.csv",
                           usecols=['siteName', 'siteProfileUrl', 'latitude', 'longitude', 'date'])

dhec_permits['date'] = pd.to_datetime(dhec_permits['date'],format= '%Y-%m-%d')
dhec_permits['source'] = "DHEC Permits"
dhec_permits.columns = ['latitude', 'longitude', 'Name', 'Desc', 'date', 'source']

####
####
town_stormwater = pd.read_csv("https://nopian.github.io/govquery/stormwater.csv",
                              usecols=['ProjectName', 'date', 'URL', 'latitude', 'longitude' ])

town_stormwater['date'] = pd.to_datetime(town_stormwater['date'],format= '%Y-%m-%d')
town_stormwater['source'] = "Town Stormwater"
town_stormwater.columns = ['Name', 'date', 'Desc', 'latitude', 'longitude', 'source']

####
####
chs_projects = pd.read_csv("https://nopian.github.io/govquery/chs_newconstruction.csv",
                           usecols=['PERMIT_ADDRESS_LINE1', 'DESCRIPTION', 'latitude', 'longitude', 'date'])

chs_projects['date'] = pd.to_datetime(chs_projects['date'],format= '%Y-%m-%d')
chs_projects['source'] = "CHS Permits"
chs_projects.columns = ['Desc', 'Name', 'latitude', 'longitude', 'date', 'source']


tab1, tab2, tab3 = st.tabs(["Map", "Last 30 Days", "Search"])

with tab1:
    st.subheader("All Projects")
    #Choose Data
    option = st.selectbox(
        'Choose projects sources:',
        ('All', 'Town Projects', 'MPW Projects', 'Town Stormwater', 'DHEC Permits', 'CHS Permits'))

    frames = [town_projects, mpw_projects, dhec_permits, town_stormwater, chs_projects]
    all_frames = pd.concat(frames)

    if option == "All":
        #Display Map
        display_map(all_frames)

    if option == "Town Projects":
        
        #Display Map
        display_map(town_projects)
        
    if option == "MPW Projects":
        
        #Display Map
        display_map(mpw_projects)
        
    if option == "Town Stormwater":
        
        #Display Map
        display_map(town_stormwater)
        
    if option == "DHEC Permits":
        
        #Display Map
        display_map(dhec_permits)
        
    if option == "CHS Permits":
        
        #Display Map
        display_map(chs_projects)

with tab3:
    st.subheader("Search Projects")
    query = st.text_input("Search:")
    if query:
        mask = all_frames.applymap(lambda x: query in str(x).lower()).any(axis=1)
        search_df = all_frames[mask]
        
        st.table(search_df) 
    
    
with tab2:
    st.subheader("New Projects")
    new_projects = all_frames[all_frames.date > pd.Timestamp.now() - pd.to_timedelta("30day")]
    st.table(new_projects)
    
    st.subheader("Map")
    display_map(new_projects)
    

    