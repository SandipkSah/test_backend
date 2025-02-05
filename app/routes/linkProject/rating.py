from quart import Blueprint, request, jsonify
from app.utils.ratingHandler import saveRating, getUserRatings, getDocumentRating

rating_blueprint = Blueprint('rating', __name__)

@rating_blueprint.route('/api/rating', methods=['POST'])
async def create_or_update_rating():
    """
    Route to save or update a rating for a qdrant entry
    """
    try:
        data = await request.get_json()

        if not data or 'document_id' not in data or 'rating' not in data or 'user_id' not in data:
            return jsonify({"error": "Invalid JSON data or missing fields (document_id, rating, user_id)."}), 400

        if not (0 <= data['rating'] <= 5):
            return jsonify({"error": "Rating must be a number between 1 and 5."}), 400
        
        
        response = await saveRating(user_id=data['user_id'], document_id=data['document_id'], rating=data['rating'])
        print(response)
        
    
        if response["type"] == "update":
            return jsonify({
                "message": "Rating updated successfully",
                "rating:": response["rating"]
            }), 200
        else:
            return jsonify({
                "message": "Rating saved successfully",
                "rating:": response["rating"]
            }), 201

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@rating_blueprint.route('/api/rating', methods=['GET'])
async def get_user_ratings():
    """
    Route to get all ratings for a user_id.
    """
    try:
        user_id = request.args.get('user_id') 

        if not user_id:
            return jsonify({"error": "user_id parameter is required"}), 400

        ratings_data = await getUserRatings(user_id=user_id)
        return jsonify(ratings_data), 200 

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500