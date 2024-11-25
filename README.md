# Ambit DCF Model Assignment

This project was developed to create a web application that computes intrinsic P/E ratios and the degree of overvaluation for companies listed on the NSE/BSE. It uses financial data sourced from Screener.

### Overview

The primary objective of this project was to build an interactive web application that retrieves critical financial data for a specified company symbol (e.g., NESTLEIND) from Screener. This data is utilized to calculate metrics such as the current P/E ratio, FY23 P/E ratio, compounded sales and profit growth rates, and to determine the intrinsic P/E and overvaluation degree using a growth-RoC DCF model.

### Tools and Technologies
- **Python**: For backend logic and calculations.
- **Streamlit**: To create the interactive user interface.
- **Pandas**: For data manipulation and analysis.
- **Plotly Express**: For data visualization.
- **BeautifulSoup**: For scraping web data.
- **NumPy**: For numerical calculations.

### App Demonstration
- **Web App**: [Growth-RoC DCF Model Web App](https://growth-roc-dcf-model.streamlit.app/)
- **Code Repository**: [GitHub Repository](https://github.com/LuciferStudies/Ambit-DCF-model-Assignment)

### Features

1. **Company Financial Data Scraping**:  
   Retrieves crucial financial details like Current P/E, FY23 P/E, and 5-year median RoCE from a company’s Screener page. It adapts to any entered company symbol via the format `https://www.screener.in/company/<symbol>/`.

2. **Computed Metrics**:
   - **Intrinsic P/E**: Derived using a DCF-based model that considers user-defined variables such as cost of capital and RoCE.
   - **Degree of Overvaluation**: The percentage difference between the lower of the current or FY23 P/E and the calculated intrinsic P/E.

3. **Growth Analysis**:  
   Displays the compounded sales and profit growth over TTM, 3, 5, and 10-year periods using updated data from Screener.

4. **User Interactivity**:  
   Users can adjust inputs like cost of capital, RoCE, growth periods, and rates through interactive sliders, enhancing user engagement and customization.

### Setup Instructions

Install the necessary Python packages using:
```
pip install -r requirements.txt
```

Key dependencies:
- Streamlit 1.12.0
- Requests 2.27.1
- BeautifulSoup4 4.11.1
- Pandas 1.4.0
- Plotly 5.5.0
- NumPy 1.22.0


### Challenges Encountered

This project was my first foray into financial data analysis and terminologies such as intrinsic value calculation and DCF models. Although I initially struggled with the implementation of the intrinsic P/E and overvaluation calculations, I invested considerable effort into understanding and accurately emulating the desired functionality. I am eager to receive feedback on potential improvements and to further my knowledge in financial modeling.

### Additional Resources

For a deeper understanding of the intrinsic P/E calculation, I referred to a [YouTube tutorial](https://www.youtube.com/watch?v=rZHlK5Rjzks) starting at the 29th minute, which was instrumental in grasping the underlying formulas to understand and calculate intrinsic value but could not integrate the logic in the code.

Thank you for considering this project.
