import json
from sqlalchemy.orm import joinedload
from exampleco.models.database import Session
from exampleco.models.database.orders import Order, OrderSchema, OrderItem, OrderItemSchema
from exampleco.utils.decorators import handle_exception

# The read endpoints should be one that lists all the orders and one that describes a single order with all the order items
# pylint: disable=unused-argument
@handle_exception
def get_all_orders(event, context):
    """
    List endpoint for orders.

    Returns:
        Returns a list of all orders pulled from the database.
    """

    orders_schema = OrderSchema(many=True)
    orders = Session.query(Order).all()
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
    order = Session.query(Order).filter(Order.id == order_id).options(joinedload(Order.order_items)).first()

    if not order:
        response = {
            "statusCode": 404,
            "body": json.dumps(
                {"error": f"order with id {order_id} does not exist."}
            ),
        }
        return response

    result = orders_schema.dump(order)
    response = {"statusCode": 200, "body": json.dumps(result)}

    return response
