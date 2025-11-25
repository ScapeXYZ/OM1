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
from llm import load_llm, LLMConfig, OpenAiLLM
from llm.output_model import CortexOutputModel
from providers.io_provider import IOProvider

@dataclass
class RuntimeConfig:
    hertz: float
    name: str
    system_prompt_base: str
    system_governance: str
    system_prompt_examples: str
    agent_inputs: List[Sensor]
    cortex_llm: None
    simulators: List = None
    agent_actions: List[AgentAction] = None
    backgrounds: List[Background] = None


def load_config(config_name: str) -> RuntimeConfig:
    """
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
