from quart import Blueprint, request, jsonify
from app.utils.quadrant import get_documents, update_qdrant_entry, delete_point_by_id, get_point
import httpx
import os
from app.utils.pointHandler import grant_points

link_blueprint = Blueprint('link', __name__)

COLLECTION_METADATA_NAME = os.getenv("COLLECTION_METADATA", "metadata_collection")
COLLECTION_CHUNK_NAME = os.getenv("COLLECTION_CHUNK", "chunk_collection")
WORKER_URL = os.getenv("WORKER_URL", "localhost:8000")

@link_blueprint.route('/api/links/personal', methods=['GET'])
async def get_links():
    """
    Route that returns entries for a specific userID from Qdrant.
    """
    tippgeber_id = request.args.get('tippgeber_id')

    try:
        documents = await get_documents(COLLECTION_METADATA_NAME, tippgeber_id)
        
        return jsonify({
            "documents": documents,
        }), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
    
@link_blueprint.route('/api/links/all', methods=['GET'])
async def get_all_links():
    """
    Route that returns entries from Qdrant.
    """
    try:
        documents = await get_documents(COLLECTION_METADATA_NAME)
        
        return jsonify({
            "documents": documents,
        }), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# This is being used by the worker who scrapes data and gets all required data for this endpoint
@link_blueprint.route('/api/links', methods=['POST'])
async def add_link():
    """
    Adds an entry to Qdrant
    """
    data = await request.get_json()
    user_id = data.get("user", {}).get("id", "")

    json_payload = {
        "url": data.get("url", ""),
        "title": data.get("title", ""),
        "type": data.get("type", ""),
        "user": {
            "id": user_id,
            "name": data.get("user", {}).get("name", ""),  
        },
    }
 
    try:
        # Call the scraping API using httpx
        async with httpx.AsyncClient() as client:
            response = await client.post("http://" + WORKER_URL + "/scrape", json=json_payload)
            print(response.status_code)
            if response.status_code == 200:
                await grant_points(user_id, 100)
                response_data = response.json()
                return jsonify(response_data), 200
            else:
                return jsonify({"error": f"Scraping API error: {response.text}"}), response.status_code
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@link_blueprint.route('/api/links', methods=['PUT'])
async def update_link():
    """
    Update an element in Qdrant, keeping certain parts of the data intact (like IDs).
    """
    id = request.args.get('id')
    data = await request.get_json()

    try:
        # Fetch existing data from Qdrant
        existing_data = await get_point(COLLECTION_METADATA_NAME, id)
        
        # Ensure that the data exists
        if not existing_data:
            return jsonify({"error": "The item with the provided ID does not exist."}), 404
        
        # Add the updated entry back to Qdrant
        point_id = await update_qdrant_entry(COLLECTION_METADATA_NAME, id, data)
        
        # Return the updated point_id as a response
        return jsonify({"point_id": point_id}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@link_blueprint.route('/api/links', methods=['DELETE'])
async def delete_link():
    """
    Deletes an entry from Qdrant
    """
    id = request.args.get('id')

    try:
        response = await delete_point_by_id(COLLECTION_METADATA_NAME, COLLECTION_CHUNK_NAME, id)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500