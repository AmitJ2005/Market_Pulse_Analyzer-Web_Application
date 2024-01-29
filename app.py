from flask import Flask, render_template, request, jsonify, send_from_directory
from yahooquery import search
import yfinance as yf
import pandas as pd

app = Flask(__name__)

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

            # Display the historical data
            print(df)

        else:
            # Handle the case where no stock symbol is found
            print(f"No stock symbol found for {selected_stock}")
    except Exception as e:
        print(f"Error fetching stock symbol for {selected_stock}: {e}")

    # You can send a response back to the frontend if needed
    return jsonify({'message': 'Selected stock received successfully'})

if __name__ == '__main__':
    # Run the Flask app with debug mode
    app.run(debug=True)
