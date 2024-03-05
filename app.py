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
            "Full-Time Employees": company_info.get("fullTimeEmployees", ""),
            "currentPrice": company_info.get("currentPrice", ""),
            "marketCap": company_info.get("marketCap", ""),
            "averageVolume": company_info.get("averageVolume", ""),
            "totalDebt": company_info.get("totalDebt", ""),
            "totalRevenue": company_info.get("totalRevenue", ""),
            "totalCash": company_info.get("totalCash", ""),
            "freeCashflow": company_info.get("freeCashflow", ""),
            "longBusinessSummary": company_info.get("longBusinessSummary", ""),
        }
        # Fetch company officers data
        company_officers = []
        for officer in company_info.get("companyOfficers", []):
            officer_info = {
                "Name": officer.get("name", ""),
                "Age": officer.get("age", ""),
                "Position": officer.get("title", "")
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
    # First visualization
    global df
    global result_info
    df.index = pd.to_datetime(df.index)
    labels = df.index.strftime('%Y-%m-%d').tolist()
    # Check if 'Close' column is present in df
    if 'Close' in df.columns:
        data = df['Close'].tolist()
    else:
        error_message = "Error: 'Close' column not found in DataFrame."
        print(error_message)
        # Return an appropriate response to the user, or handle the error as needed
        # For example, you can return a JSON response with the error message
        return jsonify({'error': error_message}), 400


    # Second visualization
    result_data = []
    for year in df.index.year.unique():
        for month in range(1, 13):
            target_data = df[(df.index.year == year) & (df.index.month == month)]
            if not target_data.empty:
                first_day_high = target_data.iloc[0]['Open']
                last_day_low = target_data.iloc[-1]['Close']
                month_range = last_day_low - first_day_high
                direction = 'Positive' if month_range > 0 else 'Negative'
                percent_change = round((last_day_low - first_day_high) / first_day_high * 100, 1)
                result_data.append({
                    'Year': year,
                    'Month': month,
                    'High': first_day_high,
                    'Low': last_day_low,
                    'Month_range': month_range,
                    'Direction': direction,
                    'Returns': percent_change
                })
    result_df = pd.DataFrame(result_data,
                             columns=['Year', 'Month', 'High', 'Low', 'Month_range', 'Direction', 'Returns'])
    result_df = result_df.round(2)

    # Third visualization
    result_data_yearly = []
    for year in df.index.year.unique():
        year_data = df[df.index.year == year]
        if not year_data.empty:
            first_day_high = year_data.iloc[0]['Open']
            last_day_low = year_data.iloc[-1]['Close']
            year_range = last_day_low - first_day_high
            direction = 'Positive' if year_range > 0 else 'Negative'
            percent_change = round((last_day_low - first_day_high) / first_day_high * 100, 1)
            result_data_yearly.append({
                'Year': year,
                'High': first_day_high,
                'Low': last_day_low,
                'Year_range': year_range,
                'Direction': direction,
                'Returns': percent_change
            })
    result_df_yearly = pd.DataFrame(result_data_yearly,
                                    columns=['Year', 'High', 'Low', 'Year_range', 'Direction', 'Returns'])
    result_df_yearly = result_df_yearly.round(2)

    return render_template('result.html', labels=json.dumps(labels), data=json.dumps(data),
                           data_monthly=result_df.to_dict('records'), data_yearly=result_df_yearly.to_dict('records')
                            , result_info=result_info)

if __name__ == '__main__':
    app.run(debug=True)