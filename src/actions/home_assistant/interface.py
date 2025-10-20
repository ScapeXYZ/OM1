from actions.base import Interface, ActionConfig
from typing import TypedDict
import os
import requests


class HomeAssistantInput(TypedDict):
    command: str


class HomeAssistantOutput(TypedDict):
    status: str


class HomeAssistant(Interface[HomeAssistantInput, HomeAssistantOutput]):
    """Home Assistant action interface."""
    input: type = HomeAssistantInput
    output: type = HomeAssistantOutput

    def __init__(self, config: ActionConfig):   # ✅ fixed double underscore
        super().__init__(config)
        self.base_url = os.getenv("HOME_ASSISTANT_URL", "http://localhost:8123")
        self.token = os.getenv("HOME_ASSISTANT_TOKEN")

        if not self.token:
            raise ValueError("❌ Missing HOME_ASSISTANT_TOKEN in .env file")

        print("✅ [HomeAssistant] Plugin initialized successfully.")

    def run(self, input_data: HomeAssistantInput) -> HomeAssistantOutput:
        """Send command to Home Assistant REST API."""
        command = input_data["command"].lower()
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        entity_id = "light.smart_bulb"
        print(f"[DEBUG] Command received: {command}")
        print(f"[DEBUG] Using URL: {self.base_url}")

        try:
            if "turn on" in command:
                response = requests.post(
                    f"{self.base_url}/api/services/light/turn_on",
                    headers=headers,
                    json={"entity_id": entity_id},
                    timeout=5
                )
                print(f"[DEBUG] Response: {response.status_code}, {response.text}")
                response.raise_for_status()
                return {"status": f"✅ Light turned ON ({entity_id})"}

            elif "turn off" in command:
                response = requests.post(
                    f"{self.base_url}/api/services/light/turn_off",
                    headers=headers,
                    json={"entity_id": entity_id},
                    timeout=5
                )
                print(f"[DEBUG] Response: {response.status_code}, {response.text}")
                response.raise_for_status()
                return {"status": f"💡 Light turned OFF ({entity_id})"}

            else:
                return {"status": f"⚠️ Unknown command: {command}"}

        except requests.exceptions.RequestException as e:
            return {"status": f"❌ Request failed: {str(e)}"}

        except Exception as e:
            return {"status": f"❌ Error: {str(e)}"}
