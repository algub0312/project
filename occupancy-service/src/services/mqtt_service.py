import asyncio
import json
import threading
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

import paho.mqtt.client as mqtt


class MQTTService:
    """Service for handling MQTT communication."""

    def __init__(self) -> None:
        """Initialize the MQTT service."""
        self._client: Optional[mqtt.Client] = None
        self._connected = False
        self._occupancy_service: object = None
        self._denmark_tz = ZoneInfo("Europe/Copenhagen")

    def start(self, host: str, port: int, topic: str) -> None:
        """Start the MQTT client.

        Args:
            host (str): MQTT broker host.
            port (int): MQTT broker port.
            topic (str): MQTT topic to subscribe to.

        """
        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect

        self._topic = topic

        try:
            self._client.connect(host, port, 60)
            thread = threading.Thread(target=self._client.loop_forever, daemon=True)
            thread.start()
            print(f"MQTT client started, connecting to {host}:{port}")
        except Exception as e:
            print(f"Failed to start MQTT client: {e}")

    def stop(self) -> None:
        """Stop the MQTT client."""
        if self._client:
            self._client.disconnect()

    def set_occupancy_service(self, service: object) -> None:
        """Set the occupancy service for processing messages.

        Args:
            service: The occupancy service instance.

        """
        self._occupancy_service = service

    @property
    def is_connected(self) -> bool:
        """Check if MQTT client is connected.

        Returns:
            bool: True if connected, False otherwise.

        """
        return self._connected

    def _on_connect(
        self, client: object, userdata: object, flags: object, rc: int
    ) -> None:
        """Handle MQTT connection.

        Args:
            client: MQTT client instance.
            userdata: User data.
            flags: Connection flags.
            rc: Result code.

        """
        if rc == 0:
            self._connected = True
            print(f"Connected to MQTT broker, subscribing to {self._topic}")
            client.subscribe(self._topic, qos=1)
        else:
            print(f"Failed to connect to MQTT broker, code: {rc}")
            self._connected = False

    def _on_disconnect(self, client: object, userdata: object, rc: int) -> None:
        """Handle MQTT disconnection.

        Args:
            client: MQTT client instance.
            userdata: User data.
            rc: Result code.

        """
        self._connected = False
        print("Disconnected from MQTT broker")

    def _on_message(self, client: object, userdata: object, msg: object) -> None:
        """Process incoming MQTT message.

        Args:
            client: MQTT client instance.
            userdata: User data.
            msg: MQTT message.

        """
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            print(f"Received MQTT message: {payload}")

            # Validate required fields - timestamp is now optional
            if "desk_id" not in payload or "state" not in payload:
                print("Invalid payload: missing required fields (desk_id, state)")
                return

            desk_id = payload["desk_id"]
            occupied = bool(payload["state"])

            # Always use current timestamp when message is received
            timestamp = datetime.now().astimezone(self._denmark_tz)
            print(f"Using current server timestamp: {timestamp}")

            # Process the message if service is available
            if self._occupancy_service:
                try:
                    # Create new event loop if none exists
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                    # Run the async function
                    loop.run_until_complete(
                        self._occupancy_service.process_mqtt_update(
                            desk_id, occupied, timestamp
                        )
                    )
                    print(f"Successfully processed MQTT message for {desk_id}")
                except Exception as e:
                    print(f"Error processing MQTT message: {e}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in MQTT message: {e}")
        except Exception as e:
            print(f"Error processing MQTT message: {e}")


# Global MQTT service instance
mqtt_service = MQTTService()
