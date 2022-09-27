import json

from exampleco.models.database import Session
from exampleco.models.database.orders import (
    Order,
    OrderSchema,
    OrderStatuses,
)
from exampleco.models.database.services import Service
from exampleco.utils.decorators import handle_exception
from sqlalchemy import and_
from sqlalchemy.orm import joinedload


# pylint: disable=unused-argument
@handle_exception
def get_all_orders(event, context):
    """
    List endpoint for orders.

    Returns:
        Returns a list of all orders pulled from the database.
    """

    orders_schema = OrderSchema(many=True)
    orders = Session.query(Order).filter(Order.is_active)
    results = orders_schema.dump(orders)

    response = {"statusCode": 200, "body": json.dumps(results)}

    return response


# pylint: disable=unused-argument
@handle_exception
def get_order(event, context):
    """
    Detail endpoint for orders.
    Expects order_id in path arguments.

    Returns:
        Returns an order with given id or 404.
    """
    order_id = event["pathParameters"]["pk"]

    orders_schema = OrderSchema(many=False)
    order = (
        Session.query(Order)
        .filter(and_(Order.id == order_id, Order.is_active))
        .options(joinedload(Order.order_items))
        .first()
    )

    if not order:
        response = {
            "statusCode": 404,
            "body": json.dumps({"error": f"order with id {order_id} does not exist."}),
        }
        return response

    result = orders_schema.dump(order)
    response = {"statusCode": 200, "body": json.dumps(result)}

    return response


@handle_exception
def create_order(event, context):
    """
    Create order endpoint.
    Expects body {"name": string, "service_id": int}

    Returns:
        Returns created order.
    """
    body = json.loads(event["body"])
    name = body["name"]
    service_id = body["service_id"]
    service = Session.query(Service).filter(Service.id == service_id).first()
    if not service:
        response = {
            "statusCode": 400,
            "body": json.dumps(
                {"error": f"Service with id {service_id} does not exist."}
            ),
        }
        return response
    order = Order(name=name, service_id=service_id)
    Session.add(order)
    Session.commit()

    orders_schema = OrderSchema(many=False)
    result = orders_schema.dump(order)
    response = {"statusCode": 201, "body": json.dumps(result)}
    return response


@handle_exception
def update_order(event, context):
    """
    Updates order endpoint.
    Expects body {"name": string, "service_id": int} and pk in path.

    Returns:
        Returns updated order.
    """
    order_id = event["pathParameters"]["pk"]

    order = (
        Session.query(Order).filter(and_(Order.id == order_id, Order.is_active)).first()
    )
    if not order:
        response = {
            "statusCode": 404,
            "body": json.dumps({"error": f"order with id {order_id} does not exist."}),
        }
        return response

    body = json.loads(event["body"])
    name = body.get("name")
    service_id = body.get("service_id")
    if service_id is not None:
        service = Session.query(Service).filter(Service.id == service_id).first()
        if not service:
            response = {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": f"Service with id {service_id} does not exist."}
                ),
            }
            return response
        order.service_id = service_id
    if name is not None:
        order.name = name

    Session.commit()

    orders_schema = OrderSchema(many=False)
    result = orders_schema.dump(order)
    response = {"statusCode": 200, "body": json.dumps(result)}
    return response


@handle_exception
def delete_order(event, context):
    """
    Updates order endpoint.
    Expects body {"name": string, "service_id": int} and pk in path.

    Returns:
        Returns updated order.
    """
    order_id = event["pathParameters"]["pk"]

    order = (
        Session.query(Order).filter(and_(Order.id == order_id, Order.is_active)).first()
    )
    if not order:
        response = {
            "statusCode": 404,
            "body": json.dumps({"error": f"order with id {order_id} does not exist."}),
        }
        return response
    order.status = OrderStatuses.DELETED
    Session.commit()
    response = {
        "statusCode": 204,
    }
    return response
