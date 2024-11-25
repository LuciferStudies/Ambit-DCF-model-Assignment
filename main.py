import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import numpy as np

# Define the Screener URL structure
BASE_URL = "https://www.screener.in/company/{symbol}/"

# Function to fetch and parse HTML from Screener
def fetch_data_from_screener(symbol):
    url = BASE_URL.format(symbol=symbol)
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Failed to fetch data for {symbol}. Please check the symbol.")
        return None
    return BeautifulSoup(response.content, 'html.parser')

# Function to extract EPS from the Profit & Loss table
def extract_eps(parsed_html):
    try:
        # Locate the Profit & Loss table
        profit_loss_section = parsed_html.find('section', {'id': 'profit-loss'})
        if not profit_loss_section:
            st.warning("Profit & Loss section not found.")
            return None
        
        # Extract the EPS row
        rows = profit_loss_section.find('table').find_all('tr')
        for row in rows:
            if "EPS in Rs" in row.text:
                eps_values = row.find_all('td')
                eps = float(eps_values[-2].text.strip())  # Latest EPS value
                return eps
    except Exception as e:
        st.warning(f"Error extracting EPS: {e}")
    return None

# Function to extract key metrics from Screener HTML
def extract_metrics(parsed_html):
    try:
        stock_symbol = parsed_html.find('h1', class_='h2').text.strip()
        current_pe, current_price = None, None
        pe_elements = parsed_html.find_all('li', class_='flex flex-space-between')
        for li in pe_elements:
            if 'Stock P/E' in li.text:
                current_pe = float(li.find('span', class_='number').text.strip())
            if 'Current Price' in li.text:
                current_price = float(li.find('span', class_='number').text.strip().replace(',', ''))
        return stock_symbol, current_pe, current_price
    except Exception as e:
        st.warning(f"Error extracting metrics: {e}")
        return None, None, None

# Function to extract Compounded Growth Rates
def extract_growth(parsed_html, metric_name):
    try:
        growth_section = parsed_html.find('section', {'id': 'profit-loss'}).find_all('table', class_='ranges-table')
        for table in growth_section:
            if metric_name in table.text:
                rows = table.find_all('tr')[1:]  # Skip the header row
                growth_data = {}
                for row in rows:
                    period = row.find_all('td')[0].text.strip()
                    value = row.find_all('td')[1].text.strip()
                    growth_data[period] = value
                return growth_data
    except Exception as e:
        st.warning(f"Error extracting {metric_name}: {e}")
    return {}

# Function to prepare Compounded Growth Tables
def prepare_growth_table(growth_data, title):
    df = pd.DataFrame(growth_data.items(), columns=['Period', 'Value'])
    df['Value'] = df['Value'].str.rstrip('%').astype(float)
    st.subheader(title)
    st.table(df)

# Function to plot Compounded Growth Chart
def plot_growth_chart(growth_data, title):
    df = pd.DataFrame(growth_data.items(), columns=['Period', 'Value'])
    df['Value'] = df['Value'].str.rstrip('%').astype(float)
    fig = px.bar(df, x='Period', y='Value', title=title, text='Value')
    st.plotly_chart(fig)

# Corrected DCF-based Intrinsic P/E Calculation
def calculate_intrinsic_pe(eps, growth_rate, roce, coc, high_growth_period, fade_period, terminal_growth_rate):
    try:
        growth_rate = float(growth_rate) / 100
        roce = float(roce) / 100
        coc = float(coc) / 100
        terminal_growth_rate = float(terminal_growth_rate) / 100

        # High Growth Period Calculation
        high_growth_value = 0
        for year in range(1, high_growth_period + 1):
            projected_eps = eps * ((1 + growth_rate) ** year)  # EPS projection
            discounted_value = projected_eps * (roce / coc) / ((1 + coc) ** year)
            high_growth_value += discounted_value

        # Fade Period Calculation
        fade_value = 0
        for year in range(1, fade_period + 1):
            adjusted_growth_rate = growth_rate - ((year / fade_period) * (growth_rate - terminal_growth_rate))
            projected_eps = eps * ((1 + adjusted_growth_rate) ** (high_growth_period + year))
            discounted_value = projected_eps * (roce / coc) / ((1 + coc) ** (high_growth_period + year))
            fade_value += discounted_value

        # Terminal Value Calculation
        terminal_eps = eps * ((1 + terminal_growth_rate) ** (high_growth_period + fade_period))
        terminal_value = terminal_eps * (roce / coc) / (coc - terminal_growth_rate)
        terminal_value_discounted = terminal_value / ((1 + coc) ** (high_growth_period + fade_period))

        # Intrinsic Value and Intrinsic P/E
        total_intrinsic_value = high_growth_value + fade_value + terminal_value_discounted
        intrinsic_pe = total_intrinsic_value / eps if eps else None
        return round(intrinsic_pe, 2) if intrinsic_pe else None
    except Exception as e:
        st.warning(f"Error calculating intrinsic P/E: {e}")
        return None

