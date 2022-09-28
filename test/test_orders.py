import json
from unittest.mock import patch

import pytest
from exampleco.models.database.orders import Order, OrderItem, OrderStatuses
from exampleco.models.database.services import Service
from .conftest import db_config

test_services_data_list = [
    {"name": "Test Service 1", "price": 22.22, "description": "Test Description 1"},
    {"name": "Test Service 2", "price": 32.22, "description": "Test Description 2"},
    {"name": "Test Service 3", "price": 42.22, "description": "Test Description 3"},
]

test_orders_data_list = [
    {
        "name": "Test Order 1",
        "order_items": [
            {"name": "Test Item 1"},
            {"name": "Test Item 2"},
            {"name": "Test Item 3"},
        ],
    },
    {
        "name": "Test Order 2",
        "order_items": [
            {"name": "Test Item 4"},
        ],
    },
    {
        "name": "Test Order 3",
        "order_items": [
            {"name": "Test Item 5"},
            {"name": "Test Item 6"},
        ],
    },
]


@pytest.fixture()
def create_orders(db_session):
    service_instances = []
    for data in test_services_data_list:
        instance = Service(**data)
        service_instances.append(instance)
        db_session.add(instance)
    db_session.commit()
    order_instances = []
    for data, service in zip(test_orders_data_list, service_instances):
        instance = Order(name=data["name"], service_id=service.id)
        order_instances.append(instance)
        db_session.add(instance)
    db_session.commit()
    order_item_instances = []
    for order, order_data in zip(order_instances, test_orders_data_list):
        for item_data in order_data["order_items"]:
            item_instance = OrderItem(**item_data, order_id=order.id)
            order_item_instances.append(item_instance)
            db_session.add(item_instance)
    db_session.commit()
    yield
    for instance in order_item_instances:
        db_session.delete(instance)
    for instance in order_instances:
        db_session.delete(instance)
    for instance in service_instances:
        db_session.delete(instance)
    db_session.commit()


@patch("exampleco.models.database.get_db_config", return_value=db_config)
def test_get_orders(mock_get_db_config, create_orders):  # pylint: disable=unused-argument
    from exampleco.api.orders import get_all_orders

    response = get_all_orders({}, None)
    body = json.loads(response["body"])
    assert len(body) == len(test_orders_data_list)
    for actual, expected in zip(sorted(body, key=lambda x: x["id"]), test_orders_data_list):
        assert actual["name"] == expected["name"]
        assert "order_items" not in actual


@patch("exampleco.models.database.get_db_config", return_value=db_config)
def test_get_order_does_not_exist(mock_get_db_config, create_orders):  # pylint: disable=unused-argument
    from exampleco.api.orders import get_order

    response = get_order({"pathParameters": {"pk": "AAABBBCCC"}}, None)
    body = json.loads(response["body"])
    assert body["error"] == "order with id AAABBBCCC does not exist."


@patch("exampleco.models.database.get_db_config", return_value=db_config)
def test_get_order(mock_get_db_config, create_orders, db_session):  # pylint: disable=unused-argument
    from exampleco.api.orders import get_order

    order = db_session.query(Order).first()
    response = get_order({"pathParameters": {"pk": order.id}}, None)
    body = json.loads(response["body"])

    assert body["name"] == order.name
    order_items = body["order_items"]
    for actual, expected in zip(
        sorted(order_items, key=lambda x: x["id"]),
        test_orders_data_list[0]["order_items"],
    ):
        assert actual["name"] == expected["name"]


@patch("exampleco.models.database.get_db_config", return_value=db_config)
def test_update_order(mock_get_db_config, create_orders, db_session):  # pylint: disable=unused-argument
    from exampleco.api.orders import update_order

    order = db_session.query(Order).first()
    service = db_session.query(Service).order_by(Service.id.desc()).first()
    payload = {"name": "TEST ORDER 1 NEW NAME!", "service_id": service.id}
    response = update_order({"pathParameters": {"pk": order.id}, "body": json.dumps(payload)}, None)
    body = json.loads(response["body"])
    assert body["name"] == payload["name"]
    assert body["service_id"] == payload["service_id"]
    db_session.refresh(order)
    assert order.name == payload["name"]
    assert order.service_id == payload["service_id"]


@patch("exampleco.models.database.get_db_config", return_value=db_config)
def test_delete_order(mock_get_db_config, create_orders, db_session):  # pylint: disable=unused-argument
    from exampleco.api.orders import delete_order, get_order

    order = db_session.query(Order).first()
    delete_order({"pathParameters": {"pk": order.id}}, None)
    db_session.refresh(order)
    assert order.status == OrderStatuses.DELETED
    response = get_order({"pathParameters": {"pk": order.id}}, None)
    body = json.loads(response["body"])
    assert body["error"] == f"order with id {order.id} does not exist."
