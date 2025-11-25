import logging
<<<<<<< HEAD

from actions.base import ActionConfig, ActionConnector
from actions.face.interface import FaceInput


class FaceAvatarConnector(ActionConnector[FaceInput]):
    """
    Connects face actions to the Avatar provider to send commands.
    """

    def __init__(self, config: ActionConfig):
        """
        Initializes the FaceAvatarConnector with the given configuration.

        Parameters
        ----------
        config : ActionConfig
            The configuration for the action connector.
        """
        super().__init__(config)

    async def connect(self, output_interface: FaceInput) -> None:
        """
        Connects the face action to the Avatar provider and sends the corresponding command.

        Parameters
        ----------
        output_interface : FaceInput
            The output interface containing the face action to be sent.
        """
        new_msg = {"face": ""}

        if output_interface.action == "smile":
            new_msg["face"] = "smile"
        elif output_interface.action == "frown":
            new_msg["face"] = "frown"
        elif output_interface.action == "cry":
            new_msg["face"] = "cry"
        elif output_interface.action == "think":
            new_msg["face"] = "think"
        elif output_interface.action == "joy":
            new_msg["face"] = "joy"
        else:
            logging.info(f"Unknown face type: {output_interface.action}")

        logging.info(f"Sent this to avatar: {new_msg}")
=======
import time

from actions.base import ActionConfig, ActionConnector
from actions.face.interface import FaceInput
from providers.avatar_provider import AvatarProvider


class FaceAvatarConnector(ActionConnector[FaceInput]):
    def __init__(self, config: ActionConfig):
        """
        Initialize the FaceAvatarConnector with AvatarProvider.

        Parameters:
        ----------
        config : ActionConfig
            Configuration parameters for the connector.
        """
        super().__init__(config)

        self.avatar_provider = AvatarProvider()
        logging.info("Face system initiated with AvatarProvider")

    async def connect(self, output_interface: FaceInput) -> None:
        """
        Send face command via AvatarProvider.

        Parameters:
        ----------
        output_interface : FaceInput
        """
        if output_interface.action == "happy":
            self.avatar_provider.send_avatar_command("Happy")
        elif output_interface.action == "sad":
            self.avatar_provider.send_avatar_command("Sad")
        elif output_interface.action == "curious":
            self.avatar_provider.send_avatar_command("Curious")
        elif output_interface.action == "confused":
            self.avatar_provider.send_avatar_command("Confused")
        elif output_interface.action == "think":
            self.avatar_provider.send_avatar_command("Think")
        elif output_interface.action == "excited":
            self.avatar_provider.send_avatar_command("Excited")
        else:
            logging.warning("Failed to send avatar face command")

        logging.info(f"Avatar face command sent: {output_interface.action}")

    def stop(self):
        """
        Stop and cleanup AvatarProvider.
        """
        self.avatar_provider.stop()
        logging.info("AvatarProvider stopped")

    def tick(self) -> None:
        time.sleep(60)
>>>>>>> upstream/main
