from quart import Blueprint, jsonify, request
import requests
from datetime import datetime, timedelta
import openai
import os

stock_details_blueprint = Blueprint('stock_details', __name__)


ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')

@stock_details_blueprint.route('/api/get_ticker/<isin>', methods=['GET'])
def get_ticker(isin):
    url = f'https://finnhub.io/api/v1/stock/profile2?isin={isin}&token={FINNHUB_API_KEY}'
    response = requests.get(url)
    data = response.json()
    ticker = data.get('ticker')
    if ticker:
        return jsonify({'ticker': ticker})
    else:
        return jsonify({'error': 'Ticker not found for the given ISIN'}), 404



@stock_details_blueprint.route('/api/swot_analysis/<ticker>', methods=['GET'])
def swot_analysis(ticker):
    try:
        # Fetch necessary data
        profile_url = f'https://finnhub.io/api/v1/stock/profile2?symbol={ticker}&token={FINNHUB_API_KEY}'
        profile_response = requests.get(profile_url)
        profile_data = profile_response.json()
        
        financial_url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}'
        financial_response = requests.get(financial_url)
        financial_data = financial_response.json()
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        news_url = f'https://finnhub.io/api/v1/company-news?symbol={ticker}&from={start_date}&to={current_date}&token={FINNHUB_API_KEY}'
        news_response = requests.get(news_url)
        news_data = news_response.json()[:3]

        if profile_response.status_code != 200 or financial_response.status_code != 200 or news_response.status_code != 200:
            return jsonify({"error": "Failed to fetch one or more required data sources"}), 500

        # Prepare the input for SWOT analysis
        swot_input = f"""
        Profile: {profile_data}
        Financials: {financial_data}
        Recent News: {news_data}
        """
        
        # Generate SWOT analysis using OpenAI
        client = openai.OpenAI(api_key=os.getenv('OPENAI_KEY'))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Generate a SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) for the following stock:"},
                {"role": "user", "content": swot_input}
            ]
        )
        swot_analysis = response.choices[0].message.content.strip()

        return jsonify({"swot_analysis": swot_analysis})
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Log the error message
        return jsonify({"error": str(e)}), 500

