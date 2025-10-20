import requests
from actions.base import ActionConnector, ActionConfig
from actions.home_assistant.interface import HomeAssistantInput, HomeAssistantOutput


class Webhook(ActionConnector[HomeAssistantInput, HomeAssistantOutput]):
    """Connector for sending commands to Home Assistant via REST API."""

    def __init__(self, config: ActionConfig):
        super().__init__(config)
        self.base_url = "http://localhost:8123/api"
        self.token = "YOUR_LONG_LIVED_ACCESS_TOKEN"

    def connect(self):
        """Optional connection step (required abstract method)."""
        # You can verify connectivity to Home Assistant here.
        # For now, just return True to satisfy the abstract class.
        return True

    def run(self, input_data: HomeAssistantInput) -> HomeAssistantOutput:
        """Send the given command to Home Assistant."""
        command = input_data.command.lower()

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        if "turn on" in command:
            requests.post(
                f"{self.base_url}/services/light/turn_on",
                headers=headers,
                json={"entity_id": "light.living_room"}
            )
            return HomeAssistantOutput(status="Light turned on")

        elif "turn off" in command:
            requests.post(
                f"{self.base_url}/services/light/turn_off",
                headers=headers,
                json={"entity_id": "light.living_room"}
            )
            return HomeAssistantOutput(status="Light turned off")

        return HomeAssistantOutput(status="Unknown command")
