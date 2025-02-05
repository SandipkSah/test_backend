from quart import Blueprint, jsonify
import pandas as pd
import json

stock_search_blueprint = Blueprint('stock_search', __name__)

stocks_df = pd.read_csv('updated_stocks_list.csv', delimiter=";", encoding='MacRoman')

@stock_search_blueprint.route('/api/search_stocks/<search_query>', methods=['GET'])
def stock_search(search_query):
    search_query_lower = search_query.lower()

    # Handle the case where ISIN might be NaN
    results = stocks_df[
        stocks_df['Name'].str.lower().str.contains(search_query_lower) |
        stocks_df['ISIN'].fillna('').str.lower().str.contains(search_query_lower)
    ]
    results = results[results['ISIN'].notna() & (results['ISIN'] != '')]
    stringified_json = json.dumps(results.to_dict(orient='records'))
    res = json.loads(stringified_json)
    return jsonify(res)
