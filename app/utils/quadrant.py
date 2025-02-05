import numpy as np
import logging
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct, PointIdsList, Filter, FieldCondition, MatchValue, FilterSelector
from app.utils.ratingHandler import getDocumentRating
import os

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
GROUP_BY_PARAMETER = "url"

# Load the connection to QDrant and the Model used for vectoring
try:
    model = SentenceTransformer(os.getenv("MODEL_NAME", "Alibaba-NLP/gte-multilingual-base"), trust_remote_code=True)
    qdrant_client = QdrantClient(host=os.getenv("QDRANT_HOST", "localhost"), port=int(os.getenv("QDRANT_PORT", 6333)))
    logger.info(f"Successfully loaded QDrant and SentenceTransformer")
except Exception as e:
    logger.error(f"Error loading QDrant or SentenceTransformer: {e}")
    raise e




def format_and_validate_data(data: dict):
    """
    Validates and filters input data to ensure it only contains allowed fields.
    
    Args:
        data (dict): The input data to be validated and formatted.
        
    Returns:
        dict: A dictionary containing only the allowed fields from the input data.
        
    Raises:
        ValueError: If the input data is not a dictionary.
    """
    if not isinstance(data, dict):
        raise ValueError("Input data must be a dictionary.")

    allowed_fields = [
        "url",
        "title",
        "name",
        "link_type",
        "summary",
        "co2_score",
        "reduk_score",
        "report_score",
        "sustfin_score",
        "regul_score"
    ]

    validated_data = {field: data.get(field) for field in allowed_fields if field in data}
    return validated_data


async def update_qdrant_entry(collection_name: str, point_id: str, new_data: dict):
    """
    Updates an entry in Qdrant, keeping the existing data intact unless overridden by `new_data`.
    
    Args:
        collection_name (str): The name of the collection to update the point in.
        point_id (str): The ID of the point to update.
        new_data (dict): A dictionary of new data to update the point with.
        
    Returns:
        str: The ID of the updated point.
        
    Raises:
        ValueError: If the point does not exist or if an error occurs during the update.
    """
    try:
        existing_point = await get_point(collection_name, point_id)
        
        # Check if the point exists
        if not existing_point or len(existing_point) == 0:
            raise ValueError(f"Point with ID {point_id} does not exist.")
        
        existing_payload = existing_point[0].payload["metadata"]
                
        updated_payload = {**existing_payload, **new_data}
        send_payload = {"metadata": updated_payload}
        point = PointStruct(id=point_id, vector=np.random.rand(768).tolist(), payload=send_payload) # Random vector because we dont care about the metadata
    
        qdrant_client.upsert(collection_name=collection_name, points=[point])
        return point_id  
        
    except Exception as e:
        raise ValueError(f"An error occurred while updating the point: {str(e)}")


