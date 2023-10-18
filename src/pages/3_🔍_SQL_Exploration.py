import webbrowser

import streamlit as st

st.set_page_config(
    page_title="Airbnb Advisor | SQL Exploration",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)

# Configure the sidebar
st.sidebar.text("")
st.sidebar.text("")
st.sidebar.markdown("Developed by Ben Harman and powered by Streamlit.")
if st.sidebar.button("🧪 Source Code"):
    webbrowser.open_new_tab("https://github.com/benharmandev/airbnb-advisor")
if st.sidebar.button("🌐 BenHarman.dev"):
    webbrowser.open_new_tab("https://benharman.dev")

st.title("🔍 SQL Exploration")
if st.button("Refresh Data"):
    conn.reset()

conn = st.experimental_connection("listings_sqlite", type="sql")


def execute_sql(query):
    try:
        df = conn.query(query)
        return df
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None


# Container 1
with st.container():
    st.markdown("The most expensive neighborhood is **Bel Air**.")
    st.code(
        """
    SELECT neighborhood
    FROM listings
    ORDER BY price DESC
    LIMIT 1;
    """
    )

# Container 2
with st.container():
    st.markdown("The neighborhood with the most listings is **Downtown LA**.")
    st.code(
        """
    SELECT neighborhood, COUNT(*)
    FROM listings
    GROUP BY neighborhood
    ORDER BY COUNT(*) DESC
    LIMIT 1;
    """
    )

# ... Repeat similar blocks for Containers 3-8 ...

# Container 8
with st.container():
    st.markdown(
        "The neighborhood with the highest average review scores is **Santa Monica**."
    )
    st.code(
        """
    SELECT neighborhood, AVG(review_scores_rating)
    FROM listings
    WHERE number_of_reviews > 50
    GROUP BY neighborhood
    ORDER BY AVG(review_scores_rating) DESC
    LIMIT 1;
    """
    )
