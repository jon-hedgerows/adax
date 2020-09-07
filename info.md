# Adax WiFi Heater Integration
A custom component for Home Assistant to integrate Adax WiFi heaters.
See [Adax](https://adax.no/en/wi-fi/) for compatible heaters.

**Requirement:** You must have your heater linked to the ADAX WiFi app.

Once you've connected your heater to the ADAX WiFi app and got it set up and working:
1. Go to the Account page and make a note of the Account ID at the bottom (something like Account ID: 12345).
2. In the Remote user client API, create a credential for Home Assistant, and make a note of the service Password.

## Configuration
```yaml
climate:
  - platform: adax
    username: !secret adax_account_id
    password: !secret adax_service_password
```
and add the account ID and service password to  ```secrets.yaml```.

# Documentation
There is no documentation, yet, apart from this file.

# Issues, Suggestions, etc.
Please log issues in the [GitHub Repository](https://github.com/jon-hedgerows/adax).

# Adax.no Client API
The API is defined here: https://adax.no/en/about-adax/api-development/

You can also find the API documentation in Swagger, based on the openapi specification provided by Adax.  https://app.swaggerhub.com/apis/hedgerows/Adax_remote-user_api/1
