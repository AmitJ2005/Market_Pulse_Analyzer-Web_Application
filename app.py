import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify, send_from_directory
from yahooquery import search
import plotly.express as px
import io
import base64

app = Flask(__name__)
# Global variables to store the DataFrame and selected stock
df = pd.DataFrame()
selected_stock = ''
result_df_same_month = None
result_df_yearly = None


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

    # Fetch stock symbol based on the selected stock
    try:
        result = search(selected_stock)
        if result['quotes']:
            stock_symbol = result['quotes'][0]['symbol']
            print(f"Stock symbol for {selected_stock}: {stock_symbol}")
            # Fetch historical data
            df = fetch_historical_data(stock_symbol)
            if df is not None:
                # Preprocess the data
                df = preprocess_data(df)
            else:
                print("Failed to fetch or preprocess data.")
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
    # Plotting the bar plot with specified colors
    plt.bar(direction_counts.index, direction_counts.values, color=colors)
    # Adding labels and title
    plt.xlabel('Status')
    plt.ylabel('Count')
    plt.title(title)
    # Save the plot to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    # Encode the plot as base64
    plot_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    # Close the buffer
    buffer.close()
    # Close the plot to free memory
    plt.close()
    return plot_base64


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
    global selected_stock
    global result_df_same_month
    global result_df_yearly
    # Check if 'Close' column exists in DataFrame
    if 'Close' not in df.columns:
        return render_template('result.html', error_message="Close column not found in DataFrame")
    # Initialize fig outside the conditional block
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
    return render_template('result.html', df=df, plot_html=plot_html, result_df_same_month=result_df_same_month,
                           result_df_yearly=result_df_yearly, plot_base64_same_month=plot_base64_same_month,
                           plot_base64_yearly=plot_base64_yearly, selected_stock=selected_stock)


if __name__ == '__main__':
    app.run(debug=True)