from tortoise import Tortoise, run_async


async def init():
    await Tortoise.init(
        db_url='sqlite://lettersbot_data.sqlite3',
        modules={'models': ["classes.dbmodels"]}
    )
    # Generate the schema
    await Tortoise.generate_schemas()

run_async(init())
