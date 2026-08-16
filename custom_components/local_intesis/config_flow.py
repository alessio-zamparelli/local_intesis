from __future__ import annotations

import logging
from collections.abc import Mapping

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    OptionsFlowWithConfigEntry,
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_PASSWORD,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_USERNAME,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_USERNAME, default=DEFAULT_USERNAME): str,
        vol.Optional(CONF_PASSWORD, default=DEFAULT_PASSWORD): str,
    }
)


class LocalIntesisConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 2

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> LocalIntesisOptionsFlow:
        return LocalIntesisOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            username = user_input.get(CONF_USERNAME, DEFAULT_USERNAME)
            password = user_input.get(CONF_PASSWORD, DEFAULT_PASSWORD)
            session = async_get_clientsession(self.hass)
            payload = {
                "command": "login",
                "data": {"username": username, "password": password},
            }
            try:
                async with session.post(
                    f"http://{host}/api.cgi",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status in (401, 403):
                        errors["base"] = "auth"
                    elif resp.status >= 400:
                        errors["base"] = "cannot_connect"
                    else:
                        json_resp = await resp.json(content_type=None)
                        if not isinstance(json_resp, Mapping):
                            errors["base"] = "cannot_connect"
                        elif not json_resp.get("success"):
                            errors["base"] = "auth"
                        else:
                            login_data = json_resp.get("data")
                            login_id = (
                                login_data.get("id")
                                if isinstance(login_data, Mapping)
                                else None
                            )
                            session_id = (
                                login_id.get("sessionID")
                                if isinstance(login_id, Mapping)
                                else None
                            )
                            if not isinstance(session_id, str) or not session_id:
                                errors["base"] = "cannot_connect"
                            else:
                                info_payload = {
                                    "command": "getinfo",
                                    "data": {"sessionID": session_id},
                                }
                                async with session.post(
                                    f"http://{host}/api.cgi",
                                    json=info_payload,
                                    timeout=aiohttp.ClientTimeout(total=10),
                                ) as info_resp:
                                    if info_resp.status >= 400:
                                        errors["base"] = "cannot_connect"
                                    else:
                                        info_json = await info_resp.json(
                                            content_type=None
                                        )
                                        info_data = (
                                            info_json.get("data")
                                            if isinstance(info_json, Mapping)
                                            and info_json.get("success")
                                            else None
                                        )
                                        info = (
                                            info_data.get("info")
                                            if isinstance(info_data, Mapping)
                                            else None
                                        )
                                        if not isinstance(info, Mapping):
                                            errors["base"] = "cannot_connect"
                                        else:
                                            serial_value = info.get("sn")
                                            model = info.get("deviceModel", "Unknown")
                                            if (
                                                serial_value is not None
                                                and not isinstance(serial_value, str)
                                            ) or not isinstance(model, str):
                                                errors["base"] = "cannot_connect"
                                            else:
                                                serial = (
                                                    serial_value.split(" ")[0]
                                                    if serial_value
                                                    else host
                                                )
                                                await self.async_set_unique_id(
                                                    f"local_intesis_{serial}"
                                                )
                                                self._abort_if_unique_id_configured()
                                                return self.async_create_entry(
                                                    title=f"Intesis ({model})",
                                                    data=user_input,
                                                )
            except (aiohttp.ClientError, TimeoutError, ValueError) as exc:
                _LOGGER.error("Connection failed: %s", exc)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "default_user": DEFAULT_USERNAME,
                "default_pass": DEFAULT_PASSWORD,
            },
        )


class LocalIntesisOptionsFlow(OptionsFlowWithConfigEntry):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL, default=current_interval): vol.All(
                    vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)
                )
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)