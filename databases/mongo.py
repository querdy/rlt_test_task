import pymongo
from pymongo import MongoClient

from app.settings import settings
from databases.repo.salary import SalaryRepo


class Database:
    def __init__(self, url: str):
        self.client: MongoClient = pymongo.MongoClient(url)
        self.salary: SalaryRepo = SalaryRepo(database=self.client[settings.DATABASE_NAME])
