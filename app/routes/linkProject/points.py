from quart import Blueprint, request, jsonify
from app.utils.pointHandler import get_points, get_customer_tier

point_blueprint = Blueprint('points', __name__)

@point_blueprint.route('/api/points', methods=['GET'])
async def get_user_points():
    """
    Get points and tier of user
    """
    user_id = request.args.get('user_id')

    try:
        points = await get_points(user_id)
        customier_tier = get_customer_tier(points)

        return jsonify({
            "user_id": user_id, 
            "points": points, 
            "tier": customier_tier
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}", "status_code": 500}), 500
