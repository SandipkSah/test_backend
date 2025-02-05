from app.ormModels.userQuestionHistorie import UserQuestion


async def add_requested_question(user_id: str, question: str, response: object):
    """
    Adds a question to the historie of questions from a user
    For Sandip: You can adapt the logic here what happens when a question is being added
    
    Args:
        user_id (str): ID of the user
        question (str): The question the user asked
        response (json object): The response with document and server response the user recieved
    
    Returns:
        The question the user asked
    """
    try:
        await UserQuestion.create(user_id=user_id, question=question, response=response)
        count = await UserQuestion.filter(user_id=user_id).count()

        if count > 3:
            # Delete the oldest question (For Sandip: You should remove that the 4th last question is deleted here)
            to_delete = await UserQuestion.filter(user_id=user_id).order_by("created_at").limit(count - 3).values_list("id", flat=True)
            await UserQuestion.filter(id__in=to_delete).delete()
    except Exception as e:
        raise RuntimeError(f"Failed to add_question: {str(e)}")



async def get_last_three_questions(user_id: str):
    """
    Gets the last three questions a user asked
    
    Args:
        user_id (str): ID of the user
    
    Returns:
      the last three questions a user asked
    """
    questions = await UserQuestion.filter(user_id=user_id).order_by("-created_at").limit(3).values_list("question", flat=True)
    return questions
