from app.settings import settings
from databases.repo.salary import SalaryRepo
from motor.motor_asyncio import AsyncIOMotorClient


class Database:
    def __init__(self, url: str):
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(url)
        self.salary: SalaryRepo = SalaryRepo(database=self.client[settings.DATABASE_NAME])
