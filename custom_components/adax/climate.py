"""
Adax WiFi Heater Integration for Home Assisant.

By Jon Davies, based on work by others

Tested against Home Assistant Version: [not tested yet]

Notes:
  The away mode set points can only be set on the thermostat.  The code below
  prevents changing set points when in away mode so there are no surprises
  when leaving away mode.

Issues:

Ideas/Future:

Change log:

"""

import asyncio
import logging
import voluptuous as vol

from homeassistant.components.climate import PLATFORM_SCHEMA, ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_HEAT, 
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_TARGET_TEMPERATURE
)
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    TEMP_CELSIUS,
    ATTR_TEMPERATURE,
    PRECISION_WHOLE
)
   
from homeassistant.helpers import config_validation as cv

from . import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_USERNAME): cv.string, vol.Required(CONF_PASSWORD): cv.string}
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Adax thermostat."""
    client_id = config[CONF_USERNAME]
    client_secret = config[CONF_PASSWORD]

    adax_data_handler = Adax(client_id, client_secret)

    dev = []
    for heater_data in adax_data_handler.get_rooms():
        dev.append(AdaxEntity(heater_data, adax_data_handler))
    add_entities(dev)


class AdaxEntity(ClimateEntity):
    """Representation of an Adax WiFi heater."""

    def __init__(self, heater_data, adax_data_handler):
        """Initialize the heater."""
        self._heater_data = heater_data
        self._adax_data_handler = adax_data_handler

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_TARGET_TEMPERATURE

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._heater_data['homeId']}_{self._heater_data['id']}"

    @property
    def name(self):
        """Return the name of the device, if any."""
        return self._heater_data['name']

    @property
    def hvac_mode(self):
        """Return hvac operation i.e. heat, off mode.
        Need to be one of HVAC_MODE_*.
        """
        if self._heater_data['heatingEnabled'] then
            return HVAC_MODE_HEAT
        else
            return HVAC_MODE_OFF

    @property
    def hvac_modes(self):
        """Return the list of available hvac operation modes.
        Need to be a subset of HVAC_MODES.
        """
        return [HVAC_MODE_HEAT, HVAC_MODE_OFF]

    @property
    def temperature_unit(self):
        """Return the unit of measurement which this device uses."""
        return TEMP_CELSIUS

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return 5 # limit defined in the API, if you want <5 turn the heater off

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return 35 # limit defined in the API

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._heater_data['temperature']

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._heater_data['targetTemperature']

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return PRECISION_WHOLE # might be able to do fractional temperatures??

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        self._adax_data_handler.set_room_target_temperature(self._heater_data['id'], self._heater_data['heatingEnabled'], temperature)
        self._adax_data_handler.update(force_update=True)

    def update(self):
        """Get the latest data."""
        for room in self._adax_data_handler.get_rooms():
            if room['id'] == self._heater_data['id']:
                self._heater_data = room
                return


######
import datetime
import requests
import sanction


API_URL = "https://api-1.adax.no/client-api"


class Adax:
    def __init__(self, account_id, password):
        self._account_id = account_id
        self._password = password
        self._oauth_client = None
        self._rooms = []
        self._last_updated = datetime.datetime.utcnow() - datetime.timedelta(hours=2)

    def get_rooms(self):
        self.update()
        return self._rooms

    def update(self, force_update=False):
        now = datetime.datetime.utcnow()
        if now - self._last_updated < datetime.timedelta(minutes=30) and not force_update:
            return
        self._last_updated = now
        self.fetch_rooms_info()

    def set_room_target_temperature(self, room_id, heatingEnabled, temperature):
        """Sets target temperature of the room."""
        json_data = {'rooms': [{ 'id': room_id, 'heatingEnabled': heatingEnabled, 'targetTemperature': str(int(temperature*100))}]}
        self._request(API_URL + '/rest/v1/control/', json_data=json_data)

    def fetch_rooms_info(self):
        """Get rooms info"""
        response = self._request(API_URL + "/rest/v1/content/")
        json_data = response.json()
        self._rooms =  json_data['rooms']
        for room in self._rooms:
            room['targetTemperature'] = room['targetTemperature'] / 100.0
            room['temperature'] = room.get('temperature', 0) / 100.0

    def _request(self, url, json_data=None, retry=2):
        if self._oauth_client is None:
            self._oauth_client = sanction.Client(token_endpoint=API_URL + '/auth/token')

        if self._oauth_client.access_token is None:
            self._oauth_client.request_token(grant_type='password', username=self._account_id, password=self._password)

        headers = {"Authorization": f"Bearer {self._oauth_client.access_token}"}
        response = None
        try:
            if json_data:
                response = requests.post(url, json=json_data, headers=headers)
            else:
                response = requests.get(url, headers=headers)
        except Exception:
            _LOGGER.error("Failed to connect to adax", exc_info=True)
            if retry < 1:
                raise
        if (response is None or response.status_code >= 300) and retry > 0:
            self._oauth_client = None
            return self._request(url, json_data, retry=retry - 1)
        return response
