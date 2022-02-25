import streamlit as st
import streamlit.components.v1 as components
import time

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

with st.sidebar:
    st.header("Set Focus Here on Page Reload")
    st.write("Please click button at bottom of page.")
    for x in range(30):
        time.sleep(1)
        text_field = st.write("Field "+str(x))
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

st.write(f"Page load: {st.session_state.counter}")

