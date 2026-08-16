# Changelog

## 1.3.0

- Added a configurable polling interval. Set it via the integration's Configure option in Home Assistant (Settings > Devices & Services > Local Intesis > Configure). Default is 30 seconds, range 6 to 3600 seconds.
- Existing installs keep their previous 6 second polling on upgrade; the new 30 second default applies to new installs.
- Changed the options flow to use the `OptionsFlowWithConfigEntry` base class, fixing an error where the configure dialog could not read the current entry.
- Raised the minimum supported Home Assistant version to 2024.3.0.
- Added a test suite covering the polling interval options flow and the config entry migration.