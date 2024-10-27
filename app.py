import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import requests
from googleapiclient.discovery import build
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from database import InventoryDB

# Constants
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=AIzaSyA8SASB1-aeG5T7Pt6tiRIWZWPCcwm-iPo'

# Set the title and favicon for the browser tab
st.set_page_config(page_title='Inventory Tracker', page_icon=':shopping_bags:')

# Initialize the database connection
db = InventoryDB()
db.initialize_data()

# Load data from MongoDB
df = db.load_data()

# Store DataFrame in session state
if 'inventory_df' not in st.session_state:
    st.session_state.inventory_df = df

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ("Dashboard", "Inventory Overview", "Add New Item", "Demand Forecast"))

# Page: Inventory Overview
if page == "Inventory Overview":
    st.info("Products in the inventory:")
    st.write(df)

    # Units Left Chart
    st.subheader('Units Left')
    
    # Filter items that need reordering
    need_to_reorder = df[df['units_left'] < df['reorder_point']]['item_name']
    
    if not need_to_reorder.empty:
        items = '\n'.join(f'* {name}' for name in need_to_reorder)
        st.error(f"We're running dangerously low on the items below:\n{items}")

    # Handle missing or NaN values to avoid infinity warnings
    df['units_left'] = df['units_left'].fillna(0)
    df['reorder_point'] = df['reorder_point'].fillna(0)

    st.altair_chart(
        alt.Chart(df)
            .mark_bar(orient='horizontal')
            .encode(
                x='units_left:Q',
                y='item_name:N',
            ) +
        alt.Chart(df)
            .mark_point(shape='diamond', filled=True, size=50, color='salmon', opacity=1)
            .encode(x='reorder_point:Q', y='item_name:N'),
        use_container_width=True
    )
    st.caption('NOTE: The :diamonds: location shows the reorder point.')

    # Best Sellers Chart
    st.subheader('Best Sellers')
    st.altair_chart(
        alt.Chart(df)
            .mark_bar(orient='horizontal')
            .encode(x='units_sold:Q', y=alt.Y('item_name:N').sort('-x')),
        use_container_width=True
    )

# Page: Add New Item
elif page == "Add New Item":
    st.title("Add New Item")
    
    with st.form("add_item_form"):
        item_name = st.text_input("Item Name")
        price = st.number_input("Price", value=0.00, step=0.01, format="%.2f")
        cost_price = st.number_input("Cost Price", value=0.00, step=0.01, format="%.2f")
        units_left = st.number_input("Units Left", min_value=0, value=0)
        reorder_point = st.number_input("Reorder Point", min_value=0, value=0)
        units_sold = st.number_input("Units Sold", min_value=0, value=0)
        description = st.text_area("Description")

        submitted = st.form_submit_button("Add Item")
        if submitted:
            new_item = {
                'item_name': item_name,
                'price': price,
                'cost_price': cost_price,
                'units_sold': units_sold,
                'units_left': units_left,
                'reorder_point': reorder_point,
                'description': description,
            }
            db.add_item(new_item)
            st.success(f"Added new item: {item_name}")

# Page: Demand Forecast
elif page == "Demand Forecast":
    st.title("Demand Forecasting")
    st.info("View forecasted demand for selected items.")

    item_names = df['item_name'].tolist()
    selected_item = st.selectbox("Select an item to forecast", item_names)

    # Simulated historical sales data
    mean_sales = 30
    std_dev = 10
    seasonal_effects = [0.9, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 1.5, 1.2, 1.0, 0.8, 0.7]
    trend = np.linspace(0, 10, 12)
    promotions = [0, 0, 0, 20, 0, 0, 30, 0, 0, 10, 0, 0]

    monthly_sales = (np.random.normal(mean_sales, std_dev, size=12) + trend + promotions) * seasonal_effects
    monthly_sales = monthly_sales.clip(0)
    time_periods = pd.date_range(start='2023-01-01', periods=12, freq='M')

    item_data = pd.Series(monthly_sales, index=time_periods)

    # Fit the model
    model = ExponentialSmoothing(item_data, trend='add', seasonal=None).fit()

    # Forecast the next 6 months
    forecast = model.forecast(steps=6)

    # Prepare data for Gemini API
    gemini_payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Analyze the sales forecast for the item '{selected_item}'. The historical sales data is {item_data.tolist()} and the forecasted sales for the next 6 months are {forecast.tolist()}."
                    }
                ]
            }
        ]
    }

    # Call Gemini API for analysis
    try:
        gemini_response = requests.post(GEMINI_API_URL, json=gemini_payload)
        gemini_response.raise_for_status()
        gemini_data = gemini_response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Gemini API Error: {e}")
        analysis_text = ""
    else:
        analysis_text = gemini_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "")

    # Combine historical and future data for plotting
    all_sales = np.concatenate([item_data.values, forecast])
    all_dates = pd.date_range(start='2023-01-01', periods=len(all_sales), freq='M')

    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(all_dates[:12], item_data, label='Historical Sales', marker='o', color='blue')
    plt.plot(all_dates[12:], forecast, label='Forecasted Sales', marker='o', color='red')
    plt.title(f'Demand Forecast for {selected_item}')
    plt.xlabel('Date')
    plt.ylabel('Units Sold')
    plt.axvline(x=item_data.index[-1], color='gray', linestyle='--', label='Forecast Start')
    plt.legend()
    plt.grid()
    st.pyplot(plt)

    # Display analysis from Gemini API
    st.subheader("AI Analysis")
    st.write(analysis_text)

