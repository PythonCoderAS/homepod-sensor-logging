from datetime import datetime, timezone
from os import environ

import databases
import ormar
import sqlalchemy
from asyncpg import DuplicateTableError
from fastapi import FastAPI, HTTPException
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

DB_URL = (
    environ.get("DB_URL", None)
    or "postgresql://homepod_data:homepod_data@localhost:5432/homepod_data"
)
ALLOW_DUMPS = True if environ.get("BAN_DUMPS", None) is None else False

app = FastAPI()
metadata = sqlalchemy.MetaData()
database = databases.Database(DB_URL)


@app.on_event("startup")
async def startup() -> None:
    if not database.is_connected:
        await database.connect()
        try:
            await database.execute(
                str(
                    CreateTable(SensorRecord.Meta.table).compile(
                        dialect=postgresql.dialect()
                    )
                )
            )
        except DuplicateTableError:
            pass


@app.on_event("shutdown")
async def shutdown() -> None:
    if database.is_connected:
        await database.disconnect()


class SensorRecord(ormar.Model):
    class Meta:
        tablename = "records"
        metadata = metadata
        database = database

    recorded_at = ormar.DateTime(
        primary_key=True, timezone=True
    )  # Time recorded at (received by the server)
    temperature_f = ormar.SmallInteger(
        nullable=False, sql_nullable=False
    )  # Temperature in Fahrenheit
    humidity = ormar.SmallInteger(
        nullable=False, sql_nullable=False, minimum=0, maximum=100
    )  # Humidity in percent


@app.get("/")
async def get_records():
    if not ALLOW_DUMPS:
        raise HTTPException(status_code=403, detail="Dumping is not allowed.")
    return await SensorRecord.objects.all()


@app.post("/")
async def post_record(record: SensorRecord.get_pydantic(exclude={"recorded_at"})):
    now = datetime.now(timezone.utc)
    return await SensorRecord.objects.create(**record.dict(), recorded_at=now)


@app.get("/latest")
async def get_latest_record():
    return await SensorRecord.objects.order_by("-recorded_at").first()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host=environ.get("HOST", "0.0.0.0"), port=int(environ.get("PORT", 8000))
    )
