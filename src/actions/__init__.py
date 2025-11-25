import importlib
from typing import Dict, Union, Optional
from actions.base import ActionConfig, ActionConnector, AgentAction, Interface

print("🔍 [DEBUG] actions package initialized — scanning for modules...")


# ------------------------------
# Describe action (metadata for LLM)
# ------------------------------
def describe_action(action_name: str, llm_label: str, exclude_from_prompt: bool) -> Optional[str]:
    if exclude_from_prompt:
        return None

    print(f"🔍 [DEBUG] Describing action: {action_name}")
    interface = None
    action = importlib.import_module(f"actions.{action_name}.interface")

    for _, obj in action.__dict__.items():
        if isinstance(obj, type) and issubclass(obj, Interface) and obj != Interface:
            interface = obj

    if interface is None:
        raise ValueError(f"❌ No interface found for action {action_name}")

    doc = (interface.__doc__ or "").replace("\n", " ")
    hints = {}
    input_interface = interface.T_input

    for field_name, field_type in input_interface.__annotations__.items():
        hints[field_name] = str(field_type)

    hint_block = "\n".join(f"{k}: {v}" for k, v in hints.items())
    final_description = f"{llm_label.upper()}: {doc}\n{hint_block}"
    return final_description.replace("  ", " ").strip()


# ------------------------------
# Load agent action (main runtime)
# ------------------------------
def load_action(action_config: Dict[str, Union[str, Dict[str, str]]]) -> AgentAction:
    print(f"🔍 [DEBUG] Loading action: {action_config['name']}")

    # 1️⃣ Load interface class
    interface = None
    action = importlib.import_module(f"actions.{action_config['name']}.interface")

    for _, obj in action.__dict__.items():                            # ⬅ FIXED indentation!
        if isinstance(obj, type) and issubclass(obj, Interface) and obj != Interface:
            interface = obj

    if interface is None:
        raise ValueError(f"❌ No interface found for action {action_config['name']}")

    # 2️⃣ Load connector ONLY if provided
    connector_class = None
    if "connector" in action_config:
        connector = importlib.import_module(
            f"actions.{action_config['name']}.connector.{action_config['connector']}"
        )
<<<<<<< HEAD
        for _, obj in connector.__dict__.items():                     # ⬅ FIXED indentation!
            if isinstance(obj, type) and issubclass(obj, ActionConnector):
                connector_class = obj

        if connector_class is None:
            raise ValueError(
                f"❌ No connector found for action {action_config['name']} → {action_config['connector']}"
            )

    # 3️⃣ Build config
    config = ActionConfig(**action_config.get("config", {}))
    exclude_from_prompt = action_config.get("exclude_from_prompt", False)

    print(f"🟢 [DEBUG] Action loaded successfully: {action_config['name']}")
=======
    config = ActionConfig(**action_config.get("config", {}))  # type: ignore

    exclude_from_prompt = False
    if "exclude_from_prompt" in action_config:
        exclude_from_prompt = bool(action_config["exclude_from_prompt"])

>>>>>>> upstream/main
    return AgentAction(
        name=action_config["name"],  # type: ignore
        llm_label=action_config["llm_label"],  # type: ignore
        interface=interface,
        connector=connector_class(config) if connector_class else None,
        exclude_from_prompt=exclude_from_prompt,
    )
