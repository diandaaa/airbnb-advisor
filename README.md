### ➡️ View the live app [here](https://airbnb-advisor.streamlit.app)!

# Airbnb Advisor

Welcome to my **Airbnb Advisor** project. This app explores a huge set of Airbnb listings and aims to provide actionable insights for hosts. Whether you're new to hosting or a seasoned veteran, explore select cities and find ways to maximize your profitability, ratings, and visibility.

### 📘 Pages at a Glance

- **📊 Charts & Metrics**: View relevant visuals covering several topics including review scores, amenities, and pricing.
- **🗺️ Map**: Get a spatial overview of a specific city's listings arranged by neighborhood and their respective metrics.
- **💻 SQL Exploration**: Dive into the SQL queries and database model that fuel this app's analytics.
- **🤖 AI Chat**: Got specific questions? My AI assistant is here to answer specific questions about the data.
- **📖 About**: Background on the data source, methodology, and the person behind this app.

### 📚 Data Source

This app utilizes data from [Inside Airbnb](http://insideairbnb.com/), a project that focuses on the impact of Airbnb on residential communities. The data was last updated on March 6, 2023. Future updates to the app will be contingent upon new, comparable data releases.

### ⚠️ Disclaimer
This app is an independent project and serves as an exploratory tool. While it aims to provide valuable insights, it is not a substitute for professional advice and nuanced understanding of individual listings.

## Run Locally

1. Clone the repository to your local machine.
2. Download the Inside Airbnb dataset from Kaggle [here](https://www.kaggle.com/datasets/konradb/inside-airbnb-usa).
3. Extract the `usa` folder from the downloaded dataset and place it into the project data folder in the format: `data/usa/...`
4. Initialize the project with `poetry`.
6. Run `setup.py` to initialize and populate the SQLite database. (Note: This takes several minutes as this is a near 100MB write operation to the database.)
7. In your terminal, type `poetry shell` to enter the virtual environment.
8. Finally, run the command `streamlit run src/1_🛖_Home.py` to launch the app in your web browser where it will start at the project home page.
