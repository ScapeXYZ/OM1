import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import json5

from actions import load_action
from actions.base import AgentAction
from backgrounds import load_background
from backgrounds.base import Background, BackgroundConfig
from inputs import load_input
from inputs.base import Sensor, SensorConfig
<<<<<<< HEAD:src/runtime/config.py
from llm import load_llm, LLMConfig, OpenAiLLM
from llm.output_model import CortexOutputModel
from providers.io_provider import IOProvider
=======
from llm import LLM, LLMConfig, load_llm
from runtime.robotics import load_unitree
from simulators import load_simulator
from simulators.base import Simulator, SimulatorConfig

>>>>>>> upstream/main:src/runtime/single_mode/config.py

@dataclass
class RuntimeConfig:
    hertz: float
    name: str
    system_prompt_base: str
    system_governance: str
    system_prompt_examples: str
    agent_inputs: List[Sensor]
<<<<<<< HEAD:src/runtime/config.py
    cortex_llm: None
    simulators: List = None
    agent_actions: List[AgentAction] = None
    backgrounds: List[Background] = None
=======
    cortex_llm: LLM
    simulators: List[Simulator]
    agent_actions: List[AgentAction]
    backgrounds: List[Background]

    # Optional robot IP address for the runtime configuration
    robot_ip: Optional[str] = None

    # Optional API key for the runtime configuration
    api_key: Optional[str] = None

    # Optional URID robot id key for the runtime configuration
    URID: Optional[str] = None

    # Optional Ethernet adapter setting for Unitree Robots
    unitree_ethernet: Optional[str] = None

    # Optional mode information for multi-mode runtime configurations
    mode: Optional[str] = None

    @classmethod
    def load(cls, config_name: str) -> "RuntimeConfig":
        """Load a runtime configuration from a file."""
        return load_config(config_name)
>>>>>>> upstream/main:src/runtime/single_mode/config.py


def load_config(
    config_name: str, config_source_path: Optional[str] = None
) -> RuntimeConfig:
    """
<<<<<<< HEAD:src/runtime/config.py
    Load configuration from ./config/*.json5
    """
    config_path = os.path.join(os.path.dirname(__file__), "../../config", f"{config_name}.json5")
    with open(config_path, "r", encoding="utf-8") as f:
        raw_config = json5.load(f)

    # Global metadata not required for bounty (robot not needed)
    g_api_key = os.environ.get("OM1_API_KEY")
    g_ut_eth = None
    g_URID = None
    g_robot_ip = None

    def add_meta(config: dict) -> dict:
        """Add API key to config if needed"""
        if not isinstance(config, dict):
            return {}
        if g_api_key:
            config["api_key"] = g_api_key
        return config
