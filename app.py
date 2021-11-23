import streamlit as st 
import pandas as pd
import datetime as dt
import itertools
import math
import streamlit.components.v1 as stc

# Settings
st.set_page_config(
	layout="centered",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	initial_sidebar_state="collapsed",  # Can be "auto", "expanded", "collapsed"
	page_title=None,  # String or None. Strings get appended with "• Streamlit". 
	page_icon=None,  # String, anything supported by st.image, or None.
)
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 500px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 500px;
        margin-left: -500px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Import data
df = pd.read_csv('database.csv', parse_dates=['date'])
df['date'] = df['date'].apply(lambda x: x.date())
products = df.iloc[:,2:-2].columns

# Banner
HTML_BANNER = """
    <div style="background-color:#464e5f;padding:10px;border-radius:10px">
    <h1 style="color:white;text-align:center;">Taho</h1>
    <p style="color:white;text-align:center;">Ad Hoc OMS</p>
    </div>
    """
stc.html(HTML_BANNER)

# Selector pannel
sc = st.container()
sc.header("Summary Data")
sc.write("View summarised data for any specified date")
selected_date = sc.date_input('Select a date', value=dt.date.today(), min_value=None, max_value=None, key=None, help=None, on_change=None, args=None, kwargs=None)

# Display summary
selected_df = df[df['date'] == selected_date]
columns = sc.columns(5)

count = 0
for col in itertools.cycle(columns):
    
    if count == len(products):
        break
    else:
        average = df[products[count]].mean()
        amount = selected_df[products[count]].sum()
        percentage_change = ((amount-average)/average)*100
        col.metric(f"{products[count]}", f"{amount}", f"{percentage_change:.2f} %")
        count += 1

# Add new data 
with st.sidebar.form(key='my_form'):

    st.header("Add New Order")
    form_dict = {}
    form_dict['date'] = st.date_input('Date', value=dt.date.today(), min_value=None, max_value=None, key=None, help=None, on_change=None, args=None, kwargs=None)
    form_dict['address'] = st.text_input('Address', value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None)
    col1, col2 = st.columns(2)
    for i, col in enumerate(range(len(products))):
        product = products[i]
        if i % 2 == 0:form_dict[product] = col1.number_input(product, min_value=0, key=i)
        else:form_dict[product] = col2.number_input(product, min_value=0, key=i)
        
    form_dict['Amount'] = st.number_input('Amount', min_value=0)
    form_dict['Author'] = st.selectbox("Author", ['XX','WES','Ku','Evan'], index=0, key=None, help=None, on_change=None, args=None, kwargs=None)
    submit_button = st.form_submit_button(label='Add Order')
    
    if submit_button:
        df = df.append(form_dict, ignore_index=True)
        df.to_csv('database.csv', index=False)
        df = pd.read_csv('database.csv', parse_dates=['date'])
        df['date'] = df['date'].apply(lambda x: x.date())
    
# Delete row
with st.sidebar.form(key='delete_form'):

    st.header("Remove Order")
    del_index = st.multiselect('Index of row you want to delete', df.index)
    del_submit_button = st.form_submit_button(label='Remove Row')
    
if del_submit_button:
    df = df.drop(del_index)
    df.to_csv('database.csv', index=False)
    
# Read the DF
format_dict = {}
for i in products: 
    format_dict[i] = "{:.0f}"
sc.dataframe(df.style.format(format_dict))

# Import and export
ie_expander = st.expander("Edit raw excel file")
downloaded = ie_expander.download_button("Download raw file", data=df.to_csv(index=False).encode('utf-8'), file_name="database.csv", help="Download the excel file for all the order history", on_click=None)
uploaded_file = ie_expander.file_uploader('Upload File', type='csv', help="Once done editing the raw file, reupload here. Don't forget to save a backup copy just incase!")
if uploaded_file:
    dataframe = pd.read_csv(uploaded_file, parse_dates=["date"])
    dataframe.to_csv('database.csv', index=False)
    df = pd.read_csv('database.csv', parse_dates=['date'])
    df['date'] = df['date'].apply(lambda x: x.date())

