from quart import Blueprint, jsonify
import pandas as pd
import os

context_prompt_blueprint = Blueprint('context_prompt', __name__)
# Read prompts from Excel
current_env = os.getenv('CURRENT_QUART_ENV', "development")
if (current_env == 'development'):
    excel_file = 'Chat GPT.xlsx'
else:
    # for now it is this way, but it needs to be changed
    #  depending on the location excel database file
    excel_file = '/home/data/Chat GPT.xlsx'



@context_prompt_blueprint.route('/api/contexts', methods=['GET'])
def get_contexts():
    """Retrieves context information from an Excel file."""
    try:
        df_context = pd.read_excel(excel_file, sheet_name="Context")

        # Convert DataFrame to JSON
        context_data = df_context.to_json(orient='records')

        return jsonify({"contexts": context_data})

    except Exception as e:
        print(f"Error occurred while retrieving contexts: {str(e)}")
        return jsonify({"error": f"Failed to get contexts.{str(e)}"}), 500

@context_prompt_blueprint.route('/api/prompts', methods=['GET'])
def get_prompts():
    """Retrieves prompt information from an Excel file."""
    try:
        df_prompt = pd.read_excel(excel_file, sheet_name="Prompts")
        df_prompt = df_prompt[df_prompt['Owner'] == 'Default']
        
        # Convert DataFrame to JSON
        prompt_data = df_prompt.to_json(orient='records')

        return jsonify({"prompts": prompt_data})

    except Exception as e:
        print(f"Error occurred while retrieving prompts: {str(e)}")
        return jsonify({"error": f"Failed to get prompts.{str(e)}"}), 500

@context_prompt_blueprint.route('/api/parameters', methods=['GET'])
def get_parameters():
    """Retrieves prompt information from an Excel file."""
    try:
        df_parameters = pd.read_excel(excel_file, sheet_name="Parameter")
        df_parameters = df_parameters[df_parameters['Owner'] == 'Default']
        
        # Convert DataFrame to JSON
        parameters_data = df_parameters.to_json(orient='records')

        return jsonify({"parameters": parameters_data})

    except Exception as e:
        print(f"Error occurred while retrieving prompts: {str(e)}")
        return jsonify({"error": f"Failed to get prompts.{str(e)}"}), 500
