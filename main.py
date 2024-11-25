import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px

# Define the Screener URL structure
BASE_URL = "https://www.screener.in/company/{symbol}/"

# Fetch and parse HTML from Screener
def fetch_data_from_screener(symbol):
    url = BASE_URL.format(symbol=symbol)
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Failed to fetch data for {symbol}. Please check the symbol.")
        return None
    return BeautifulSoup(response.content, 'html.parser')

# Extract EPS from the Quarterly Results table
def extract_eps(parsed_html):
    section = parsed_html.find('section', {'id': 'quarters'})
    if section:
        rows = section.find('table').find_all('tr')
        for row in rows:
            if "EPS in Rs" in row.text:
                eps = float(row.find_all('td')[-1].text.strip())  # Fetching the latest EPS value from the last column
                return eps
    st.error("EPS data not found in the quarterly results section.")
    return None

# Extract key metrics from Screener HTML
def extract_metrics(parsed_html):
    stock_symbol = parsed_html.find('h1', class_='h2').text.strip()
    current_pe = current_price = None
    pe_elements = parsed_html.find_all('li', class_='flex flex-space-between')
    for element in pe_elements:
        if 'Stock P/E' in element.text:
            current_pe = float(element.find('span', class_='number').text.strip())
        elif 'Current Price' in element.text:
            current_price = float(element.find('span', class_='number').text.strip().replace(',', ''))
    return stock_symbol, current_pe, current_price

# Extract and display Compounded Growth Rates
def extract_growth(parsed_html, metric_name):
    section = parsed_html.find('section', {'id': 'profit-loss'})
    growth_data = {}
    if section:
        tables = section.find_all('table', class_='ranges-table')
        for table in tables:
            if metric_name in table.text:
                rows = table.find_all('tr')[1:]  # Skipping the header row
                for row in rows:
                    period = row.find_all('td')[0].text.strip()
                    value = row.find_all('td')[1].text.strip() 
                    growth_data[period] = value
    return growth_data

# Display growth data in a table and chart
def display_growth_data(growth_data, title):
    df = pd.DataFrame(list(growth_data.items()), columns=['Period', 'Growth'])
    st.subheader(title + " Table")
    st.table(df)
    st.subheader(title + " Chart")
    fig = px.bar(df, x='Period', y='Growth', title=title)
    st.plotly_chart(fig)

# Calculate intrinsic P/E based on DCF
def calculate_intrinsic_pe(eps, growth_rate, roce, coc, high_growth_period, fade_period, terminal_growth_rate):
    growth_rate /= 100
    roce /= 100
    coc /= 100
    terminal_growth_rate /= 100
    total_value = 0
    # Calculating the present value for each year's EPS during the high growth period
    for year in range(1, high_growth_period + 1):
        future_eps = eps * (1 + growth_rate) ** year
        total_value += future_eps * (roce / coc) / ((1 + coc) ** year)
    # Calculating fade period
    for year in range(1, fade_period + 1):
        adjusted_growth_rate = growth_rate - (year / fade_period) * (growth_rate - terminal_growth_rate)
        future_eps = eps * (1 + adjusted_growth_rate) ** (high_growth_period + year)
        total_value += future_eps * (roce / coc) / ((1 + coc) ** (high_growth_period + year))
    # Calculating terminal value
    terminal_eps = eps * (1 + terminal_growth_rate) ** (high_growth_period + fade_period)
    terminal_value = terminal_eps * (roce / coc) / (coc - terminal_growth_rate)
    total_value += terminal_value / ((1 + coc) ** (high_growth_period + fade_period))
    return total_value / eps if eps else None

# Calculate degree of overvaluation
def calculate_overvaluation(current_pe, intrinsic_pe):
    if intrinsic_pe:
        return (current_pe / intrinsic_pe - 1) * 100
    return None

# Streamlit UI setup
st.title("Growth-RoC DCF Model")
st.write("This app calculates the intrinsic P/E ratio and degree of overvaluation for a company.")

# Sidebar Inputs
symbol = st.sidebar.text_input("Enter NSE/BSE Symbol", "NESTLEIND")
coc = st.sidebar.slider("Cost of Capital (%)", 8, 16, 12)
roce_slider = st.sidebar.slider("Return on Capital Employed (RoCE) %", 10, 100, 20)
high_growth_period = st.sidebar.slider("High Growth Period (years)", 1, 10, 5)
fade_period = st.sidebar.slider("Fade Period (years)", 1, 10, 5)
growth_rate = st.sidebar.slider("Growth Rate (%)", 1, 30, 10)
terminal_growth_rate = st.sidebar.slider("Terminal Growth Rate (%)", 0, 10, 2)

if st.button("Analyze"):
    parsed_html = fetch_data_from_screener(symbol)
    if parsed_html:
        stock_symbol, current_pe, current_price = extract_metrics(parsed_html)
        eps = extract_eps(parsed_html)
        if eps:
        
            intrinsic_pe = calculate_intrinsic_pe(eps, growth_rate, roce_slider, coc, high_growth_period, fade_period, terminal_growth_rate)
            overvaluation = calculate_overvaluation(current_pe, intrinsic_pe)
            st.subheader("Financial Analysis")
            st.write(f"**Symbol:** {stock_symbol}")
            st.write(f"**Current Price:** {current_price}")
            st.write(f"**Current P/E:** {current_pe}")
            st.write(f"**EPS:** {eps}")
            st.write(f"**Intrinsic P/E:** {intrinsic_pe:.2f}")
            st.write(f"**Overvaluation:** {overvaluation:.2f}%")
            sales_growth = extract_growth(parsed_html, "Sales Growth")
            profit_growth = extract_growth(parsed_html, "Profit Growth")
            display_growth_data(sales_growth, "Sales Growth")
            display_growth_data(profit_growth, "Profit Growth")
        else:
            st.error("EPS data could not be retrieved.")
    else:
        st.error("Failed to retrieve data for the specified symbol.")