async def query_qdrant(collection_name: str, collection_metadata: str, query_text: str, filters: dict):
    """
    Query Qdrant with filters applied to the metadata collection.
    
    Args:
        collection_name (str): The name of the chunk collection to query.
        collection_metadata (str): The name of the metadata collection to query.
        query_text (str): The query string that will be encoded and used for semantic search.
        filters (dict): A dictionary containing filter conditions such as query limits, category filters, and ratings.
    
    Returns:
        List[dict]: A list of documents that match the query and filters, each containing 'text', 'metadata', 'related_metadata', 
                    'score', and 'user_rating' fields.
        
    Raises:
        Exception: If an error occurs during the query process.
    """
    try:
        # Encode the query text into a vector
        logger.info(f"Encoding query text: {query_text}")
        query_vector = model.encode([query_text])[0].tolist()

        # Filters with fallback values
        query_limit = filters.get('queryLimit', 10) if isinstance(filters.get('queryLimit', 10), int) and 1 <= filters.get('queryLimit', 10) <= 25 else 10
        general_rating = filters.get('generalRating', [0, 5])
        link_types = filters.get('linkTypes', [])
        category_filters = filters.get('categoryFilters', {
            "co2_score": [0, 100],
            "reduk_score": [0, 100],
            "regul_score": [0, 100],
            "report_score": [0, 100],
            "sustfin_score": [0, 100],
        })

        # Building the filter for metadata based on the restrictions
        metadata_filter_query = {
            "must": []
        }

        # Filter for link_type (skip if not set or empty)
        if link_types:
            metadata_filter_query["must"].append({
                "key": "metadata.link_type",
                "match": {"any": link_types}
            })

        # Filters for categories (skip if in range from 0 - 100)
        for category, range_values in category_filters.items():
            if range_values != [0, 100]:
                metadata_filter_query["must"].append({
                    "key": "metadata." + category,
                    "range": {"gte": range_values[0], "lte": range_values[1]}
                })

        # If either filter from above or scoring filter is set, we need to do these steps for filters
        metadata_points = []
        if metadata_filter_query["must"] or general_rating != [0, 5]:
            logger.info("Querying metadata collection with filters.")
            logger.info(metadata_filter_query)

            # Get number of all available points in collection
            collection_info = qdrant_client.get_collection(collection_metadata)
            total_points = collection_info.points_count
            metadata_results = qdrant_client.query_points(
                collection_name=collection_metadata,
                query_filter=metadata_filter_query, # Set filter that was given above
                limit=total_points # Get all points from metadata collection
            )

            metadata_points = {str(point.id): point.payload for point in metadata_results.points} if metadata_results.points else {}

            # Limit the valid ids even more by seeing if ranking is in the range
            if general_rating != [0, 5]:
                min_rating, max_rating = general_rating
                filtered_valid_ids = []
                for valid_id, payload in metadata_points.items():
                    user_rating = await getDocumentRating(valid_id)
                    if user_rating is None or (min_rating <= user_rating <= max_rating):
                        filtered_valid_ids.append(valid_id)
                        payload["user_rating"] = user_rating  # Cache the rating
                valid_ids = filtered_valid_ids
            else:
                valid_ids = list(metadata_points.keys())

            if not valid_ids:
                logger.info("No valid IDs found after applying filters.")
                return []

            query_filter = {
                "must": [
                    {"key": "link_id", "match": {"any": valid_ids}}  
                ]
            }
        else:
            query_filter = {}

        # Query the chunk collection using valid IDs and query vector
        logger.info(f"Querying chunk collection")
        results = qdrant_client.query_points_groups(
            collection_name=collection_name,
            query=query_vector,
            query_filter=query_filter,
            group_by=GROUP_BY_PARAMETER,
            limit=query_limit,
            group_size=1
        )

        # Prepare to store documents with additional metadata
        documents = []

        # Loop through results to fetch additional metadata
        for group in results.groups:
            if not group.hits:
                continue

            # Extract the primary document's data
            chunk_hit = group.hits[0]
            link_id = chunk_hit.payload.get("link_id", "")

            # Retrieve related metadata from preloaded metadata points
            related_metadata = None

            # If metadata_points is empty, we'll fetch metadata from the database using link_id
            if not metadata_points:
                logger.info(f"Fetching metadata for link_id {link_id} since metadata_points is empty.")
                metadata_result = qdrant_client.retrieve(
                    collection_name=collection_metadata,
                    ids=[link_id]
                )
                payload = metadata_result[0].payload
            # The metadata is loaded already from the prior filters, get it there
            else:
                payload = metadata_points[link_id]
              
                
            related_metadata = {
                "id": link_id,
                "metadata": payload.get("metadata", {})
            }
            user_rating = payload.get("user_rating")
            
            # If the rating hasnt been loaded because of no filter, load it at the end here
            if general_rating == [0, 5]:
                user_rating = await getDocumentRating(link_id)

            # Combine primary document and related metadata
            documents.append({
                "id_metadata": related_metadata.get("id") if related_metadata else None,
                "metadata": related_metadata.get("metadata") if related_metadata else {},
                "chunk": chunk_hit.payload.get("chunk", "No content available."),
                "score": chunk_hit.score,
                "user_rating": user_rating
            })

        return documents

    except Exception as e:
        logger.error(f"Error querying Qdrant: {e}")
        raise


