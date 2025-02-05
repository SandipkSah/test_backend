from quart import Blueprint, jsonify
import requests
from datetime import datetime, timedelta
import yfinance as yf
import os


financial_data_blueprint = Blueprint('financial_data', __name__)

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')

@financial_data_blueprint.route('/api/current_price/<ticker>', methods=['GET'])
def get_current_price(ticker):
    url = f'https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}'
    response = requests.get(url)
    data = response.json()
    return jsonify(data)

@financial_data_blueprint.route('/api/recent_news/<ticker>', methods=['GET'])
def get_recent_news(ticker):
    current_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    url = f'https://finnhub.io/api/v1/company-news?symbol={ticker}&from={start_date}&to={current_date}&token={FINNHUB_API_KEY}'
    response = requests.get(url)
    data = response.json()
    return jsonify(data[:10])  # Return only the first 3 news articles

@financial_data_blueprint.route('/api/financial_statements/<ticker>', methods=['GET'])
def get_financial_statements(ticker):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}'
    response = requests.get(url)
    data = response.json()
    return jsonify(data)

@financial_data_blueprint.route('/api/analyst_sentiments/<ticker>', methods=['GET'])
def get_analyst_sentiments(ticker):
    url = f'https://finnhub.io/api/v1/stock/recommendation?symbol={ticker}&token={FINNHUB_API_KEY}'
    response = requests.get(url)
    data = response.json()
    return jsonify(data)

@financial_data_blueprint.route('/api/business_model/<ticker>', methods=['GET'])
def get_business_model(ticker):
    url = f'https://finnhub.io/api/v1/stock/profile2?symbol={ticker}&token={FINNHUB_API_KEY}'
    response = requests.get(url)
    data = response.json()
    return jsonify(data)

@financial_data_blueprint.route('/api/time_series/<ticker>', methods=['GET'])
def get_time_series(ticker):
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        data = stock.history(period="1y")  # Fetch 1 year of historical data
        data = data.reset_index().to_dict(orient='records')
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@financial_data_blueprint.route('/api/total_revenue/<ticker>', methods=['GET'])
def total_revenue(ticker):
    """Retrieves total revenue for a given ticker."""
    yf_ticker = yf.Ticker(ticker)
    financials = yf_ticker.financials.T
    total_revenue = financials["Total Revenue"]
    json_data = total_revenue.to_json(orient='index')
    return json_data

@financial_data_blueprint.route('/api/ebitda/<ticker>', methods=['GET'])
def ebitda(ticker):
    """Retrieves EBITDA for a given ticker."""
    yf_ticker = yf.Ticker(ticker)
    financials = yf_ticker.financials.T
    ebitda = financials["EBITDA"]
    json_data = ebitda.to_json(orient='index')
    return json_data

@financial_data_blueprint.route('/api/balance_sheet/<ticker>', methods=['GET'])
def balance_sheet(ticker):
    """Retrieves balance sheet data for a given ticker."""
    yf_ticker = yf.Ticker(ticker)
    balance_sheet_table = yf_ticker.balancesheet
    json_data = balance_sheet_table.to_json(orient='index')
    return json_data