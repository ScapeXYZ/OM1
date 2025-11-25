from inputs.base import Sensor
from actions.pizza_order.interface import PizzaOrderInput
from inputs.plugins.pizza_order import get_connector

class PizzaOrder(Sensor):
    def __init__(self):
        super().__init__(
            name="pizza_order",
            input_interface=PizzaOrderInput,
            connector_loader=get_connector
        )
