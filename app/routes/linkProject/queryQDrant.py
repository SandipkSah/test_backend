from quart import Blueprint, request, jsonify
from app.utils.quadrant import query_qdrant
from app.utils.llm import generate_response_from_retrieved_documents
from app.utils.userQuestionHandler import add_requested_question, get_last_three_questions
import os

query_blueprint = Blueprint('query', __name__)
COLLECTION_CHUNK_NAME = os.getenv("COLLECTION_CHUNK", "chunk_collection")
COLLECTION_METADATA_NAME = os.getenv("COLLECTION_METADATA", "metadata_collection")

@query_blueprint.route('/api/query', methods=['POST'])
async def query_qdrant_endpoint():
    """
    Route that based on a query_text queries qdrant for the top hits and generates a response with an LLM-Model
    """
    data = await request.get_json()

    if not data or 'query_text' not in data or 'filters' not in data or 'user_id' not in data:
        return jsonify({"error": "Invalid JSON data or missing query_text or filters or user_id"}), 400
    
    query_text = data['query_text']  # The query the user asked for
    user_id = data['user_id']  # The user who requested the query
    filters = data['filters']  # The filters object that contains the limits and criteria
    print(f"Filters: {filters}")
    
    # Init quadrant and the model

    # Get the top documents from qdrant
    retrieved_docs = await query_qdrant(
        collection_name=COLLECTION_CHUNK_NAME,
        collection_metadata=COLLECTION_METADATA_NAME,
        query_text=query_text,
        filters=filters,
    )
    
    if not retrieved_docs:
         return {"response_text": "Es wurden keine Dokumente gefunden", "documents": []}
    
    # Generate a response using the retrieved documents
    response = await generate_response_from_retrieved_documents(
        query=query_text,
        retrieved_docs=retrieved_docs
    )
    
    await add_requested_question(question=query_text, user_id=user_id, response={"response_text": response, "documents": retrieved_docs}) 
    return {"response_text": response, "documents": retrieved_docs}

@query_blueprint.route('/api/query/historie', methods=['GET'])
async def get_last_questions():
    """
    Returns back the last (maximum 3) queries that the user did prior
    """
    user_id = request.args.get('user_id') 

    if not user_id:
        return jsonify({"error": "user_id parameter is required"}), 400
    
    return await get_last_three_questions(user_id=user_id)
