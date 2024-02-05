import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from yahooquery import search
import plotly.express as px
import io
import base64

# Rest of your code...


app = Flask(__name__)

# Global variable to store the DataFrame
df = pd.DataFrame()

# Define a global variable to store the selected stock
selected_stock = ''

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

    # Update the global DataFrame with the sample data
    global df
    df = df

    data = request.get_json()
    selected_stock = data.get('selectedStock', '')

    # Process the selected stock as needed
    print(f'Selected stock: {selected_stock}')

    # Fetch stock symbol based on the selected stock
    try:
        result = search(selected_stock)

        if result['quotes']:
            # Take the first stock symbol from the search results
            stock_symbol = result['quotes'][0]['symbol']
            print(f"Stock symbol for {selected_stock}: {stock_symbol}")

            # Fetch historical data using yfinance
            data = yf.download(stock_symbol, period='max')
            df = data.reset_index()

            # Convert the index to datetime
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)

            # Add the following lines to ensure the 'Date' column is a DatetimeIndex
            df.index = pd.DatetimeIndex(df.index)
            df.index.name = 'Date'

            # preprocessing the data
            df= df.drop(columns=["Adj Close"])
            df=df.round(2)
            df['Daily_Price_Change'] = df['Close'] - df['Open']
            df['Daily_Price_Range'] = df['High'] - df['Low']
            df['Day Of Week'] = df.index.day_name()
            df['Direction'] = df.apply(lambda row: 'Positive' if (row['Open'] - row['Close']) < 0 else 'Negative',
                                           axis=1)
            df['Percentage Change'] = df.apply(
                lambda row: f"{round((row['Close'] - row['Open']) / row['Open'] * 100, 1)}%", axis=1)
            df['Day'] = df.index.day
            df['Month'] = df.index.month
            df['Year'] = df.index.year
            df = df.round(2)

            # Display the historical data
            print(df.head(10))

        else:
            # Handle the case where no stock symbol is found
            print(f"No stock symbol found for {selected_stock}")
    except Exception as e:
        print(f"Error fetching stock symbol for {selected_stock}: {e}")

    # You can send a response back to the frontend if needed
    return jsonify({'message': 'Selected stock received successfully'})

# Visualization route to generate and display plots
@app.route('/visualize_data')
def visualize_data():
    global df

    if 'Close' in df.columns:
        fig = px.line(df, x=df.index, y='Close', title='Stock Prices Over Time')
    else:
        print("Error: 'Close' column not found in DataFrame.")

    # Analysis 1: Same Month for Every Year - Positive or Negative Index
    target_month = 2
    result_data_same_month = []

    for year in df.index.year.unique():
        target_data = df[(df.index.year == year) & (df.index.month == target_month)]

        if not target_data.empty:
            first_day_high = target_data.iloc[0]['Open']
            last_day_low = target_data.iloc[-1]['Close']

            result_data_same_month.append({
                'Year': year,
                'First_High': first_day_high,
                'Last_Low': last_day_low,
                'Month_range': last_day_low - first_day_high,
                'Direction': 'Positive' if (last_day_low - first_day_high) > 0 else 'Negative',
                '-%-Change': f"{round((last_day_low - first_day_high) / first_day_high * 100, 1)}%"
            })

    result_df_same_month = pd.DataFrame(result_data_same_month,
                                        columns=['Year', 'First_High', 'Last_Low', 'Month_range', 'Direction',
                                                 '- %-Change'])

    # Count the occurrences of each unique value in the 'Direction' column for Analysis 1
    direction_counts_same_month = result_df_same_month['Direction'].value_counts()

    # Define colors for positive and negative values for Analysis 1
    colors_same_month = ['red' if label == 'Negative' else 'green' for label in direction_counts_same_month.index]

    # Plotting the bar plot with specified colors for Analysis 1
    plt.bar(direction_counts_same_month.index, direction_counts_same_month.values, color=colors_same_month)

    # Adding labels and title for Analysis 1
    plt.xlabel('Status')
    plt.ylabel('Count')
    plt.title('Same Month for Every Year - Positive or Negative Index')

    # Save the plot to a BytesIO object for Analysis 1
    buffer_same_month = io.BytesIO()
    plt.savefig(buffer_same_month, format='png')
    buffer_same_month.seek(0)

    # Encode the plot as base64 for embedding in HTML for Analysis 1
    plot_base64_same_month = base64.b64encode(buffer_same_month.read()).decode('utf-8')

    # Close the buffer for Analysis 1
    buffer_same_month.close()

    plt.close('all')

    # Save the Plotly plot as an HTML string for the line chart
    plot_html = fig.to_html(full_html=False)


    # Analysis 2: 2005-2024 Market - Positive or Negative Index
    result_data_yearly = []

    for year in df.index.year.unique():
        year_data = df[df.index.year == year]

        if not year_data.empty:
            first_day_high = year_data.iloc[0]['Open']
            last_day_low = year_data.iloc[-1]['Close']

            result_data_yearly.append({
                'Year': year,
                'First_High': first_day_high,
                'Last_Low': last_day_low,
                'Year_range': last_day_low - first_day_high,
                'Direction': 'Positive' if (last_day_low - first_day_high) > 0 else 'Negative',
                '-%-Change': f"{round((last_day_low - first_day_high) / first_day_high * 100, 1)}%"
            })

    result_df_yearly = pd.DataFrame(result_data_yearly, columns=['Year', 'First_High', 'Last_Low', 'Year_range', 'Direction','- %-Change'])

    # Count the occurrences of each unique value in the 'Direction' column for Analysis 2
    direction_counts_yearly = result_df_yearly['Direction'].value_counts()

    # Define colors for positive and negative values for Analysis 2
    colors_yearly = ['red' if label == 'Negative' else 'green' for label in direction_counts_yearly.index]

    # Plotting the bar plot with specified colors for Analysis 2
    plt.bar(direction_counts_yearly.index, direction_counts_yearly.values, color=colors_yearly)

    # Adding labels and title for Analysis 2
    plt.xlabel('Status')
    plt.ylabel('Count')
    plt.title('2005-2024 Market - Positive or Negative Index')

    # Save the plot to a BytesIO object for Analysis 2
    buffer_yearly = io.BytesIO()
    plt.savefig(buffer_yearly, format='png')
    buffer_yearly.seek(0)

    # Encode the plot as base64 for embedding in HTML for Analysis 2
    plot_base64_yearly = base64.b64encode(buffer_yearly.read()).decode('utf-8')

    # Close the buffer for Analysis 2
    buffer_yearly.close()

    plt.close('all')

    # Save the Plotly plot as an HTML string for the line chart
    plot_html = fig.to_html(full_html=False)

    # Pass the line chart and both bar plots to the HTML template
    return render_template('result.html', df=df, plot_html=plot_html, plot_base64_same_month=plot_base64_same_month,
                           plot_base64_yearly=plot_base64_yearly)


if __name__ == '__main__':
    # Run the Flask app with debug mode
    app.run(debug=True)