from tortoise import fields
from tortoise.models import Model

class UserQuestion(Model):
    '''
    Model used to save the questions a user asked via the query
    Saves the question and response 
    '''
    class Meta:
        table = "user_questions"
        ordering = ["-created_at"]  
    
    id = fields.IntField(pk=True) 
    user_id = fields.CharField(max_length=255)
    question = fields.TextField()  
    response = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
