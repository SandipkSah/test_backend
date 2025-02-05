from quart import Blueprint, request, jsonify
import tempfile
import pandas as pd
import PyPDF2
import openai
import json
import os
import base64
import requests
from bs4 import BeautifulSoup

OPENAI_KEY =  os.getenv('OPENAI_KEY')


GPT_analysis_blueprint = Blueprint('document_analysis', __name__)

# def download_save_annual_report(ticker):

#     sec_report_urls_list_file = "cik_report_urls.csv"
#     df = pd.read_csv(sec_report_urls_list_file)
    
    
#     # Filter the DataFrame to find the row with the matching ticker
#     report_row = df.loc[df['ticker'].str.lower() == ticker.lower()]
    
#     if not report_row.empty:
#         # Extract the URL from the filtered DataFrame
#         url = report_row['report_url'].iloc[0]
        
#         # Code to download and save the annual report can be added here
#         # For example, using requests or another library to download the file
        
#     else:
#         print(f"No report found for ticker: {ticker}")
#         return -1

#     # Download the PDF file
#     response = requests.get(url)
    
#     # Check if the request was successful
#     if response.status_code == 200:
#         file_data = response.content
        
#         # Create a temporary file
#         file_name = f'{ticker}_2023.pdf'
#         temp_file_path = os.path.join(tempfile.gettempdir(), file_name)
        
#         # Save the PDF file to the temporary file
#         with open(temp_file_path, 'wb') as temp_file:
#             temp_file.write(file_data)
        
#         return temp_file_path
#     else:
#         raise Exception(f"Failed to download PDF from {url}. Status code: {response.status_code}")
        


def download_extract_text_annual_report(ticker):
    # Load the CSV file into a pandas DataFrame
    sec_report_urls_list_file = "cik_report_urls.csv"
    try:
        df = pd.read_csv(sec_report_urls_list_file)
    except FileNotFoundError:
        return f"Error: The file '{sec_report_urls_list_file}' was not found."
    except pd.errors.EmptyDataError:
        return f"Error: The file '{sec_report_urls_list_file}' is empty."
    except Exception as e:
        return f"An unexpected error occurred while reading the file: {e}"

    print(f"Processing ticker: {ticker}")
    
    # Filter the DataFrame to find the row with the matching ticker
    matching_row = df.loc[df['ticker'].str.lower() == ticker.lower()]
    
    if not matching_row.empty:
        report_url = matching_row['report_url'].iloc[0]
        print(f"Found URL: {report_url}")
        
        headers = {
            "User-Agent": "Essencif.AI_app - Essencif.AI (sandip.sah@calcolution.com)"
        }

        try:
            # Download the HTML content with headers
            response = requests.get(report_url, headers=headers)
            response.raise_for_status()  # Check if the request was successful
        except requests.exceptions.RequestException as e:
            return f"Error: Failed to retrieve the report. Details: {e}"
        
        # Parse HTML content and extract text
        soup = BeautifulSoup(response.content, 'html.parser')
        extracted_text = soup.get_text()
        
        return extracted_text
    else:
        return f"No report found for ticker: {ticker}"



def convert_to_expected_types(prompt):
    converted_prompt = {}
    for key, value in prompt.items():
        if key == 'max_tokens' or key == 'n':
            converted_prompt[key] = int(value)
        elif key == 'temperature' or key == 'top_p' or key == 'presence_penalty' or key == 'frequency_penalty':
            converted_prompt[key] = float(value)
        elif key == 'stream':
            converted_prompt[key] = bool(value)
        elif key == 'messages' and isinstance(value, str):
            converted_prompt[key] = json.loads(value)
        else:
            # Default to keeping it as a string
            converted_prompt[key] = str(value)
    return converted_prompt

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
        return text


def summarize_text_document(text, parameter, context):
    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": parameter['Prompt'] + text}
    ]

    client = openai.OpenAI(api_key=OPENAI_KEY)
    response = client.chat.completions.create(
        model=parameter['Engine'],
        messages=messages,
        # max_tokens=parameter['Max_tokens'],
        temperature=parameter['temperature'],
        top_p=parameter['top_p'],
        n=parameter['n'],
        stream=parameter['stream'],
        presence_penalty=parameter['presence_penalty'],
        frequency_penalty=parameter['frequency_penalty'],
        user=parameter['user']
    )
    return response.choices[0].message.content.strip()

def summarize_text_annual_report(text, parameter, context):
    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": parameter['Prompt'] + text}
    ]

    client = openai.OpenAI(api_key=OPENAI_KEY)
    response = client.chat.completions.create(
        model=parameter['Engine'],
        messages=messages,
        # max_tokens=parameter['Max_tokens'],
        temperature=parameter['temperature'],
        top_p=parameter['top_p'],
        n=parameter['n'],
        stream=parameter['stream'],
        presence_penalty=parameter['presence_penalty'],
        frequency_penalty=parameter['frequency_penalty'],
        user=parameter['user']
    )
    return response.choices[0].message.content.strip()