elif page == "Dashboard":
    st.title("Dashboard")

    # Add your dashboard stats and visualizations here
    st.header("Key Inventory Statistics")

    # Calculating key metrics
    total_revenue = df['price'].sum()
    total_units_sold = df['units_sold'].sum()
    average_cost_price = df['cost_price'].mean()
    low_stock_items = df[df['units_left'] < df['reorder_point']]['item_name'].tolist()
    total_items_in_stock = df['units_left'].sum()
    total_unique_items = df['item_name'].nunique()
    stock_value = (df['price'] * df['units_left']).sum()
    gross_profit = total_revenue - (df['cost_price'] * df['units_sold']).sum()
    

    # Create columns for better layout
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
        st.metric("Total Items in Stock", total_items_in_stock)

    with col2:
        st.metric("Total Units Sold", total_units_sold)
        st.metric("Total Unique Items", total_unique_items)
        
    with col3:
        st.metric("Average Cost Price", f"₹{average_cost_price:.2f}")
        st.metric("Total Stock Value", f"₹{stock_value:,.2f}")

    if low_stock_items:
        st.warning(f"Low Stock Items: {', '.join(low_stock_items)}")
    else:
        st.success("No low stock items currently.")

    # Sales Analysis Visualization
    sales_data = df.groupby('item_name').agg({'units_sold': 'sum', 'price': 'mean'}).reset_index()

    st.subheader("Sales Performance by Item")
    st.altair_chart(
        alt.Chart(sales_data)
            .mark_bar()
            .encode(
                x='item_name:N',
                y='units_sold:Q',
                color='item_name:N'
            )
            .properties(
                title='Total Units Sold by Item'
            ),
        use_container_width=True
    )

    # Pie Chart for Stock Distribution
    st.subheader("Stock Distribution")
    stock_distribution = df[['item_name', 'units_left']]

    st.altair_chart(
        alt.Chart(stock_distribution)
            .mark_arc()
            .encode(
                theta=alt.Theta(field='units_left', type='quantitative'),
                color=alt.Color(field='item_name', type='nominal'),
                tooltip=['item_name:N', 'units_left:Q']
            )
            .properties(
                title='Stock Distribution by Item'
            ),
        use_container_width=True
    )

    # Time Series Analysis
    st.subheader("Sales Trend Over Time")
    # Check if 'date' column exists
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        sales_trend = df.groupby(df['date'].dt.to_period('M')).agg({'units_sold': 'sum'}).reset_index()
        sales_trend['date'] = sales_trend['date'].dt.to_timestamp()

        st.altair_chart(
            alt.Chart(sales_trend)
                .mark_line(point=True)
                .encode(
                    x='date:T',
                    y='units_sold:Q',
                    tooltip=['date:T', 'units_sold:Q']
                )
                .properties(
                    title='Monthly Sales Trend'
                ),
            use_container_width=True
        )

    # Additional analysis: Top 5 items by revenue
    st.subheader("Top 5 Items by Revenue")
    top_items = df.groupby('item_name').agg({'price': 'mean', 'units_sold': 'sum'}).reset_index()
    top_items['total_revenue'] = top_items['price'] * top_items['units_sold']
    top_items = top_items.nlargest(5, 'total_revenue')

    st.altair_chart(
        alt.Chart(top_items)
            .mark_bar()
            .encode(
                x='item_name:N',
                y='total_revenue:Q',
                color='item_name:N'
            )
            .properties(
                title='Top 5 Items by Revenue'
            ),
        use_container_width=True
    )

    # Additional analysis: Stock Level Analysis
    st.subheader("Stock Level Analysis")
    stock_analysis = df[['item_name', 'units_left', 'reorder_point']]
    stock_analysis['stock_status'] = stock_analysis.apply(lambda x: 'Low Stock' if x['units_left'] < x['reorder_point'] else 'Sufficient', axis=1)

    st.altair_chart(
        alt.Chart(stock_analysis)
            .mark_bar()
            .encode(
                x='item_name:N',
                y='units_left:Q',
                color='stock_status:N'
            )
            .properties(
                title='Stock Levels with Reorder Points'
            ),
        use_container_width=True
    )