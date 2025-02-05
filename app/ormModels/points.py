from tortoise import fields
from tortoise.models import Model

class UserPoints(Model):
    '''
    The status points of a user
    '''
    class Meta:
        table = "user_points"
    
    user_id = fields.CharField(max_length=255, primary_key=True)
    points = fields.IntField()

    def __repr__(self):
        return f"<UserPoints(user_id={self.user_id}, points={self.points})>"
