import streamlit as st
import pandas as pd
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf

st.title('Nasdaq-100 EDA')

hidden_bar=st.expander("About")
hidden_bar.markdown("""
This web app allows users to explore the **Nasdaq-100 Index** by displaying information about its constituent companies, including their sectors and current year-to-date stock closing prices. The index data is web scraped from Wikipedia and the stock prices are obtained from Yahoo! Finance's API. Users can access and download the list of companies sorted by sectors and view their corresponding stock prices on the app's interface. The app is built using Python's Streamlit library.
* **Python libraries:** streamlit, pandas, io, base64, matplotlib, seaborn, yfinance
* **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/Nasdaq-100), [yfinance](https://pypi.org/project/yfinance/)
""")

#Header for sidebar
st.sidebar.header('Selected Industries')


@st.cache_data
#Method for scraping data
def webScraper():
    df=pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')[4]
    return df
nasdaq_data = webScraper()


#Unique sectors in Nasdaq-100
unique_sectors_sorted = sorted(nasdaq_data['GICS Sector'].unique())

selected_sectors = nasdaq_data[(nasdaq_data['GICS Sector'].isin(st.sidebar.multiselect('GICS Sector', unique_sectors_sorted, unique_sectors_sorted)))]

st.header('Companies in Selected Sector/s')

st.dataframe(selected_sectors)


#Method to download the data as a csv file
def csvDownloader(df):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    b64 = base64.b64encode(buffer.getvalue().encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="Nasdaq-100.csv">Download CSV File</a>'
    return href
#Display data dimensions
st.write(str(selected_sectors.shape[0]) + ' rows × ' + str(selected_sectors.shape[1]) + ' columns')
#Downloading csv file
st.markdown(csvDownloader(selected_sectors), unsafe_allow_html=True)


#Download stock price data from yfinance
data=yf.download (tickers=list(selected_sectors[:15].Ticker), period="ytd" , group_by='ticker')

#Helper method to visualize stock prices
def visualize (ticker):
    stock= pd.DataFrame(data[ticker].Close)
    stock['Date']=stock.index
    fig=plt.figure(figsize= (7, 5))
    sns.lineplot(data=stock)
    plt.title(ticker + ' Stock Price Chart')
    plt.xlabel("Date")
    plt.ylabel("Closing Price")
    return st.pyplot(fig)
    

num_companies = st.sidebar.slider('Number of Companies to View Charts', 1, 10)

#Visualizing stock price
if st.button('View Charts'):
    st.header('Stock Closing Price (YTD)')
    tickers = list(selected_sectors.Ticker)[:num_companies]
    for ticker in tickers:
        visualize(ticker)
