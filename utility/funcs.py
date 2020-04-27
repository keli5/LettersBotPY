from tortoise import Tortoise
import json
async def setup():
    await Tortoise.init(
        db_url='sqlite://../lettersbot_data.sqlite3',
        modules={'models': ["models"]}
    )