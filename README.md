# Assist Traces

Assist Traces is a custom [Home Assistant](https://www.home-assistant.io/) integration that records full Assist pipeline runs for building fine-tuning datasets.

[![Add to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ConstructorFleet&repository=Assist-Tuning&category=integration)
[![Add to Home Assistant](https://my.home-assistant.io/badges/add-integration.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=assist_traces)

## Installation

### HACS (Recommended)

Use the badge above to add this repository to [HACS](https://hacs.xyz/) and install the **Assist Traces** integration.

### Manual installation

1. Copy the `custom_components/assist_traces` directory to your Home Assistant `custom_components` folder.
2. Restart Home Assistant.
3. From the UI, go to **Settings** → **Devices & Services** → **Add Integration** and search for **Assist Traces**.

## Development

### Building

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[test]
```

### Running

After installation, add the integration from Home Assistant's UI as described above.

### Testing

Run linting and tests with:

```bash
ruff check .
pytest
```
