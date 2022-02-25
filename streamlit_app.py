import streamlit as st
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import time
import shapestats_kc as shp
from sgqlc.endpoint.http import HTTPEndpoint
import datetime
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta
import numpy as np



#Create a list of the months of data that SafeGraph has.
#SafeGraph's dataset goes back to Jan 2018
strt_dt = datetime.date(2018,1,1)
#Going up until the last month, or today minus one month
end_dt = datetime.datetime.today() - relativedelta(months=1)
#Make list of dates
dates = [dt for dt in rrule(MONTHLY, dtstart=strt_dt, until=end_dt)]



st.set_page_config(page_title="HR&A SafeGraph Analysis Template", page_icon="📈", layout="centered")

if "counter" not in st.session_state:
    st.session_state.counter = 1



hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            
            header {visibility: hidden;}
            
            
            div[data-testid="stVerticalBlock"]{gap: 0em !important;}
            </style>
            """
            #footer {visibility: hidden;}
            #button[data-testid] {visibility: hidden;}
            #div > div > iframe{display: none;}
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


url = 'https://api.safegraph.com/v2/graphql'
headers = {'apikey': st.secrets["SG_KEY"]}

endpoint = HTTPEndpoint(url, headers)



def scroll():
    st.session_state.counter += 1
    components.html(
        f"""
        <p>{st.session_state.counter}</p>
        <script>
        window.parent.document.querySelector('.css-1outpf7').scrollTo({{top: window.parent.document.querySelector('.css-1outpf7').scrollHeight, behavior: 'smooth'}});
        </script>
        """,
        height=0
        )

def query_radius(i,lat,lng,distance):
    records_per_call = 20
    cursor = ""
    nextPage = True
    dfs = pd.DataFrame()
    st.sidebar.write("Querying radius around polygon #",i)
    while nextPage == True:
        query = f"""
                    query radius {{
                      search(
                        filter: {{
                          by_radius: {{
                            latitude: {lat}
                            longitude: {lng}
                            distanceInMeters: {distance}
                          }}
                        }}
                      ) {{
                        places {{
                          results(first: {records_per_call}, after: "{cursor}") {{
                          pageInfo {{
                              endCursor
                              hasNextPage
                            }}
                            edges {{
                              node {{
                                placekey
                                safegraph_core {{
                                  naics_code
                                  latitude
                                  longitude
                                }}
                              }}
                            }}
                          }}
                        }}
                      }}
                    }}
                """
        res = endpoint(query)
        edges = res['data']['search']['places']['results']['edges']
        x = pd.DataFrame()
        for edge in edges:
            df = pd.DataFrame.from_records(edge['node']['safegraph_core'],index=[0])
            df['placekey'] = [edge['node']['placekey']]
            dfs = dfs.append(df.squeeze(), ignore_index=True)
        time.sleep(2)
        cursor = res['data']['search']['places']['results']['pageInfo']['endCursor']
        nextPage = res['data']['search']['places']['results']['pageInfo']['hasNextPage']
        st.sidebar.write("   Found places:", len(dfs))
        st.session_state.counter += 1

    else:
        st.sidebar.write(f"""Completed querying all places in Polygon #{i}""")

    return(dfs)

def month_analysis(data,start_date,end_date):

    time_range = dates[start_date:end_date+1]

    place_files = []
    for month in time_range:
        start_string = month.strftime("%Y-%m-%d")
        end_string = (month + relativedelta(months=1)).strftime("%Y-%m-%d")

        #Get the data from the SafeGraph API
        place_file = get_monthly_data(list(data['placekey']),start_string,end_string)
        place_files.append(place_file)

    return pd.concat(place_files)



