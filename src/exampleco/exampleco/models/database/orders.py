import enum

from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemySchema
from sqlalchemy import Column, Integer, String, text, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .services import Service
from . import Base
from sqlalchemy.ext.hybrid import hybrid_property


class OrderStatuses(enum.Enum):
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)

    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    service = relationship("Service", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")
    status = Column(
        Enum(OrderStatuses),
        default=OrderStatuses.ACTIVE.value,
        server_default=OrderStatuses.ACTIVE.value,
        nullable=False,
    )

    created_on = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    modified_on = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

    @hybrid_property
    def is_active(self):
        print(self, "self!!!")
        return self.status == OrderStatuses.ACTIVE

    @is_active.expression
    def is_active(cls):
        print(cls, "cls!!!")
        return cls.status == OrderStatuses.ACTIVE

    def __repr__(self) -> str:
        return (
            "<Order(name='{}', status='{}', service_id='{}', created_on='{}')>".format(
                self.name, self.status, self.service_id, self.created_on
            )
        )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    order = relationship("Order", back_populates="order_items")
    created_on = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    modified_on = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

    def __repr__(self) -> str:
        return "<OrderItem(name='{}', order_id='{}', created_on='{}')>".format(
            self.name, self.order_id, self.created_on
        )


class OrderItemSchema(SQLAlchemySchema):
    id = fields.Integer()
    name = fields.String(required=True)
    order_id = fields.Integer(required=True)
    created_on = fields.DateTime()
    modified_on = fields.DateTime()

    class Meta:
        model = OrderItem
        load_instance = True


class OrderSchema(SQLAlchemySchema):
    id = fields.Integer()
    name = fields.String(required=True)
    service_id = fields.Integer(required=True)
    created_on = fields.DateTime()
    modified_on = fields.DateTime()
    order_items = fields.Nested(OrderItemSchema, many=True)

    class Meta:
        model = Order
        load_instance = True
