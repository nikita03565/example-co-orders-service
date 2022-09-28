import json

from exampleco.models.database import get_session_maker
from exampleco.models.database.services import Service, ServiceSchema
from exampleco.utils.decorators import handle_exception

session_maker = get_session_maker()
Session = session_maker()
# pylint: disable=unused-argument
@handle_exception
def get_all_services(event, context):
    """
    List endpoint for services.

    Returns:
        Returns a list of all services pulled from the database.
    """

    services_schema = ServiceSchema(many=True)
    services = Session.query(Service).all()
    results = services_schema.dump(services)

    response = {"statusCode": 200, "body": json.dumps(results)}

    return response


# pylint: disable=unused-argument
@handle_exception
def get_service(event, context):
    """
    Detail endpoint for services.
    Expects service_id in path arguments.

    Returns:
        Returns a service with given id or 404.
    """
    service_id = event["pathParameters"]["pk"]

    services_schema = ServiceSchema(many=False)
    service = Session.query(Service).filter(Service.id == service_id).first()

    if not service:
        response = {
            "statusCode": 404,
            "body": json.dumps(
                {"error": f"Service with id {service_id} does not exist."}
            ),
        }
        return response

    result = services_schema.dump(service)
    response = {"statusCode": 200, "body": json.dumps(result)}

    return response
