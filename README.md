# Ecovacs X12S EU (experimental)

Private custom integration based on [Home Assistant Core 2026.11.0](https://github.com/home-assistant/core/tree/2026.11.0/homeassistant/components/ecovacs), using its original license and pinned dependencies. Adds a process-local alias for EU X12S `sdr8vw` to US `k5azjg` without changing the reported device class or writing to site-packages. Native support takes precedence. EU firmware compatibility is unverified; some entities may be incorrect.

## Installation
Back up HA. Install via a private-repository-capable HACS variant (standard HACS does not support private repositories), or download the private repo ZIP while logged into GitHub and copy `custom_components/ecovacs` into HA `/config/custom_components/`. Restart Core. Keep the existing Ecovacs config entry. Check logs for `Experimental EU X12S profile alias installed` and test read-only sensors before commands. Do not expose credentials or device IDs in issues.

## Updates and rollback
This is a snapshot of HA 2026.11.0, not automatically synced with Core. Review compatibility before upgrading HA. Remove `/config/custom_components/ecovacs` (or uninstall in HACS), then restart Core to restore the built-in integration. Do not delete the config entry. Minimum target HA 2026.11.0; newer versions unverified. English strings included; upstream build-time translation references may not resolve in a custom integration.
