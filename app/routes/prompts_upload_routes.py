from quart import Blueprint, request, jsonify
import base64
import io
import pandas as pd
from openpyxl import load_workbook
import os

prompt_upload_blueprint = Blueprint('prompts_upload', __name__)

current_env = os.getenv('CURRENT_QUART_ENV', "development")
if (current_env == 'development'):
    excel_file = 'Chat GPT.xlsx'
else:
    # for now it is this way, but it needs to be changed
    #  depending on the location excel database file
    excel_file = '/home/data/Chat GPT.xlsx'

@prompt_upload_blueprint.route('/api/prompts_upload', methods=['POST'])
def prompts_upload():
    # Assuming JSON data is sent with a base64-encoded Excel file
    data = request.get_json()

    if not data or 'excel_file' not in data:
        return jsonify({"error": "Invalid JSON data or no file provided"}), 400

    try:
        # Decode the base64-encoded file content
        file_content = base64.b64decode(data['excel_file'])
        input_file = io.BytesIO(file_content)

        # Load the uploaded Excel file directly into a new workbook object
        uploaded_wb = load_workbook(input_file)

        # Save the uploaded workbook, replacing the existing file
        uploaded_wb.save(excel_file)
        return jsonify({"message": "Uploaded file replaced the existing file successfully"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