async def get_documents(collection_name: str, tippgeberFilter=None):
    """
    Retrieves all documents from a Qdrant collection using the Python client scroll method.
    Supports filtering by a custom filter condition.

    Args:
        collection_name (str): The name of the collection to query.
        tippgeberFilter (str, optional): An optional filter for the `tippgeber_id`.
    
    Returns:
        List[dict]: A list of retrieved documents as dictionaries, with 'id' and 'metadata' fields.
        
    Raises:
        Exception: If an error occurs during the document retrieval.
    """
    try:     
        collection_info = qdrant_client.get_collection(collection_name)
        total_points = collection_info.points_count
        documents = []
        
        if tippgeberFilter:
            result, _ = qdrant_client.scroll(
                collection_name=collection_name,
                limit=total_points,
                scroll_filter=Filter(
                    should=[FieldCondition(
                        key="metadata.user.id", match=MatchValue(value=tippgeberFilter)
                    )],
                ),
                with_payload=True,
                with_vectors=False,  
            )
        else:
            result, _ = qdrant_client.scroll(
                collection_name=collection_name,
                limit=total_points, 
                with_payload=True,
                with_vectors=False,  
            )
        
        for record in result:
            document = {
                "id": record.id,
                "metadata": record.payload.get("metadata", {})
            }
            documents.append(document)
            
        return documents

    except Exception as e:
        logging.error(f"Error in get_documents: {e}", exc_info=True)
        raise


async def delete_point_by_id(collection_metadata_name: str, collection_chunk_name: str, point_id: str):
    """
    Deletes a point from a Qdrant collection based on the point's ID.
   
    Args:
        collection_metadata_name (str): The name of the metadata collection.
        collection_chunk_name (str): The name of the chunk collection.
        point_id (str): The ID of the point to delete.
        
    Returns:
        str: A success message if the deletion is successful.
    
    Raises:
        Exception: If any error occurs during the deletion process.
    """
    try:
        print(f"Deleting point with ID: {point_id}")

        # Fetch the metadata point by ID
        metadata_result = await get_point(collection_metadata_name, point_id)

        # Ensure the metadata point exists
        if not metadata_result or len(metadata_result) == 0:
            raise ValueError(f"Metadata point with ID {point_id} not found.")
        
        # Delete all chunks containing the URL in the payload
        qdrant_client.delete(
            collection_name=collection_chunk_name,
            points_selector=FilterSelector(
            filter=Filter(
                must=[
                    FieldCondition(
                        key="link_id",
                        match=MatchValue(value=point_id),
                        ),
                    ],
                )
            ),
        )
        print(f"Chunks associated with id {point_id} deleted successfully.")

        # Delete the metadata point
        qdrant_client.delete(
            collection_name=collection_metadata_name,
            points_selector=PointIdsList(
                points=[point_id],
            )
        )
        print(f"Metadata point with ID {point_id} deleted successfully.")
        return "Success"
    except Exception as e:
        logging.error(f"Error deleting point with ID {point_id}: {e}", exc_info=True)
        raise


async def get_point(collection_name: str, point_id: str):
    """
    Retrieves a point from the Qdrant collection by ID.
    
    Args:
        collection_name (str): The name of the collection to retrieve the point from.
        point_id (str): The ID of the point to retrieve.
    
    Returns:
        dict: The retrieved point's payload.
        
    Raises:
        Exception: If the point cannot be found or if an error occurs during retrieval.
    """
    try:
        metadata_result = qdrant_client.retrieve(
            collection_name=collection_name,
            ids=[point_id]
        )
        return metadata_result
    except Exception as e:
        logger.error(f"Error retrieving point: {e}")
        raise
