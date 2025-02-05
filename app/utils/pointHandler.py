from app.ormModels.points import UserPoints
from tortoise.exceptions import DoesNotExist
from quart import current_app

async def grant_points(user_id, points):
    """
    Grants points to the user.
    
    Args:
        user_id (str): The ID of the user.
        points (int): The number of points to grant to the user.

    Returns:
        int: The updated points of the user after the operation.

    Raises:
        Exception: If there is any issue while updating or creating user points.
    """
    try:
        user_points, created = await UserPoints.get_or_create(user_id=user_id, defaults={'points': 0})
        
        if not created:
            user_points.points += points    
        await user_points.save() 
        return user_points.points
    
    except Exception as e:
        print(f"Error granting points: {e}")
        raise


async def get_points(user_id):
    """
    Retrieves the points of the user from the database.

    Args:
        user_id (str): The ID of the user whose points are to be retrieved.

    Returns:
        int: The current points of the user. Returns 0 if the user doesn't exist.

    Raises:
        Exception: If there is an issue during the database query.
    """
    try:
        user_points = await UserPoints.get(user_id=user_id)
        return user_points.points 
    
    except DoesNotExist:
        return 0
    
    except Exception as e:
        print(f"Error getting points: {e}")
        raise


def get_customer_tier(points):
    """
    Determines the customer tier based on the user's points.

    Args:
        points (int): The points of the user.

    Returns:
        str: The tier name associated with the user's points.
             Returns "Unknown" if no tier is found.

    Raises:
        KeyError: If the configuration `TIERS` is not set correctly.
    """
    try:
        tiers = current_app.config['TIERS']

        sorted_tiers = sorted(tiers.items(), key=lambda item: item[1], reverse=True)

        for tier, threshold in sorted_tiers:
            if points >= threshold:
                return tier
        
        # If no tier is found, return "Unknown"
        return "Unknown"
    
    except KeyError:
        # If the TIERS config is missing, raise an error
        print("Error: TIERS configuration is missing or invalid.")
        raise