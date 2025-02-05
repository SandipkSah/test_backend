from app.ormModels.applicationAdmins import ApplicationAdmins
from tortoise.exceptions import DoesNotExist

async def is_user_admin(user_id: str) -> bool:
    """
    Check if a user_id exists in the ApplicationAdmins table.
    
    Args:
        user_id (str): The user ID to check.
    
    Returns:
        bool: True if the user_id exists, False otherwise.
    """
    try:
        await ApplicationAdmins.get(user_id=user_id)
        return True
    except DoesNotExist:
        return False