from datetime import datetime, timedelta, time

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorLatentCommandCursor, AsyncIOMotorCollection, AsyncIOMotorDatabase


from app.schemas.aggregate import RequestAggregateSchema, ResponseAggregateSchema
from app.settings import settings

GROUP_TYPE_FORMATS_MAPPER: dict = {
    "month": "%Y-%m-01T00:00:00",
    "day": "%Y-%m-%dT00:00:00",
    "hour": "%Y-%m-%dT%H:00:00",
}

TIMEDELTA_MAPPER: dict = {
    "month": timedelta(),
    "day": timedelta(days=1),
    "hour": timedelta(hours=1),
}


class SalaryRepo:
    def __init__(self, database):
        self.database: AsyncIOMotorDatabase = database
        self.collection: AsyncIOMotorCollection = self.database[settings.COLLECTION_NAME]

    async def aggregate(self, data: RequestAggregateSchema) -> ResponseAggregateSchema:
        dt_format: str = GROUP_TYPE_FORMATS_MAPPER.get(data.group_type)
        logger.info(f"request: {data}")
        aggregated_results: AsyncIOMotorLatentCommandCursor = self.collection.aggregate([
            {"$match": {"dt": {"$gte": data.dt_from, "$lte": data.dt_upto}}},
            {"$densify": {
                "field": "dt",
                "range": {
                    "step": 1,
                    "unit": data.group_type,
                    "bounds": [
                        data.dt_from,
                        (
                            (data.dt_upto + TIMEDELTA_MAPPER.get(data.group_type))
                            if data.dt_upto.time() == time(hour=0, minute=0, second=0) else data.dt_upto
                        )
                    ]
                }
            }},
            {"$group": {
                "_id": {"$dateToString": {"format": dt_format, "date": "$dt"}},
                "total": {"$sum": "$value"},
            }},
            {"$sort": {"_id": 1}},
        ])
        response: ResponseAggregateSchema = ResponseAggregateSchema(dataset=[], labels=[])
        for result in await aggregated_results.to_list(length=None):
            response.dataset.append(result.get("total"))
            response.labels.append(datetime.strptime(result.get("_id"), dt_format).isoformat())
        logger.info(f"response: {response}")
        return response
