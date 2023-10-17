import webbrowser

import streamlit as st

st.set_page_config(
    page_title="Airbnb Dash | About",
    page_icon=":hut:",
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

st.markdown(
    """
    ## 📚 Database Structure 

    This database is meticulously structured to cater to the needs of the overall **Airbnb Advisor** project, a web app augmented with Streamlit 
    to provide comprehensive visuals, metrics, and AI chatbot functionalities. The schema is primarily based on 
    SQLAlchemy and encompasses a well-organized hierarchy of tables that are interconnected through foreign keys to 
    maintain data integrity and relationships. 

    ## 🔗 Lookup Tables

    - **Simple Lookup Tables**: Include `HostResponseTimes`, `PropertyTypes`, and `RoomTypes`. They are basic lookup 
    tables each possessing a unique identifier and a description column. For instance, in `HostResponseTimes`, 
    `host_response_time_id` is the primary key.

    - **Hierarchical Lookup Tables**: These are multi-level lookup tables such as `Neighborhoods` and `Amenities`, which 
    maintain hierarchical relationships. `Neighborhoods` has a foreign key `city_id`, connecting it to the `Cities` 
    table, establishing a parent-child relationship between cities and neighborhoods.

    ## 🌐 Entity Tables

    - **Hosts**: An entity table where each host is uniquely identified by a `host_id`. It holds various host attributes 
    and is connected to the `HostResponseTimes` table via a foreign key.

    - **ListingsCore**: Central entity table for listing various properties. It maintains relationships with several 
    tables such as `Hosts`, `PropertyTypes`, and `RoomTypes` through foreign keys. This relationship helps in 
    maintaining a structured data flow and ensuring referential integrity.

    ## ➡️ Extension Tables

    - **ListingsLocation**, **ListingsReviewsSummary**: These extension tables are linked to the `ListingsCore` table, 
    extending its information. For instance, `ListingsLocation` is connected through a foreign key to `ListingsCore` and 
    `Neighborhoods`, creating a relationship between listings and their respective locations.

    ## 🌉 Junction Tables

    - **ListingsAmenities**: Acts as a bridge between `ListingsCore` and `Amenities`, allowing for the mapping of 
    multiple amenities to multiple listings. This table employs a primary key and maintains foreign key relationships 
    with both involved tables.

    The database design and the use of foreign keys facilitate smooth navigation through various tables, thereby 
    optimizing the execution of complex SQL queries. This thoughtful architecture enables the AI chatbot to execute 
    precise queries, accessing interconnected data across tables efficiently, and providing accurate results within the 
    Airbnb Advisor application.

    ## 🤖 AI Chatbot 

    The AI Chatbot integrated into the 'Airbnb Advisor' is a powerful component designed to interact with the database 
    dynamically. Through the use of Natural Language Processing (NLP), the chatbot can interpret user queries and execute 
    SQL commands to retrieve relevant information. 

    The unique feature of the database schema that aids the chatbot is the utilization of the `CustomBase` class. This 
    class encapsulates metadata like `_table_type` and `_description`, enabling the chatbot to understand and interact 
    with the database more intelligently. The metadata acts as a guide for the chatbot, assisting it in identifying the 
    right tables and establishing relevant connections, thus making query executions more efficient and accurate.

    Furthermore, the chatbot is capable of navigating through the hierarchical structures, foreign key relationships, and 
    junction tables in the database. This ensures that the chatbot can handle complex queries, providing users with 
    detailed and interconnected information that spans across multiple tables, ensuring that the responses are both 
    comprehensive and precise.
    
    The design and architecture of the database play a crucial role in supporting the chatbot's functionalities, ensuring 
    it operates with maximal efficiency and accuracy, providing users of the 'Airbnb Advisor' with reliable and insightful 
    data driven guidance.
    """
)