def summarize_text_website(link, parameter, context):
    # messages = [
    #     {"role": "system", "content": context},
    #     {"role": "user", "content": parameter['Prompt']}
    # ]

    # client = openai.OpenAI(api_key=OPENAI_KEY)
    # response = client.chat.completions.create(
    #     model=parameter['Engine'],
    #     messages=messages,
    #     # max_tokens=parameter['Max_tokens'],
    #     temperature=parameter['temperature'],
    #     top_p=parameter['top_p'],
    #     n=parameter['n'],
    #     stream=parameter['stream'],
    #     presence_penalty=parameter['presence_penalty'],
    #     frequency_penalty=parameter['frequency_penalty'],
    #     user=parameter['user']
    # )
    # return response.choices[0].message.content.strip()
    return f"this is yet to be implemented,the parameters passed are  {link}, {context} and prompts"

def summarize_text_internet(parameter, context):
    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": parameter['Prompt']}
    ]

    client = openai.OpenAI(api_key=OPENAI_KEY)
    response = client.chat.completions.create(
        model=parameter['Engine'],
        messages=messages,
        # max_tokens=parameter['Max_tokens'],
        temperature=parameter['temperature'],
        top_p=parameter['top_p'],
        n=parameter['n'],
        stream=parameter['stream'],
        presence_penalty=parameter['presence_penalty'],
        frequency_penalty=parameter['frequency_penalty'],
        user=parameter['user']
    )
    return response.choices[0].message.content.strip()




@GPT_analysis_blueprint.route('/api/document_analysis', methods=['POST'])
async def document_analysis():
    # Assuming JSON data is sent for Prompt, Context, and the base64-encoded file
    data = await request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    # Accessing Prompt and Context
    Prompt = data.get('prompt')
    Context = data.get('context')
    # analysis_type = data.get('analysis_type')
    analysis_type = data.get('analysis_type')

    if (analysis_type == "document"):
        base64_file = data.get('pdf_file')
        file_name = data.get('file_name')
        if not base64_file or not file_name:
            return jsonify({"error": "PDF file data is required"}), 400

        # Decode the base64 file back to binary
        try:
            file_data = base64.b64decode(base64_file)  # Assuming data URL format
        except (TypeError, ValueError, IndexError) as e:
            return jsonify({"error": "Invalid base64 file data"}), 400

        # Save the file to a temporary location
        temp_file_path = os.path.join(tempfile.gettempdir(), file_name)
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(file_data)

        # Assuming `Prompt` is a JSON string that needs to be converted to a dictionary
        try:
            if isinstance(Prompt, str):
                Prompt = json.loads(Prompt)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format for Prompt"}), 400

        # Convert Prompt values to the expected types if needed
        Prompt = convert_to_expected_types(Prompt)

        # Extract text from PDF (assuming read_pdf function exists)
        pdf_text = read_pdf(temp_file_path)
        pdf_text = pdf_text[:500000]  # Limiting the length of text


        # Run the summary function
        response = summarize_text_document(pdf_text, Prompt, Context)
        return jsonify({"data": response})

    elif (analysis_type == "website"):
        link = data.get('link')
        # Assuming `Prompt` is a JSON string that needs to be converted to a dictionary
        try:
            if isinstance(Prompt, str):
                Prompt = json.loads(Prompt)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format for Prompt"}), 400

        # Convert Prompt values to the expected types if needed
        Prompt = convert_to_expected_types(Prompt)

        # Run the summary function
        response = summarize_text_website( link, Prompt, Context)
        return jsonify({"data": response})

    elif (analysis_type == "gpt_knowledge"):

        # Assuming `Prompt` is a JSON string that needs to be converted to a dictionary
        try:
            if isinstance(Prompt, str):
                Prompt = json.loads(Prompt)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format for Prompt"}), 400

        # Convert Prompt values to the expected types if needed
        Prompt = convert_to_expected_types(Prompt)

        # Run the summary function
        response = summarize_text_internet( Prompt, Context)
        return jsonify({"data": response})

    elif (analysis_type == "sec_filing"):

        # Assuming `Prompt` is a JSON string that needs to be converted to a dictionary
        try:
            if isinstance(Prompt, str):
                Prompt = json.loads(Prompt)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format for Prompt"}), 400

        try:
            ticker = data.get('company_name')
            text_from_html = download_extract_text_annual_report(ticker)
            text_from_html = text_from_html[:500000]  # Limiting the length of text
        except Exception as error :
            print("Something went wrong trying to access Annual report",error)
            return jsonify({"data":"something went wrong trying to access annual report from Sec"})

        # Convert Prompt values to the expected types if needed
        Prompt = convert_to_expected_types(Prompt)

        # Run the summary function
        response = summarize_text_annual_report( text_from_html, Prompt, Context)
        return jsonify({"data": response})

    return jsonify({"data":"something went wrong"})
