import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template, request, jsonify, send_from_directory
from yahooquery import search
import json

app = Flask(__name__)
# Global variables to store the DataFrame and selected stock
df = pd.DataFrame()
selected_stock = ''
stock_symbol = ''
result_df_same_month = None
result_df_yearly = None
result_info = None


def fetch_info(stock_symbol):
    try:
        # Create a Ticker object for the stock
        stock_ticker = yf.Ticker(stock_symbol)
        # Get company information
        company_info = stock_ticker.info
        general_info = {
            "Company Name": company_info.get("shortName", ""),
            "Industry": company_info.get("industry", ""),
            "Sector": company_info.get("sector", ""),
            "Website": company_info.get("website", ""),
            "longBusinessSummary": company_info.get("longBusinessSummary", ""),
            "Full-Time Employees": company_info.get("fullTimeEmployees", ""),
            "dividendRate": company_info.get("dividendRate", ""),
            "Dividend Yield": company_info.get("dividendYield", ""),
            "beta": company_info.get("beta", ""),
            "volume": company_info.get("volume", ""),
            "marketCap": company_info.get("marketCap", ""),
            "fiftyTwoWeekLow": company_info.get("fiftyTwoWeekLow", ""),
            "fiftyTwoWeekHigh": company_info.get("fiftyTwoWeekHigh", ""),
            "52WeekChange": company_info.get("52WeekChange", ""),
            "twoHundredDayAverage": company_info.get("twoHundredDayAverage", ""),
            "enterpriseValue": company_info.get("enterpriseValue", ""),
            "sharesOutstanding": company_info.get("sharesOutstanding", ""),
            "floatShares": company_info.get("floatShares", ""),
            "heldPercentInsiders": company_info.get("heldPercentInsiders", ""),
            "heldPercentInstitutions": company_info.get("heldPercentInstitutions", ""),
            "impliedSharesOutstanding": company_info.get("impliedSharesOutstanding", ""),
            "bookValue": company_info.get("bookValue", ""),
            "priceToBook": company_info.get("priceToBook", ""),
            "lastSplitFactor": company_info.get("lastSplitFactor", ""),
            "lastDividendValue": company_info.get("lastDividendValue", ""),
            "lastDividendDate": company_info.get("lastDividendDate", ""),
            "shortName": company_info.get("shortName", ""),
            "currentPrice": company_info.get("currentPrice", ""),
            "totalCash": company_info.get("totalCash", ""),
            "ebitda": company_info.get("ebitda", ""),
            "totalDebt": company_info.get("totalDebt", ""),
            "totalRevenue": company_info.get("totalRevenue", ""),
            "debtToEquity": company_info.get("debtToEquity", ""),
            "revenuePerShare": company_info.get("revenuePerShare", ""),
            "grossMargins": company_info.get("grossMargins", ""),
            "freeCashflow": company_info.get("freeCashflow", ""),
            "earningsGrowth": company_info.get("earningsGrowth", ""),
            "revenueGrowth": company_info.get("revenueGrowth", ""),
            "ebitdaMargins": company_info.get("ebitdaMargins", ""),
            "operatingMargins": company_info.get("operatingMargins", ""),
        }
        # Fetch company officers data
        company_officers = []
        for officer in company_info.get("companyOfficers", []):
            officer_info = {
                "Name": officer.get("name", ""),
                "Age": officer.get("age", ""),
                "Position": officer.get("title", ""),
                "Salary": officer.get("totalPay", "")
            }
            company_officers.append(officer_info)

        # Add company officers data to general_info
        general_info["companyOfficers"] = company_officers
        return general_info

    except Exception as e:
        print(f"Error fetching stock information for {stock_symbol}: {e}")
        return None


# Function to fetch historical data using yfinance
def fetch_historical_data(stock_symbol):
    try:
        data = yf.download(stock_symbol, period='max')
        data.reset_index(inplace=True)
        data['Date'] = pd.to_datetime(data['Date'])
        data.set_index('Date', inplace=True)
        return data
    except Exception as e:
        print(f"Error fetching historical data for {stock_symbol}: {e}")
        return None


# Function to preprocess the data
def preprocess_data(data):
    data = data.drop(columns=["Adj Close"])
    data = data.round(2)
    return data


# Function to handle fetching and preprocessing data for selected stock
def handle_selected_stock(selected_stock):
    global df
    global stock_symbol
    global result_info
    # Fetch stock symbol based on the selected stock
    try:
        result = search(selected_stock)
        if result['quotes']:
            stock_symbol = result['quotes'][0]['symbol']
            print(f"Stock symbol for {selected_stock}: {stock_symbol}")
            info = fetch_info(stock_symbol)
            result_info = info  # Store fetched information globally
            # Fetch historical data
            df = fetch_historical_data(stock_symbol)
            if df is not None:
                # Preprocess the data
                df = preprocess_data(df)
            else:
                print("Failed to fetch or preprocess data.")
            return info
        else:
            print(f"No stock symbol found for {selected_stock}")
    except Exception as e:
        print(f"Error fetching stock symbol for {selected_stock}: {e}")


# Route to serve the HTML page
@app.route('/')
def index():
    print("Rendering index.html")
    return render_template('index.html')


@app.route('/stock_names.json')
def get_stock_names():
    # Logic to read and return stock_names.json
    return send_from_directory(app.root_path, 'stock_names.json')


# Route to handle the selected stock and fetch historical data
@app.route('/submit_selected_stock', methods=['POST'])
def submit_selected_stock():
    global selected_stock
    data = request.get_json()
    selected_stock = data.get('selectedStock', '')
    # Handle selected stock
    handle_selected_stock(selected_stock)
    return jsonify({'message': 'Selected stock received successfully'})


# Visualization route to generate and display plots
@app.route('/visualize_data')
def visualize_data():
    global df
    global result_info

    # Prepare data for Chart.js
    labels = df.index.strftime('%Y-%m-%d').tolist()
    data = df['Close'].tolist()
    return render_template('result.html', labels=json.dumps(labels), data=json.dumps(data))


if __name__ == '__main__':
    app.run(debug=True)