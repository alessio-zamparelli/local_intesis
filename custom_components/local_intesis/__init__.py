from __future__ import annotations

import asyncio
import logging
import math
from collections.abc import Mapping

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_GET_DP,
    API_GET_INFO,
    API_GET_VALUE,
    API_LOGIN,
    API_SET_VALUE,
    CONF_SCAN_INTERVAL,
    DOMAIN,
    ERROR_COMMUNICATION_VALUE,
    FAN_SPEED_TABLES,
    MIN_SCAN_INTERVAL,
    PRESET_MODE_MAP,
    UID_ALARM_STATUS,
    UID_AQUAREA_COOL_CONSUMPTION,
    UID_AQUAREA_HEAT_CONSUMPTION,
    UID_CLIMATE_WORKING_MODE,
    UID_CONFIG_HVANE,
    UID_CONFIG_VVANE,
    UID_ERROR_CODE,
    UID_ERROR_CODE_LEGACY,
    UID_FAN_SPEED,
    UID_HVANE,
    UID_RSSI,
    UID_VVANE,
)

PLATFORMS = ["climate"]

_LOGGER = logging.getLogger(__name__)


class IntesisGateway:
    def __init__(self, host: str, username: str, password: str, session: aiohttp.ClientSession) -> None:
        self._host = host
        self._username = username
        self._password = password
        self._session = session
        self._base = f"http://{host}/api.cgi"
        self._session_id: str | None = None
        self._auth_lock = asyncio.Lock()
        self._devices: dict = {}
        self._datapoints: dict = {}
        self._config_fan_map: dict[int, str] = {}
        self._config_vvane_list: list[int] = []
        self._config_hvane_list: list[int] = []
        self._has_climate_working_mode = False
        self._has_alarm_status = False
        self._has_error_code = False
        self._has_rssi = False
        self._has_aquarea_cool = False
        self._has_aquarea_heat = False

    async def _request(self, command: str, _retry: bool = True, **kwargs) -> dict | None:
        if not self._session_id:
            if not await self._authenticate():
                _LOGGER.error("Not authenticated for %s", self._host)
                return None
        session_id = self._session_id
        payload = {"command": command, "data": {"sessionID": session_id, **kwargs}}
        try:
            async with self._session.post(self._base, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                json_resp = await resp.json(content_type=None)
                if not isinstance(json_resp, Mapping):
                    _LOGGER.warning("Unexpected response from %s: %s", self._host, json_resp)
                    return None
                if json_resp.get("success"):
                    data = json_resp.get("data")
                    return dict(data) if isinstance(data, Mapping) else None
                error = json_resp.get("error")
                if isinstance(error, Mapping):
                    code = error.get("code")
                    if code in (1, 5) and _retry:
                        if self._session_id == session_id:
                            self._session_id = None
                        if command != API_LOGIN:
                            return await self._request(command, _retry=False, **kwargs)
                    _LOGGER.warning("API error %s: %s", code, error.get("message"))
                    return None
                _LOGGER.warning("Unexpected response from %s: %s", self._host, json_resp)
                return None
        except (aiohttp.ClientError, TimeoutError, ValueError) as exc:
            _LOGGER.error("Request failed for %s: %s", self._host, exc)
            return None

    async def _authenticate(self) -> bool:
        async with self._auth_lock:
            if self._session_id:
                return True

            payload = {"command": API_LOGIN, "data": {"username": self._username, "password": self._password}}
            try:
                async with self._session.post(
                    self._base,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    json_resp = await resp.json(content_type=None)
                    if not isinstance(json_resp, Mapping):
                        _LOGGER.warning("Malformed auth response from %s", self._host)
                        return False

                    data = json_resp.get("data")
                    identity = data.get("id") if isinstance(data, Mapping) else None
                    session_id = identity.get("sessionID") if isinstance(identity, Mapping) else None
                    if json_resp.get("success") and isinstance(session_id, str) and session_id:
                        self._session_id = session_id
                        _LOGGER.debug("Authenticated with %s", self._host)
                        return True

                    error = json_resp.get("error")
                    message = error.get("message", "unknown") if isinstance(error, Mapping) else "unknown"
                    _LOGGER.warning("Auth failed for %s: %s", self._host, message)
            except (aiohttp.ClientError, TimeoutError, ValueError, TypeError) as exc:
                _LOGGER.error("Auth failed for %s: %s", self._host, exc)
            return False

    async def connect(self) -> bool:
        result = await self._request(API_GET_INFO)
        if not isinstance(result, Mapping):
            return False
        info = result.get("info")
        if not isinstance(info, Mapping):
            return False
        raw_id = info.get("sn")
        device_id = raw_id.split(maxsplit=1)[0] if isinstance(raw_id, str) and raw_id.strip() else self._host

        dp_result = await self._request(API_GET_DP)
        if not isinstance(dp_result, Mapping):
            return False
        dp_container = dp_result.get("dp")
        datapoints = dp_container.get("datapoints") if isinstance(dp_container, Mapping) else None
        if not isinstance(datapoints, list):
            return False

        parsed_datapoints: dict[int, dict] = {}
        for datapoint in datapoints:
            if not isinstance(datapoint, Mapping):
                continue
            uid = self._as_int(datapoint.get("uid"))
            if uid is None:
                continue
            parsed_datapoints[uid] = dict(datapoint)
        if not parsed_datapoints:
            return False

        self._devices[device_id] = {
            "name": info.get("ownSSID") if isinstance(info.get("ownSSID"), str) else f"Intesis_{device_id}",
            "model": info.get("deviceModel") if isinstance(info.get("deviceModel"), str) else "",
            "fw": info.get("wlanFwVersion") if isinstance(info.get("wlanFwVersion"), str) else "",
        }
        self._datapoints = parsed_datapoints
        self._parse_config_datapoints()
        return True

    def _parse_config_datapoints(self) -> None:
        self._has_climate_working_mode = UID_CLIMATE_WORKING_MODE in self._datapoints
        self._has_alarm_status = UID_ALARM_STATUS in self._datapoints
        self._has_error_code = UID_ERROR_CODE in self._datapoints or UID_ERROR_CODE_LEGACY in self._datapoints
        self._has_rssi = UID_RSSI in self._datapoints
        self._has_aquarea_cool = UID_AQUAREA_COOL_CONSUMPTION in self._datapoints
        self._has_aquarea_heat = UID_AQUAREA_HEAT_CONSUMPTION in self._datapoints

        self._config_fan_map = self._get_fan_map()

        vvane_cfg = self._datapoints.get(UID_CONFIG_VVANE)
        vvane_dp = self._datapoints.get(UID_VVANE)
        self._config_vvane_list = self._get_states(vvane_dp) or self._get_states(vvane_cfg)

        hvane_cfg = self._datapoints.get(UID_CONFIG_HVANE)
        hvane_dp = self._datapoints.get(UID_HVANE)
        self._config_hvane_list = self._get_states(hvane_dp) or self._get_states(hvane_cfg)

    def _get_states(self, datapoint: object) -> list[int]:
        if not isinstance(datapoint, Mapping):
            return []
        descr = datapoint.get("descr")
        if not isinstance(descr, Mapping) or not isinstance(descr.get("states"), list):
            return []
        return [state for item in descr["states"] if (state := self._as_int(item)) is not None]

    def _get_fan_map(self) -> dict[int, str]:
        fan_datapoint = self._datapoints.get(UID_FAN_SPEED)
        fan_values = sorted(self._get_states(fan_datapoint))
        if not fan_values:
            return {}
        device_model = self._devices.get(self.device_id, {}).get("model", "")
        if 0 not in fan_values and "MH-AC-WIFI" in device_model:
            fan_values = [0] + fan_values
        for table_key in sorted(FAN_SPEED_TABLES.keys(), reverse=True):
            table = FAN_SPEED_TABLES[table_key]
            if sorted(table.keys()) == fan_values:
                return table
        labels = ["auto", "low", "medium", "high", "max"]
        return {s: labels[i] if i < len(labels) else f"speed_{s}" for i, s in enumerate(fan_values)}

    @staticmethod
    def _as_int(value: object) -> int | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value) if math.isfinite(value) and value.is_integer() else None
        if isinstance(value, str):
            try:
                return int(value.strip())
            except ValueError:
                return None
        return None

    def _in_range(self, uid: int, value: int) -> bool:
        if uid in (UID_ERROR_CODE, UID_ERROR_CODE_LEGACY) and value == ERROR_COMMUNICATION_VALUE:
            return True
        dp = self._datapoints.get(uid)
        if not isinstance(dp, Mapping):
            return True
        descr = dp.get("descr")
        if not isinstance(descr, Mapping):
            return True

        minimum = self._as_int(descr.get("minValue"))
        maximum = self._as_int(descr.get("maxValue"))
        if minimum is None or maximum is None or minimum <= maximum:
            if minimum is not None and value < minimum:
                return False
            if maximum is not None and value > maximum:
                return False

        states = descr.get("states")
        if isinstance(states, (list, tuple, set, frozenset)):
            valid_states = {state for item in states if (state := self._as_int(item)) is not None}
            if valid_states and value not in valid_states:
                return False
        return True

    def _poll_item(self, item: object) -> tuple[int, int] | None:
        if not isinstance(item, Mapping):
            return None
        uid = self._as_int(item.get("uid"))
        value = self._as_int(item.get("value"))
        status = self._as_int(item.get("status", 0))
        if uid is None or value is None or status != 0 or not self._in_range(uid, value):
            return None
        return uid, value

    async def poll_values(self) -> dict[int, int]:
        result = await self._request(API_GET_VALUE, uid="all")
        if not isinstance(result, Mapping):
            return {}
        values = {}
        dpval = result.get("dpval", [])
        if isinstance(dpval, list):
            for item in dpval:
                parsed = self._poll_item(item)
                if parsed is not None:
                    uid, value = parsed
                    values[uid] = value
        elif isinstance(dpval, Mapping):
            parsed = self._poll_item(dpval)
            if parsed is not None:
                uid, value = parsed
                values[uid] = value
        if UID_ERROR_CODE not in values and UID_ERROR_CODE_LEGACY in values:
            values[UID_ERROR_CODE] = values[UID_ERROR_CODE_LEGACY]
        return values

    async def set_value(self, uid: int, value: int) -> bool:
        result = await self._request(API_SET_VALUE, uid=uid, value=value)
        return result is not None

    @property
    def devices(self) -> dict:
        return self._devices

    @property
    def device_id(self) -> str:
        return next(iter(self._devices), "unknown")

    @property
    def device_name(self) -> str:
        return self._devices.get(self.device_id, {}).get("name", "Intesis Gateway")

    @property
    def device_model(self) -> str:
        return self._devices.get(self.device_id, {}).get("model", "")

    @property
    def fan_modes(self) -> list[str]:
        return list(dict.fromkeys(self._config_fan_map.values()))

    def get_fan_value(self, label: str) -> int | None:
        for k, v in self._config_fan_map.items():
            if v == label:
                return k
        return None

    def get_fan_label(self, value: int) -> str:
        return self._config_fan_map.get(value, "auto")

    @property
    def vvane_list(self) -> list[int]:
        return self._config_vvane_list

    @property
    def hvane_list(self) -> list[int]:
        return self._config_hvane_list

    def supports_vvane(self) -> bool:
        return bool(self._config_vvane_list)

    def supports_hvane(self) -> bool:
        return bool(self._config_hvane_list)

    def has_datapoint(self, uid: int) -> bool:
        return uid in self._datapoints

    @property
    def has_climate_working_mode(self) -> bool:
        return self._has_climate_working_mode

    @property
    def has_alarm_status(self) -> bool:
        return self._has_alarm_status

    @property
    def has_error_code(self) -> bool:
        return self._has_error_code

    @property
    def has_rssi(self) -> bool:
        return self._has_rssi

    @property
    def has_aquarea_cool(self) -> bool:
        return self._has_aquarea_cool

    @property
    def has_aquarea_heat(self) -> bool:
        return self._has_aquarea_heat

    @property
    def preset_modes(self) -> list[str]:
        return list(PRESET_MODE_MAP.values()) if self._has_climate_working_mode else []

    def get_preset_value(self, label: str) -> int | None:
        for k, v in PRESET_MODE_MAP.items():
            if v == label:
                return k
        return None

    def get_preset_label(self, value: int) -> str | None:
        return PRESET_MODE_MAP.get(value)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    host = entry.data[CONF_HOST]
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    session = async_get_clientsession(hass)
    gateway = IntesisGateway(host, username, password, session)
    if not await gateway.connect():
        raise ConfigEntryNotReady(f"Could not connect to gateway at {host}")
    hass.data[DOMAIN][entry.entry_id] = gateway
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if entry.version == 1:
        new_options = dict(entry.options)
        new_options.setdefault(CONF_SCAN_INTERVAL, MIN_SCAN_INTERVAL)
        hass.config_entries.async_update_entry(
            entry, options=new_options, version=2
        )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
