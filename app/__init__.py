from quart import Quart
from quart_cors import cors
from dotenv import load_dotenv
from tortoise import Tortoise
from app.ormModels.applicationAdmins import ensure_default_admins
import config
from quart import current_app
import os

app = Quart(__name__)
app.config.from_object(config)
app = cors(app, allow_origin="*")



load_dotenv(override=True)

# Database initialization function
async def init_tortoise():
    await Tortoise.init(
        db_url=current_app.config.get("DB_URL", "sqlite://essencifai"),
        modules={"models": ["app.ormModels.rating", "app.ormModels.points", "app.ormModels.userQuestionHistorie", "app.ormModels.applicationAdmins"]},
    )
    await Tortoise.generate_schemas()
    
    # Ensure default admin entries exist
    await ensure_default_admins()

# Initialize the database (you should now await this in the main async function)
@app.before_serving
async def init():
    await init_tortoise()

# Import blueprints (same as before)
from app.routes.base_routes import base_blueprint
from app.routes.stock_search_routes import stock_search_blueprint
from app.routes.stock_details_routes import stock_details_blueprint
from app.routes.financial_data_routes import financial_data_blueprint
from app.routes.GPT_analysis_routes import GPT_analysis_blueprint
from app.routes.context_prompt_routes import context_prompt_blueprint
from app.routes.prompts_upload_routes import prompt_upload_blueprint
from app.routes.linkProject.queryQDrant import query_blueprint
from app.routes.linkProject.links import link_blueprint
from app.routes.linkProject.rating import rating_blueprint
from app.routes.linkProject.points import point_blueprint
from app.routes.linkProject.adminCheck import adminCheck_blueprint

# Register blueprints (same as before)
app.register_blueprint(base_blueprint)
app.register_blueprint(stock_search_blueprint)
app.register_blueprint(stock_details_blueprint)
app.register_blueprint(financial_data_blueprint)
app.register_blueprint(GPT_analysis_blueprint)
app.register_blueprint(context_prompt_blueprint)
app.register_blueprint(prompt_upload_blueprint)
app.register_blueprint(query_blueprint)
app.register_blueprint(link_blueprint)
app.register_blueprint(rating_blueprint)
app.register_blueprint(point_blueprint)
app.register_blueprint(adminCheck_blueprint)

# CORS header middleware
@app.after_request
async def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == "__main__":
    # app.run(debug=True)
    port = int(os.getenv("PORT", 8000))  # Default to 8000 if PORT is not set
    app.run(host="0.0.0.0", port=port)