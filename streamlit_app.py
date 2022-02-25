import streamlit as st
import streamlit.components.v1 as components
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import time
import shapestats_kc as shp
from sgqlc.endpoint.http import HTTPEndpoint

st.set_page_config(page_title="HR&A SafeGraph Analysis Template", page_icon="📈", layout="centered")

if "counter" not in st.session_state:
    st.session_state.counter = 1



hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            button[data-testid] {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            div > div > iframe{display: none;}
            div[data-testid="stVerticalBlock"]{gap: 0em !important;}
            </style>
            """
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
        st.sidebar.write("&nbsp;&nbsp;&nbsp;&nbsp;Found places:", len(dfs))
        st.session_state.counter += 1

    else:
        st.sidebar.write(f"""Completed querying all places in Polygon #{i}""")

        for t in range(1,30):
            time.sleep(1)
            scroll()
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
        p = gpd.GeoSeries([Point(center[0], center[1])], crs="EPSG:26914").to_crs(epsg=4326)
        data = query_radius(1,p[0].y,p[0].x,round(radius))
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
