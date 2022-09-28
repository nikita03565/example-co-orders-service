import datetime
import json

from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from exampleco.models.database import get_session_maker
from exampleco.models.database.orders import (
    Order,
    OrderSchemaList,
    OrderSchemaDetail,
    OrderStatuses,
)
from exampleco.models.database.services import Service
from exampleco.utils.decorators import handle_exception

WEEK = "THIS_WEEK"
MONTH = "THIS_MONTH"
YEAR = "THIS_YEAR"

session_maker = get_session_maker()
Session = session_maker()


# pylint: disable=unused-argument
@handle_exception
def get_all_orders(event, context):
    """
    List endpoint for orders.

    Returns:
        Returns a list of all orders pulled from the database.
    """

    orders_schema = OrderSchemaList(many=True)
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

    orders_schema = OrderSchemaDetail(many=False)
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
            "body": json.dumps({"error": f"Service with id {service_id} does not exist."}),
        }
        return response
    order = Order(name=name, service_id=service_id)
    Session.add(order)
    Session.commit()

    orders_schema = OrderSchemaDetail(many=False)
    result = orders_schema.dump(order)
    response = {"statusCode": 201, "body": json.dumps(result)}
    return response


@handle_exception
def update_order(event, context):
    """
    Update order endpoint.
    Expects body {"name": string, "service_id": int} and pk in path.

    Returns:
        Returns updated order.
    """
    order_id = event["pathParameters"]["pk"]

    order = Session.query(Order).filter(and_(Order.id == order_id, Order.is_active)).first()
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
                "body": json.dumps({"error": f"Service with id {service_id} does not exist."}),
            }
            return response
        order.service_id = service_id
    if name is not None:
        order.name = name

    Session.commit()

    orders_schema = OrderSchemaDetail(many=False)
    result = orders_schema.dump(order)
    response = {"statusCode": 200, "body": json.dumps(result)}
    return response


@handle_exception
def delete_order(event, context):
    """
    Delete order endpoint.
    Expects pk in path.

    Returns:
        Returns 204 response.
    """
    order_id = event["pathParameters"]["pk"]

    order = Session.query(Order).filter(and_(Order.id == order_id, Order.is_active)).first()
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


@handle_exception
def orders_stats(event, context):
    """
    Endpoint that can be used by the frontend to display the number of created orders over time.
    Expects time-period query parameter with possible values THIS_WEEK, THIS_MONTH, THIS_YEAR.

    Returns:
        Returns number of orders in buckets.
    """
    time_period = event["queryStringParameters"].get("time-period")
    allowed_periods = [WEEK, MONTH, YEAR]

    if time_period not in allowed_periods:
        response = {
            "statusCode": 400,
            "body": json.dumps({"error": f"time-period must be one of {allowed_periods}"}),
        }
        return response
    response_data = {}
    now = datetime.datetime.now()
    if time_period == WEEK:
        group_by_clauses = [
            func.year(Order.created_on),
            func.month(Order.created_on),
            func.dayofmonth(Order.created_on),
            func.hour(Order.created_on),
        ]
        result = (
            Session.query(*group_by_clauses, func.count(Order.id))
            .filter(Order.created_on > now - datetime.timedelta(days=7))
            .group_by(*group_by_clauses)
            .all()
        )
        for row in result:
            year, month, day, hour, count = row
            dtm = datetime.datetime(year=year, month=month, day=day, hour=hour).isoformat()
            response_data[dtm] = count
    if time_period == MONTH:
        group_by_clauses = [
            func.year(Order.created_on),
            func.month(Order.created_on),
            func.dayofmonth(Order.created_on),
        ]
        result = (
            Session.query(*group_by_clauses, func.count(Order.id))
            .filter(Order.created_on > now - datetime.timedelta(days=30))
            .group_by(*group_by_clauses)
            .all()
        )
        for row in result:
            year, month, day, count = row
            dtm = datetime.datetime(year=year, month=month, day=day).isoformat()
            response_data[dtm] = count
    if time_period == YEAR:
        group_by_clauses = [
            func.year(Order.created_on),
            func.month(Order.created_on),
        ]
        result = (
            Session.query(*group_by_clauses, func.count(Order.id))
            .filter(Order.created_on > now - datetime.timedelta(days=365))
            .group_by(*group_by_clauses)
            .all()
        )
        for row in result:
            year, month, count = row
            dtm = datetime.datetime(year=year, month=month, day=1).isoformat()
            response_data[dtm] = count
    response = {"statusCode": 200, "body": json.dumps(response_data)}
    return response
