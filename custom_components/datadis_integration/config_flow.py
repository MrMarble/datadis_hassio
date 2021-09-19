from typing import Any, Dict, Optional

import datadis.concurrent as datadis
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from custom_components.datadis_integration.sensor import CONF_CUPS

from .const import DOMAIN

AUTH_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_CUPS): cv.string,
    }
)


async def validate_auth(username: str, password: str):
    """Validates Datadis API credentials

    Raises a ValueError if the credentials are invalid
    """
    try:
        datadis.get_token(username, password)
    except:
        raise ValueError


class DatadisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_auth(
                    user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
                )
            except ValueError:
                errors["base"] = "auth"
            if not errors:
                # Input is valid, set data.
                self.data = user_input

        return self.async_show_form(
            step_id="user", data_schema=AUTH_SCHEMA, errors=errors
        )
