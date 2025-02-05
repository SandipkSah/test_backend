from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import IntegrityError
from quart import current_app

class ApplicationAdmins(Model):
    '''
    People who should be administrator
    '''
    class Meta:
        table = "application_admins"
    
    user_id = fields.CharField(max_length=255, primary_key=True)

    def __repr__(self):
        return f"<ApplicationAdmins(user_id={self.user_id})>"
    
    
async def ensure_default_admins():
    """
    Ensures that the default admin entries exist in the ApplicationAdmins table.
    """
    default_admins = current_app.config.get("DEFAULT_ADMINS", [])
    if not default_admins:
        print("No default admins found in config.")
        return

    for admin_id in default_admins:
        try:
            await ApplicationAdmins.get_or_create(user_id=admin_id)
        except IntegrityError as e:
            print(f"Error adding default admin {admin_id}: {str(e)}")