# Degree of Overvaluation Calculation
def calculate_overvaluation(current_pe, intrinsic_pe):
    try:
        return (current_pe / intrinsic_pe - 1) * 100
    except:
        return None

# Streamlit UI
st.title("Growth-RoC DCF Model")
st.write("This app calculates the intrinsic P/E ratio and degree of overvaluation for a company.")

# Sidebar Inputs
symbol = st.sidebar.text_input("Enter NSE/BSE Symbol (e.g., NESTLEIND)", value="NESTLEIND")
coc = st.sidebar.slider("Cost of Capital (%)", 8, 16, step=1, value=12)
high_growth_period = st.sidebar.slider("High Growth Period (years)", 5, 20, step=1, value=10)
fade_period = st.sidebar.slider("Fade Period (years)", 5, 15, step=1, value=10)
growth_rate = st.sidebar.slider("Growth Rate (%)", 5, 20, step=1, value=10)
terminal_growth_rate = st.sidebar.slider("Terminal Growth Rate (%)", 0, 5, step=1, value=2)
roce_slider = st.sidebar.slider("Return on Capital Employed (RoCE) %", 10, 100, step=1, value=20)

# Trigger Analysis
if st.button("Run Analysis"):
    parsed_html = fetch_data_from_screener(symbol)
    if parsed_html:
        stock_symbol, current_pe, current_price = extract_metrics(parsed_html)
        eps = extract_eps(parsed_html)  # Use correct EPS scraping logic
        sales_growth = extract_growth(parsed_html, "Compounded Sales Growth")
        profit_growth = extract_growth(parsed_html, "Compounded Profit Growth")

        if not eps:
            st.error("Failed to extract EPS. Please check the company symbol.")
        else:
            intrinsic_pe = calculate_intrinsic_pe(
                eps=eps, 
                growth_rate=growth_rate, 
                roce=roce_slider, 
                coc=coc, 
                high_growth_period=high_growth_period, 
                fade_period=fade_period, 
                terminal_growth_rate=terminal_growth_rate
            )
            overvaluation = calculate_overvaluation(current_pe, intrinsic_pe)

            # Display Results
            st.subheader("Results")
            st.write(f"**Stock Symbol:** {stock_symbol}")
            st.write(f"**Current P/E Ratio:** {current_pe}")
            st.write(f"**Current Price:** {current_price}")
            st.write(f"**EPS (from Profit & Loss Table):** {eps}")
            st.write(f"**Intrinsic P/E:** {intrinsic_pe:.2f}" if intrinsic_pe else "Intrinsic P/E: Calculation Error")
            st.write(f"**Degree of Overvaluation:** {overvaluation:.2f}%" if overvaluation else "Degree of Overvaluation: Calculation Error")
            
            # Display Growth Tables and Charts
            if sales_growth:
                st.subheader("Compounded Sales Growth (TTM/3/5/10 Years)")
                prepare_growth_table(sales_growth, "Sales Growth Table")
                plot_growth_chart(sales_growth, "Compounded Sales Growth")

            if profit_growth:
                st.subheader("Compounded Profit Growth (TTM/3/5/10 Years)")
                prepare_growth_table(profit_growth, "Profit Growth Table")
                plot_growth_chart(profit_growth, "Compounded Profit Growth")
    else:
        st.error("Failed to fetch data. Please check the company symbol or internet connection.")
