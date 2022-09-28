import json
from unittest.mock import patch

import pytest
from exampleco.models.database.services import Service

from .conftest import db_config

test_data_list = [
    {"name": "Test Service 1", "price": 22.22, "description": "Test Description 1"},
    {"name": "Test Service 2", "price": 32.22, "description": "Test Description 2"},
    {"name": "Test Service 3", "price": 42.22, "description": "Test Description 3"},
]


@pytest.fixture()
def create_services(db_session):
    instances = []
    for data in test_data_list:
        instance = Service(**data)
        instances.append(instance)
        db_session.add(instance)
    db_session.commit()
    yield
    for instance in instances:
        db_session.delete(instance)
    db_session.commit()


@patch("exampleco.models.database.get_db_config", return_value=db_config)
def test_get_services(mock_get_db_config, create_services):
    from exampleco.api.services import get_all_services

    response = get_all_services({}, None)
    body = json.loads(response["body"])
    assert len(body) == len(test_data_list)
    for actual, expected in zip(sorted(body, key=lambda x: x["id"]), test_data_list):
        assert actual["name"] == expected["name"]
        assert actual["description"] == expected["description"]
        assert actual["price"] == expected["price"]


@patch("exampleco.models.database.get_db_config", return_value=db_config)
def test_get_service(mock_get_db_config, create_services, db_session):
    from exampleco.api.services import get_service

    service = db_session.query(Service).first()
    response = get_service({"pathParameters": {"pk": service.id}}, None)
    body = json.loads(response["body"])

    assert body["name"] == service.name
    assert body["description"] == service.description
    assert body["price"] == service.price


@patch("exampleco.models.database.get_db_config", return_value=db_config)
def test_get_service_does_not_exist(mock_get_db_config, create_services):
    from exampleco.api.services import get_service

    response = get_service({"pathParameters": {"pk": "BBBCCCDDD"}}, None)
    body = json.loads(response["body"])

    assert body["error"] == "Service with id BBBCCCDDD does not exist."
