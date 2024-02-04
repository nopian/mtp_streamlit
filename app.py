import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

def display_map(location_data:pd.DataFrame):
    
    m = folium.Map(location=[32.83, -79.82], zoom_start=12)

    for index, location_info in location_data.iterrows():
        
        if str(location_info["Desc"]).startswith("http"):
            desc = f'<a href="{location_info["Desc"]}" target="_blank">{location_info["Desc"]}</a>'
        else:
            desc = location_info["Desc"]

        popup = folium.Popup(
            f"""
                  {location_info["Name"]}<br>
                  <br>
                  {desc}<br>
                  """,
            max_width=500,
        )
        folium.Marker([location_info["latitude"], location_info["longitude"]], popup=popup).add_to(m)

    map_data = st_folium(m, width=1500, height=1200, returned_objects=["last_object_clicked"])

st.set_page_config(
    page_title="MT P - Projects",
    layout="wide"
)

st.header('MT P - Projects')

#Grab CSVs
town_projects = pd.read_csv("https://nopian.github.io/govquery/projects.csv",
                            usecols=['Name', 'Group', 'Agenda', 'latitude', 'longitude', 'date'])

town_projects = town_projects[town_projects["Group"].str.contains("Old Village Historic District") == False]
town_projects = town_projects[town_projects["Group"].str.contains("Board of Zoning Appeals") == False]
town_projects = town_projects[town_projects["Group"].str.contains("Planning Commission") == False]

town_projects['date'] = pd.to_datetime(town_projects['date'],format= '%Y-%m-%d')
town_projects = town_projects.drop(columns=['Group'])

town_projects.columns = ['Name', 'Desc', 'latitude', 'longitude', 'date']

####
####
mpw_projects = pd.read_csv("https://nopian.github.io/govquery/mpw_projects.csv",
                           usecols=['PROJECT NAME', 'WebsiteDesc', 'latitude', 'longitude', 'date'])

mpw_projects['date'] = pd.to_datetime(mpw_projects['date'],format= '%Y-%m-%d')
mpw_projects.columns = ['Name', 'Desc', 'latitude', 'longitude', 'date']

####
####
dhec_permits = pd.read_csv("https://nopian.github.io/govquery/dhec_permits.csv",
                           usecols=['siteName', 'siteProfileUrl', 'latitude', 'longitude', 'date'])

dhec_permits['date'] = pd.to_datetime(dhec_permits['date'],format= '%Y-%m-%d')
dhec_permits.columns = ['latitude', 'longitude', 'Name', 'Desc', 'date' ]

####
####
town_stormwater = pd.read_csv("https://nopian.github.io/govquery/stormwater.csv",
                              usecols=['ProjectName', 'URL', 'latitude', 'longitude', 'date'])

town_stormwater['date'] = pd.to_datetime(town_stormwater['date'],format= '%Y-%m-%d')
town_stormwater.columns = ['Name', 'Desc', 'latitude', 'longitude', 'date']

####
####
chs_projects = pd.read_csv("https://nopian.github.io/govquery/chs_newconstruction.csv",
                           usecols=['PERMIT_ADDRESS_LINE1', 'DESCRIPTION', 'latitude', 'longitude', 'date'])

chs_projects['date'] = pd.to_datetime(chs_projects['date'],format= '%Y-%m-%d')
chs_projects.columns = ['Desc', 'Name', 'latitude', 'longitude', 'date']


#Choose Data
option = st.selectbox(
    'Choose projects source:',
    ('All', 'Town Projects', 'MPW Projects', 'Town Stormwater', 'DHEC Permits', 'CHS New Construction'))

frames = [town_projects, mpw_projects, dhec_permits, town_stormwater, chs_projects]
all_frames = pd.concat(frames)

#Search
text_search = st.text_input("Search projects by name", value="")
m1 = all_frames["Name"].str.contains(text_search, na=False, case=False)
m2 = all_frames["Desc"].str.contains(text_search, na=False, case=False)
df_search = all_frames[m1 | m2]
if text_search:
    st.write(df_search)

st.write("Last 7 days")
st.write(all_frames[all_frames.date > pd.Timestamp.now() - pd.to_timedelta("7day")])
    
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
    
if option == "CHS New Construction":
    
    #Display Map
    display_map(chs_projects)
    