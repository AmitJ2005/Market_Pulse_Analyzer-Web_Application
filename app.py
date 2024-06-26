import pandas as pd
import yfinance as yf
from flask import Flask, render_template, request, jsonify, send_from_directory
import json

app = Flask(__name__)
df = pd.DataFrame()
stock_symbol = ''
stock_ticker = None
result_info = None
stock_information = None

def initialize_ticker(stock_symbol):
    global stock_ticker
    stock_ticker = yf.Ticker(stock_symbol)

def stock_info():
    global stock_ticker
    try:
        data = {
            'Income_Statement': stock_ticker.income_stmt.to_html(),
            'Quarterly_Statement': stock_ticker.quarterly_income_stmt.to_html(),
            'Balance_Sheet': stock_ticker.balance_sheet.to_html(),
            'Quarterly_Balance': stock_ticker.quarterly_balance_sheet.to_html(),
            'Cashflow': stock_ticker.cashflow.to_html(),
        }
        return data
    except Exception as e:
        return f"Error fetching stock info for {stock_symbol}: {e}"
        
def fetch_info():
    global stock_ticker
    try:
        company_info = stock_ticker.info
        general_info = {
            "Company Name": company_info.get("longName", ""),
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
            "share in Market": company_info.get("floatShares", ""),
            "Total Share in Company": company_info.get("sharesOutstanding", ""),
            "enterpriseValue": company_info.get("enterpriseValue", ""),
        }
        company_officers = []
        for officer in company_info.get("companyOfficers", []):
            officer_info = {
                "Name": officer.get("name", ""),
                "Age": officer.get("age", ""),
                "Position": officer.get("title", "")
            }
            company_officers.append(officer_info)

        general_info["companyOfficers"] = company_officers
        return general_info
    except Exception as e:
        print(f"Error fetching stock information for {stock_symbol}: {e}")
        return None

def fetch_historical_data():
    global stock_ticker
    try:
        data = stock_ticker.history(period='max')
        return data
    except Exception as e:
        print(f"Error fetching historical data for {stock_symbol}: {e}")
        return None

def preprocess_data(data):
    if "Adj Close" in data.columns:
        data = data.drop(columns=["Adj Close"])
    data = data.round(2)
    return data

def handle_selected_stock(selected_stock):
    global df
    global stock_symbol
    global result_info
    global stock_information

    try:
        with open('stock_names.json', 'r') as f:
            stock_symbols = json.load(f)
        stock_symbol = stock_symbols.get(selected_stock)

        if stock_symbol is None:
            print(f"No symbol found for stock: {selected_stock}")
            return None, None

        initialize_ticker(stock_symbol)
        stock_information = stock_info()
        result_info = fetch_info()
        df = fetch_historical_data()
        if df is not None:
            df = preprocess_data(df)
        else:
            print("Failed to fetch or preprocess data.")
        return result_info, stock_information
    except Exception as e:
        print(f"Error fetching stock symbol for {selected_stock}: {e}")
        return None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')

@app.route('/login')
def login():
    return render_template('Login.html')

@app.route('/stock_names.json')
def get_stock_names():
    return send_from_directory(app.root_path, 'stock_names.json')

@app.route('/submit_selected_stock', methods=['POST'])
def submit_selected_stock():
    global result_info
    global stock_information
    
    data = request.get_json()
    selected_stock = data.get('selectedStock', '')
    result_info, stock_information = handle_selected_stock(selected_stock)
    if result_info and stock_information:
        return jsonify({'message': 'Selected stock received successfully'})
    else:
        return jsonify({'message': 'Failed to process selected stock'}), 500

@app.route('/visualize_data')
def visualize_data():
    global df
    global result_info
    global stock_information

    # First visualization
    if df is None or df.empty:
        error_message = "No data available for visualization"
        print(error_message)
        return jsonify({'error': error_message}), 400

    df.index = pd.to_datetime(df.index)
    labels = df.index.strftime('%Y-%m-%d').tolist()

    try:
        data = df['Close'].tolist()
    except KeyError:
        error_message = "Error: 'Close' column not found in DataFrame."
        print(error_message)
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
                           data_monthly=result_df.to_dict('records'), data_yearly=result_df_yearly.to_dict('records'),
                           result_info=result_info, stock_information=stock_information)

if __name__ == '__main__':
    app.run(debug=True)