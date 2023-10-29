from datetime import datetime, timedelta

from loguru import logger
from pymongo.collection import Collection
from pymongo.command_cursor import CommandCursor
from pymongo.database import Database

from app.schemas.aggregate import RequestAggregateSchema, ResponseAggregateSchema
from app.settings import settings

GROUP_TYPE_FORMATS_MAPPER: dict = {
    "month": "%Y-%m-01T00:00:00",
    "day": "%Y-%m-%dT00:00:00",
    "hour": "%Y-%m-%dT%H:00:00",
}

TIMEDELTA_MAPPER: dict = {
    "month": timedelta(),
    "day": timedelta(),
    "hour": timedelta(hours=1),
}


class SalaryRepo:
    def __init__(self, database):
        self.database: Database = database
        self.collection: Collection = self.database[settings.COLLECTION_NAME]

    def aggregate(self, data: RequestAggregateSchema) -> ResponseAggregateSchema:
        dt_format: str = GROUP_TYPE_FORMATS_MAPPER.get(data.group_type)
        aggregated_results: CommandCursor = self.collection.aggregate([
            {"$match": {"dt": {"$gte": data.dt_from, "$lte": data.dt_upto}}},
            {"$densify": {
                "field": "dt",
                "range": {
                    "step": 1,
                    "unit": data.group_type,
                    "bounds": [
                        data.dt_from,
                        data.dt_upto + TIMEDELTA_MAPPER.get(data.group_type)
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
        for result in aggregated_results:
            response.dataset.append(result.get("total"))
            response.labels.append(datetime.strptime(result.get("_id"), dt_format).isoformat())
        logger.info(response)
        return response
