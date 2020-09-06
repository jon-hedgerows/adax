# Adax WiFi Heater Integration
A custom component for Home Assistant to integrate with Adax WiFi heaters.
See [Adax](https://adax.no/en/wi-fi/) for compatible heaters.

**Requirement:** You must have your heater linked to the ADAX WiFi app.

Once you've connected your heater to the ADAX WiFi app and got it set up and working, go to the
Account page and make a note of the Account ID at the bottom (something like Account ID: 12345).  In the
Remote user client API, create a credential for Home Assistant, and make a note of the service Password.


## Basic Configuration
```yaml
climate:
  - platform: adax
    name: roomheater
    account_id: !secret adax_account_id
    password: !secret adax_service_password
```

# Documentation
Please visit the [GitHub Repository](https://github.com/jon-hedgerows/adax) for full documentation.

# Adax.no Client API
https://adax.no/en/about-adax/api-development/
