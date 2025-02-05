from quart import Blueprint, request, jsonify
from app.utils.adminHandler import is_user_admin

adminCheck_blueprint = Blueprint('adminCheck', __name__)

@adminCheck_blueprint.route('/api/adminCheck', methods=['GET'])
async def is_admin():
    """
    Checks if the user is in the admin table and should get admin rights
    Note:   We do not do this via Azure AD B2C because B2C does not natively support loading direct roles of users.
            Since we dont want to modify the Azure AD B2C of Essencify and most likely to only admin is Christian, we treat this as a sort of config file (as database table) 
            to store admins in.
    """
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "Missing 'user_id' parameter"}), 400

    try:
        is_admin = await is_user_admin(user_id)
        return "true" if is_admin else "false"
    
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}", "status_code": 500}), 500