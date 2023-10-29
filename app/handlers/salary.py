import json

import pydantic
from aiogram import Router
from aiogram.types import Message

from app.messages.salary import REDUCE_THE_SELECTION, INVALID_QUERY_FORMAT
from app.schemas.aggregate import ResponseAggregateSchema, RequestAggregateSchema
from app.settings import settings
from databases.mongo import Database

router = Router()


@router.message()
async def aggregate_payments_handler(message: Message, db: Database):
    try:
        request_data = RequestAggregateSchema.model_validate_json(message.text)
        aggregated_data: ResponseAggregateSchema = db.salary.aggregate(
            data=request_data
        )
        answer: str = f"{json.dumps(aggregated_data.model_dump())}"
        await message.answer(
            answer if len(answer) < settings.MESSAGE_MAX_LENGTH else REDUCE_THE_SELECTION
        )
    except pydantic.ValidationError:
        await message.answer(INVALID_QUERY_FORMAT)
