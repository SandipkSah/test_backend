from app.ormModels.rating import Rating
from app.utils.pointHandler import grant_points


"""
Saves a rating for a document for a user
    
Args:
    user_id (str): ID of the user
    document_id (str): ID of the document
    rating (float): Amount of points to give
    
Returns:
    The update object with message what action was taken
"""
async def saveRating(user_id: str, document_id: str, rating: float):
    try:
        existing_rating = await Rating.filter(user_id=user_id, qdrant_id=document_id).first()

        if existing_rating:
            existing_rating.rating = rating
            await existing_rating.save()  
            return {
                "type": "update",
                "rating": {
                    "user_id": existing_rating.user_id,
                    "qdrant_id": existing_rating.qdrant_id,
                    "rating": existing_rating.rating
                }
            }
        else:
            rating_instance = await Rating.create(
                user_id=user_id,
                qdrant_id=document_id,
                rating=rating
            )
            await grant_points(user_id, 10)
            return {
                "type": "created",
                "rating": {
                    "user_id": rating_instance.user_id,
                    "qdrant_id": rating_instance.qdrant_id,
                    "rating": rating_instance.rating
                }
            }
    except Exception as e:
        raise RuntimeError(f"Failed to save or update rating: {str(e)}")

"""
Gets all ratings a user did
    
Args:
    user_id (str): ID of the user
    
Returns:
   All the ratings the user did as an array
"""
async def getUserRatings(user_id: str):
    try:
        ratings = await Rating.filter(user_id=user_id).all()

        if not ratings:
            return [] 

        ratings_data = [
            {
                "user_id": rating.user_id,
                "qdrant_id": rating.qdrant_id,
                "rating": rating.rating
            }
            for rating in ratings
        ]
        return ratings_data
    except Exception as e:
        raise RuntimeError(f"Failed to save or update rating: {str(e)}")

"""
Gets the overall rating of a document based on all user ratings
    
Args:
    qdrant_id (str): The ID of the document
    
Returns:
   The float value rounded to two decimals for the document or undefined if no ratings exist
"""
async def getDocumentRating(qdrant_id: str):
    try:
        ratings = await Rating.filter(qdrant_id=qdrant_id).all()
        # No Ratings available
        if not ratings:
            return None
    
        total_rating = sum(rating.rating for rating in ratings)
        average_rating = total_rating / len(ratings)

        return round(average_rating, 2) 
    
    except Exception as e:
        raise RuntimeError(f"Failed to calculate average rating: {str(e)}")