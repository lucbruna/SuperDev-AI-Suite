from faker import Faker

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