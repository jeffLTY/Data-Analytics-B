# import streamlit as st

# st.title("🎈 My new app")
# st.write(
#     "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
# )

import streamlit as st
import pandas as pd
import plotly.express as px
from matplotlib import pyplot as plt
import seaborn as sns

try:
    import mysql.connector
except ImportError:
    st.error("MySQL Connector not found. Please install requirements using 'pip install -r requirements.txt'")
    st.stop()

# Display loading message
st.title("🎈 Data Analytics Dashboard")
with st.spinner('Connecting to database...'):
    try:
        # Read connection parameters securely from Streamlit secrets
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=st.secrets["mysql"]["port"]
        )
    except mysql.connector.Error as e:
        st.error(f"Error connecting to MySQL database: {e}")
        st.stop()
    except KeyError as e:
        st.error("Missing MySQL configuration in secrets. Please check your .streamlit/secrets.toml file.")
        st.stop()

    try:
        # Query data
        query = "SELECT * FROM gender_gap_edu_sex_wide_v3"
        gendergap_edu_sex = pd.read_sql(query, conn)
        st.dataframe(gendergap_edu_sex)
    except Exception as e:
        st.error(f"Error querying database: {e}")
    finally:
        # Close connection
        conn.close()

# Check and display column names
st.write("Available columns:", gendergap_edu_sex.columns.tolist())

def _plot_series(series, series_name, series_index=0):
    palette = list(sns.palettes.mpl_palette('Dark2'))
    # Check if required columns exist
    required_columns = ['year', 'gap_change_from_first']
    missing_columns = [col for col in required_columns if col not in series.columns]
    
    if missing_columns:
        st.error(f"Missing required columns: {missing_columns}")
        return
        
    xs = series['year']
    ys = series['gap_change_from_first']
    plt.plot(xs, ys, label=series_name, color=palette[series_index % len(palette)])

try:
    fig, ax = plt.subplots(figsize=(10, 5.2), layout='constrained')
    
    # Verify column names before sorting
    if 'year' not in gendergap_edu_sex.columns:
        st.error("Column 'year' not found in the dataset")
        st.stop()
        
    if 'education' not in gendergap_edu_sex.columns:
        st.error("Column 'education' not found in the dataset")
        st.stop()
        
    df_sorted = gendergap_edu_sex.sort_values('year', ascending=True)
    
    for i, (series_name, series) in enumerate(df_sorted.groupby('education')):
        _plot_series(series, series_name, i)
    
    fig.legend(title='education', bbox_to_anchor=(1, 1), loc='upper left')
    sns.despine(fig=fig, ax=ax)
    plt.xlabel('year')
    plt.ylabel('gap_change_from_first')
    
    # Display the plot in Streamlit
    st.pyplot(fig)
    
except Exception as e:
    st.error(f"Error creating visualization: {e}")
