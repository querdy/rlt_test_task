from aiogram import Router

from app.handlers import salary, command

base_router = Router()
base_router.include_router(command.router)
base_router.include_router(salary.router)
