from actions.pizza_order.connector.create_order import CreateOrderConnector
from actions.base import ActionConfig

def get_connector(config: ActionConfig):
    return CreateOrderConnector(config)
