<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="custom_components/local_intesis/brand/icon.png">
    <img src="custom_components/local_intesis/brand/icon.png" alt="LocalIntesis" width="128">
  </picture>
</p>

<p align="center">
  <img src="https://img.shields.io/github/v/release/teamsuperpanda/local_intesis?style=flat-square&logo=github&label=Release" alt="Release">
  <img src="https://img.shields.io/badge/HACS-Integration-41BDF5?style=flat-square&logo=home-assistant&logoColor=white" alt="HACS">
  <img src="https://img.shields.io/badge/Home%20Assistant-2024.1.0-41BDF5?style=flat-square&logo=home-assistant&logoColor=white" alt="HA">
  <img src="https://img.shields.io/github/last-commit/teamsuperpanda/local_intesis?style=flat-square" alt="Last commit">
</p>

# Local Intesis - AC control without the cloud

A Home Assistant integration that talks directly to your IntesisHome WiFi gateway over your local network. No cloud. No waiting. No accounts you didn't make. Just your AC, your network, your rules.

## Why Local Intesis?

Other IntesisHome integrations bundle cloud SDKs, external libraries, and TCP tunnels that route through a cloud server. That server frequently drops connections, leaving your AC controls flapping between available and unavailable.

Local Intesis is different. Your IntesisHome gateway has a working HTTP API on port 80 sitting right on your LAN. This integration talks directly to it. No cloud account. No internet required. No flaky servers.

Zero dependencies. No pyintesishome, no pip packages, nothing to break. Four easy-to-audit files.

## Features

- Full climate control: heat, cool, dry, fan only, auto (heat/cool), and off
- Target temperature with 1-degree precision
- Fan speeds: auto, quiet (where supported), low, medium, high, max (automatically detected from your device)
- Vertical and horizontal swing with independent control
- Preset modes: eco, comfort, and boost/powerful (when your device supports it)
- Power consumption tracking: cooling and heating kW usage reported as state attributes
- Outdoor temperature, alarm status, error codes with descriptions, and signal strength (RSSI) as state attributes
- Automatic discovery of your device's capabilities - only shows what your AC actually supports
- Configurable polling interval (default 30 seconds) for snappy updates
- Optimistic updates - your commands take effect instantly while the integration syncs in the background
- Supports models: DK-RC-WIFI-1B, FJ-RC-WIFI-1B, FJ-AC-WIFI-1B, MH-AC-WIFI-1 (any IntesisHome gateway with the local HTTP API should work)

## How it works

The integration connects directly to your IntesisHome gateway over HTTP on port 80. It logs in, discovers what datapoints your AC exposes, and maps them to Home Assistant climate controls. Polling happens at a configurable interval (default 30 seconds). Commands are optimistic - the UI updates immediately and the background sync confirms the change.

## Installation

- Via HACS as a custom repository: add `https://github.com/teamsuperpanda/local_intesis` as a custom repository, search for Local Intesis, and install
- Manual: copy the `custom_components/local_intesis` directory into your Home Assistant `custom_components` folder, then restart

## Configuration

After installing and restarting Home Assistant, add the integration via Settings > Devices & Services > Add Integration > Local Intesis. You will need:

- The IP address or hostname of your IntesisHome gateway
- Username and password (default is admin/admin on most gateways)

The polling interval can be changed after setup from the integration's Configure option in Home Assistant (Settings > Devices & Services > Local Intesis > Configure).

## Troubleshooting

- Connection failed: check the IP address is correct and the gateway is on the same network
- Authentication error: reset your gateway's password using the Intesis mobile app
- No devices found: make sure your AC is paired with the gateway
- Wrong fan speeds or missing features: some gateways report capabilities differently. Try updating your gateway's firmware

## Debug logging

Add this to your configuration.yaml:

```
logger:
  default: warning
  logs:
    custom_components.local_intesis: debug
```


