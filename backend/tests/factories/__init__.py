from sqlalchemy.ext.declarative import declarative_base
from faker import Faker
from backend.database.base import Base

fake = Faker()


def create_user_payload():
    return {
        "email": fake.email(),
        "password": "TestPass123!",
        "name": fake.name(),
    }


def create_project_payload():
    return {
        "name": fake.catch_phrase(),
        "description": fake.text(max_nb_chars=200),
    }