def get_monthly_data(placekeys,start_date,end_date):

    st.sidebar.write(f"""Getting Data: {start_date}""")
    #The max number of records SG will return is 20 places so we will have to loop through them
    records_per_call = 20
    got_so_far = 0
    got_this_batch = records_per_call
    #Make an empty DataFrame to hold all of the places
    poi_dfs = []

    while got_this_batch == records_per_call:
        variables = {
          "placekeys": placekeys[got_so_far:(got_so_far+records_per_call)],
            "start_date": start_date,
            "end_date": end_date
        }

        query = f"""
        query MyQuery2($placekeys: [Placekey!], $start_date: String!, $end_date: String!) {{
          batch_lookup(placekeys: $placekeys) {{
            safegraph_monthly_patterns(by_range: {{start_date: $start_date, end_date: $end_date}}) {{
              placekey
              poi_cbg
              popularity_by_hour
              date_range_end
              date_range_start
              raw_visit_counts
              raw_visitor_counts
              visits_by_day
              visitor_home_cbgs
              visitor_daytime_cbgs
            }}
            safegraph_core {{
              latitude
              longitude
              location_name
              naics_code
              street_address
              postal_code
              sub_category
              top_category
              city
            }}
          }}
        }}
                    """

        res = endpoint(query,variables)
        key0 = list(res)[0]
        key1 = list(res[key0])[0]
        #pd.DataFrame.from_records(res[key0][key1][0]['safegraph_monthly_patterns'])
        r = res[key0][key1]
        for place in r:
            df = pd.DataFrame.from_records(place)
            df = df.rename(columns={'safegraph_core': 'safegraph_monthly_patterns'}).stack().unstack().transpose()
            poi_dfs.append(df)
        got_this_batch = len(r)
        got_so_far += got_this_batch
    poi_dfs = pd.concat(poi_dfs,ignore_index=True)
    return poi_dfs

st.title("HR&A SafeGraph Analysis Tool")


form = st.form(key="inputs")
m = folium.Map(location=[40.70, -73.94], zoom_start=10, tiles='CartoDB positron')
Draw(export=False).add_to(m)

with form:
    studyname = st.text_input("Project Name",value="")
    st.markdown("***")
    col1, col2 = st.columns([3, 1])
    with col1:
        folium_static(m,width="50%",height="50%")

    
    with col2:
        uploaded_file = st.file_uploader("Upload Study Area Shapefile")

    placeholder = st.empty()
    st.markdown("***")
    options = st.select_slider(
     'Select a timeframe',
     options=[dt.strftime("%B %Y") for dt in dates],
     value=([dt.strftime("%B %Y") for dt in dates][len(dates)-25], [dt.strftime("%B %Y") for dt in dates][len(dates)-1]))

    start_month = dates.index(datetime.datetime.strptime(options[0],"%B %Y"))
    end_month = dates.index(datetime.datetime.strptime(options[1],"%B %Y"))
    st.markdown("***")
    st.markdown("***")
    expander = st.expander("Advanced Settings")
    with expander:
        st.write(f"Open original NAICS def google sheet")

    st.markdown("***")

    submitted = st.form_submit_button(label="Submit")

    def convert_df(df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
     return df.to_csv().encode('utf-8')

    def printer(n,gdf):
        st.sidebar.write(f"Starting Process:")
        time.sleep(5)
        b = gdf.iloc[0].geometry
        radius, center = shp.minimum_bounding_circle(b)
        p = gpd.GeoSeries([Point(center[0], center[1])], crs="EPSG:26914").to_crs(epsg=4326)
        data = query_radius(1,p[0].y,p[0].x,round(radius))
        place_files = month_analysis(data,start_month,end_month)
        csv = convert_df(place_files)

        with download:
            st.sidebar.write(f"""Completed""")
            st.success('Success!')
            st.download_button(label="Download files",
                        data=csv,
                        file_name= studyname + '.csv',
                        mime='text/csv',)

    


download = st.container()

if uploaded_file is not None:
    dataframe = gpd.read_file(uploaded_file).to_crs(epsg=26914)
    data_map = dataframe.to_crs(epsg=4326)
    folium.GeoJson(data=data_map['geometry'],style_function=lambda x: {'fillColor': 'orange'}).add_to(m)

if submitted and uploaded_file is not None:
    if studyname == "":
        st.error('Please name your project')
    else:
        with st.spinner('Processing...'):
            printer(studyname, dataframe)



if submitted and uploaded_file is None:

    if studyname == "":
        st.error('Please upload your shapefile and name your project')
    else:
        st.error('Please upload your shapefile')





if uploaded_file is not None:
    dataframe = gpd.read_file(uploaded_file).to_crs(epsg=4326)
    geometry = dataframe['geometry']
    bbox = dataframe.total_bounds
    m.fit_bounds([[bbox[1],bbox[0]],[bbox[3],bbox[2]]], padding=[20,20])
    folium.GeoJson(data=geometry).add_to(m)


# call to render Folium map in Streamlit
folium_static(m)