=======
    Load and parse a runtime configuration from a JSON file.

    Parameters
    ----------
    config_name : str
        Name of the configuration file (without .json extension)
    config_source_path : Optional[str]
        Optional path to the configuration file to load. If not provided, the default path based on config_name will be used.

    Returns
    -------
    RuntimeConfig
        Parsed runtime configuration object

    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist
    json.JSONDecodeError
        If the configuration file contains invalid JSON
    KeyError
        If required configuration fields are missing
    ImportError
        If component types specified in config cannot be imported
    ValueError
        If configuration values are invalid (e.g., negative hertz)
    """
    config_path = (
        os.path.join(
            os.path.dirname(__file__), "../../../config", config_name + ".json5"
        )
        if config_source_path is None
        else config_source_path
    )

    with open(config_path, "r+") as f:
        raw_config = json5.load(f)

    g_robot_ip = raw_config.get("robot_ip", None)
    if g_robot_ip is None or g_robot_ip == "" or g_robot_ip == "192.168.0.241":
        logging.warning(
            "No robot ip found in the configuration file. Checking for backup robot ip in your .env file."
        )
        backup_key = os.environ.get("ROBOT_IP")
        g_robot_ip = backup_key
        if backup_key:
            raw_config["robot_ip"] = backup_key
            logging.info("Success - Found ROBOT_IP in your .env file.")
        else:
            logging.warning(
                "Could not find robot ip address. Please find your robot IP address and add it to the configuration file or .env file."
            )
    g_api_key = raw_config.get("api_key", None)
    if g_api_key is None or g_api_key == "" or g_api_key == "openmind_free":
        logging.warning(
            "No API key found in the configuration file. Checking for backup OM_API_KEY in your .env file."
        )
        backup_key = os.environ.get("OM_API_KEY")
        g_api_key = backup_key
        if backup_key:
            raw_config["api_key"] = backup_key
            logging.info("Success - Found OM_API_KEY in your .env file.")
        else:
            logging.warning(
                "Could not find any API keys. Please get a free key at portal.openmind.org."
            )

    g_URID = raw_config.get("URID", None)
    if g_URID is None or g_URID == "":
        logging.warning(
            "No URID found in the configuration file. Multirobot deployments will conflict."
        )

    if g_URID == "default":
        logging.info("Checking for backup URID in your .env file.")
        backup_URID = os.environ.get("URID")
        if backup_URID:
            g_URID = backup_URID
            logging.info("Success - Found URID in your .env file.")
        else:
            logging.warning(
                "Could not find backup URID in your .env file. Using 'default'. Multirobot deployments will conflict."
            )

    g_ut_eth = raw_config.get("unitree_ethernet", None)
    if g_ut_eth is None or g_ut_eth == "":
        logging.info("No robot hardware ethernet port provided.")
    else:
        # Load Unitree robot communication channel, if needed
        load_unitree(g_ut_eth)

    conf = raw_config["cortex_llm"].get("config", {})
    logging.debug(f"config.py: {conf}")

    parsed_config = {
        **raw_config,
        "backgrounds": [
            load_background(bg["type"])(
                config=BackgroundConfig(
                    **add_meta(
                        bg.get("config", {}), g_api_key, g_ut_eth, g_URID, g_robot_ip
                    )
                )
            )
            for bg in raw_config.get("backgrounds", [])
        ],
        "agent_inputs": [
            load_input(input["type"])(
                config=SensorConfig(
                    **add_meta(
                        input.get("config", {}), g_api_key, g_ut_eth, g_URID, g_robot_ip
                    )
                )
            )
            for input in raw_config.get("agent_inputs", [])
        ],
        "simulators": [
            load_simulator(simulator["type"])(
                config=SimulatorConfig(
                    name=simulator["type"],
                    **add_meta(
                        simulator.get("config", {}),
                        g_api_key,
                        g_ut_eth,
                        g_URID,
                        g_robot_ip,
                    ),
                )
            )
            for simulator in raw_config.get("simulators", [])
        ],
        "agent_actions": [
            load_action(
                {
                    **action,
                    "config": add_meta(
                        action.get("config", {}),
                        g_api_key,
                        g_ut_eth,
                        g_URID,
                        g_robot_ip,
                    ),
                }
            )
            for action in raw_config.get("agent_actions", [])
        ],
    }

    cortex_llm = (
        load_llm(raw_config["cortex_llm"]["type"])(
            config=LLMConfig(
                **add_meta(  # type: ignore
                    raw_config["cortex_llm"].get("config", {}),
                    g_api_key,
                    g_ut_eth,
                    g_URID,
                    g_robot_ip,
                )
            ),
            available_actions=parsed_config["agent_actions"],
        ),
    )

    if len(cortex_llm) != 1:
        raise ValueError("Expected exactly one cortex_llm instance.")

    parsed_config["cortex_llm"] = cortex_llm[0]

    return RuntimeConfig(**parsed_config)


def get_nested_value(data, keys):
    if not keys:
        return data
    if isinstance(data, dict) and keys[0] in data:
        return get_nested_value(data[keys[0]], keys[1:])
    return None


def add_meta(
    config: Dict,
    g_api_key: Optional[str],
    g_ut_eth: Optional[str],
    g_URID: Optional[str],
    g_robot_ip: Optional[str],
    g_mode: Optional[str] = None,
) -> dict[str, str]:
    """
    Add an API key and Robot configuration to a runtime configuration.

    Parameters
    ----------
    config : dict
        The runtime configuration to update.
    g_api_key : str
        The API key to add.
    g_ut_eth : str
        The Robot ethernet port to add.
    g_URID : str
        The Robot URID to use.

    Returns
    -------
    dict
        The updated runtime configuration.
    """

    # logging.info(f"config before {config}")
    if "api_key" not in config and g_api_key is not None:
        config["api_key"] = g_api_key
    if "unitree_ethernet" not in config and g_ut_eth is not None:
        config["unitree_ethernet"] = g_ut_eth
    if "URID" not in config and g_URID is not None:
        config["URID"] = g_URID
    if "robot_ip" not in config and g_robot_ip is not None:
        config["robot_ip"] = g_robot_ip
    if "mode" not in config and g_mode is not None:
        config["mode"] = g_mode
    return config


# this is for testing only
def build_runtime_config_from_test_case(config: dict) -> RuntimeConfig:
    api_key = config.get("api_key")
    g_ut_eth = config.get("unitree_ethernet")
    g_URID = config.get("URID")
    g_robot_ip = config.get("robot_ip")
>>>>>>> upstream/main:src/runtime/single_mode/config.py

    # Load backgrounds if any
    backgrounds = [
        load_background(bg["type"])(
            config=BackgroundConfig(**add_meta(bg.get("config", {})))
        )
        for bg in raw_config.get("backgrounds", [])
    ]

    # Load inputs if provided
    agent_inputs = [
        load_input(inp["type"])(
            config=SensorConfig(**add_meta(inp.get("config", {})))
        )
        for inp in raw_config.get("agent_inputs", [])
    ]
<<<<<<< HEAD:src/runtime/config.py

    # Load LLM
    cortex_llm_cfg = raw_config.get("cortex_llm")
    if isinstance(cortex_llm_cfg, dict):
        llm_type = cortex_llm_cfg.get("type")
        llm_config = cortex_llm_cfg.get("config", {})
    else:
        llm_type = cortex_llm_cfg
        llm_config = {}

    cortex_llm = load_llm(
       llm_type,
       config=LLMConfig(**add_meta(llm_config)),
    )


    # Load agent_actions (pizza ordering)
=======
    simulators = [
        load_simulator(sim["type"])(
            config=SimulatorConfig(
                name=sim["type"],
                **add_meta(
                    sim.get("config", {}), api_key, g_ut_eth, g_URID, g_robot_ip
                ),
            )
        )
        for sim in config.get("simulators", [])
    ]
>>>>>>> upstream/main:src/runtime/single_mode/config.py
    agent_actions = [
        load_action({
            **action.get("config", {}),
            "name": action.get("name"),
            "description": action.get("description"),
            "parameters": action.get("parameters", {}),
            "llm_label": action.get("llm_label", "")
        })
        for action in raw_config.get("agent_actions", [])
    ]
<<<<<<< HEAD:src/runtime/config.py


=======
    cortex_llm = load_llm(config["cortex_llm"]["type"])(
        config=LLMConfig(
            **add_meta(  # type: ignore
                config["cortex_llm"].get("config", {}),
                api_key,
                g_ut_eth,
                g_URID,
                g_robot_ip,
            )
        ),
        available_actions=agent_actions,
    )
>>>>>>> upstream/main:src/runtime/single_mode/config.py
    return RuntimeConfig(
        hertz=raw_config.get("hertz", 1.0),
        name=raw_config.get("name", "Pizza Order Assistant"),
        system_prompt_base=raw_config.get("system_prompt_base", ""),
        system_governance=raw_config.get("system_governance", ""),
        system_prompt_examples=raw_config.get("system_prompt_examples", ""),
        agent_inputs=agent_inputs,
        cortex_llm=cortex_llm,
        simulators=[],
        agent_actions=agent_actions,
        backgrounds=backgrounds,
    )
