import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template, request, jsonify, send_from_directory
from yahooquery import search
import plotly.express as px
import plotly.graph_objects as go

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


# Function to generate bar plot and return base64 encoded image
def generate_bar_plot(data, title):
    # Count the occurrences of each unique value in the 'Direction' column
    direction_counts = data['Direction'].value_counts()
    # Define colors for positive and negative values
    colors = ['red' if label == 'Negative' else 'green' for label in direction_counts.index]
    fig = go.Figure(
        data=[go.Bar(x=direction_counts.index, y=direction_counts.values, marker_color=colors)],
        layout=go.Layout(title=title, xaxis=dict(title='Status'), yaxis=dict(title='Count'))
    )
    fig.update_layout(updatemenus=[])
    plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return plot_html

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
    global result_df_same_month
    global result_df_yearly
    global result_info

    # line chart
    fig = px.line(df, x=df.index, y='Close', title='Stock Prices Over Time')
    # Save the Plotly plot as an HTML string for the line chart
    plot_html = fig.to_html(full_html=False)


    # Analysis 1: Same Month for Every Year - Positive or Negative Index
    result_data_same_month = []
    for year in df.index.year.unique():
        target_data = df[(df.index.year == year) & (df.index.month == 2)]
        if not target_data.empty:
            first_day_high = target_data.iloc[0]['Open']
            last_day_low = target_data.iloc[-1]['Close']
            month_range = last_day_low - first_day_high
            direction = 'Positive' if month_range > 0 else 'Negative'
            percent_change = f"{round((last_day_low - first_day_high) / first_day_high * 100, 1)}%"
            result_data_same_month.append({
                'Year': year,
                'High': first_day_high,
                'Low': last_day_low,
                'Month_range': month_range,
                'Direction': direction,
                'Returns': percent_change
            })
    result_df_same_month = pd.DataFrame(result_data_same_month,
                                        columns=['Year', 'High', 'Low', 'Month_range', 'Direction', 'Returns'])
    result_df_same_month = result_df_same_month.round(2)

    # Generate bar plot for Analysis 1
    plot_base64_same_month = generate_bar_plot(result_df_same_month, 'Same Month for Every Year - Positive or Negative Index')


    # Analysis 2: 2005-2024 Market - Positive or Negative Index
    result_data_yearly = []
    for year in df.index.year.unique():
        year_data = df[df.index.year == year]
        if not year_data.empty:
            first_day_high = year_data.iloc[0]['Open']
            last_day_low = year_data.iloc[-1]['Close']
            year_range = last_day_low - first_day_high
            direction = 'Positive' if year_range > 0 else 'Negative'
            percent_change = f"{round((last_day_low - first_day_high) / first_day_high * 100, 1)}%"
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

    # Generate bar plot for Analysis 2
    plot_base64_yearly = generate_bar_plot(result_df_yearly, '2005-2024 Market - Positive or Negative Index')


    return render_template('result.html', plot_html=plot_html, result_df_same_month=result_df_same_month,
                           result_df_yearly=result_df_yearly, plot_base64_same_month=plot_base64_same_month,
                           plot_base64_yearly=plot_base64_yearly, result_info=result_info)


if __name__ == '__main__':
    app.run(debug=True)