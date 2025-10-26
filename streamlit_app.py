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
        query = "SELECT * FROM gender_gap_edu_sex_wide_v2"
        gendergap_edu_sex = pd.read_sql(query, conn)
        gendergap_edu_sex #st.dataframe(gendergap_edu_sex)
    except Exception as e:
        st.error(f"Error querying database: {e}")
    finally:
        # Close connection
        conn.close()

def _plot_series(series, series_name, series_index=0, ax=None):
    palette = list(sns.palettes.mpl_palette('Dark2'))
    xs = pd.to_numeric(series['year'], errors='coerce')
    ys = pd.to_numeric(series['gap_change_from_first'], errors='coerce')
    
    ax.plot(xs, ys, label=series_name, color=palette[series_index % len(palette)])
fig, ax = plt.subplots(figsize=(10, 5.2), layout='constrained')
gendergap_edu_sex['year'] = pd.to_numeric(gendergap_edu_sex['year'], errors='coerce')
df_sorted = gendergap_edu_sex.sort_values('year', ascending=True)
for i, (series_name, series) in enumerate(df_sorted.groupby('education')):
     _plot_series(series, series_name, i, ax=ax)

# format axes and legend once (not inside loop)
ax.set_xlabel('year')
ax.set_ylabel('gap_change_from_first')
sns.despine(fig=fig, ax=ax)
ax.legend(title='education', bbox_to_anchor=(1, 1), loc='upper left')

# explicitly render Matplotlib figure in Streamlit
st.pyplot(fig)


