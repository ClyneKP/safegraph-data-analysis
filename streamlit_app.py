import streamlit as st
import geopandas as gpd
import pandas as pd
import time
import shapestats_kc as shp
from sgqlc.endpoint.http import HTTPEndpoint

st.set_page_config(page_title="HR&A SafeGraph Analysis Template", page_icon="📈", layout="centered")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            button[data-testid] {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

adjust_console = """
            <script>
            $('.block-container').scrollTop($('.block-container')[0].scrollHeight);
            </script>
            """

url = 'https://api.safegraph.com/v2/graphql'
headers = {'apikey': st.secrets["SG_KEY"]}

endpoint = HTTPEndpoint(url, headers)


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
        st.sidebar.write("&nbsp;&nbsp;&nbsp;&nbsp;Found places:", len(dfs))
    else:
        st.sidebar.write(f"""Completed querying all places in Polygon #{i}""")
        for t in range(1,20):
            time.sleep(1)
            st.markdown(adjust_console, unsafe_allow_html=True) 
            st.sidebar.write(f"""Next""")
    return(dfs)



st.title("HR&A SafeGraph Analysis Tool")


form = st.form(key="inputs")


with form:
    studyname = st.text_input("Project Name",value="")
    uploaded_file = st.file_uploader("Upload Study Area Shapefile")
    if uploaded_file is not None:
        dataframe = gpd.read_file(uploaded_file).to_crs(epsg=26914)

    expander = st.expander("See all records")
    with expander:
        st.write(f"Open original NAICS def google sheet")

    submitted = st.form_submit_button(label="Submit")

    def convert_df(df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
     return df.to_csv().encode('utf-8')

    def printer(n,gdf):
        st.sidebar.write(f"Starting Process:")
        time.sleep(5)
        b = gdf.iloc[0].geometry
        radius, center = shp.minimum_bounding_circle(b)
        lat = 37.78247
        lng = -122.407752
        distance = 100
        data = query_radius(1,lat,lng,distance)
        csv = convert_df(data)

        with download:
            st.sidebar.write(f"""Completed""")
            st.success('Success!')
            st.download_button(label="Download files",
                        data=csv,
                        file_name= studyname + '.csv',
                        mime='text/csv',)

    

download = st.container()

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
        






