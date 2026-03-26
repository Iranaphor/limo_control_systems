# Limo Control Systems

A ROS 2 + Docker workspace for running and developing LIMO robot software.

## What this repo is

This repository combines:
- A prebuilt LIMO platform stack (`limo_drivers`, `zenoh_router`, `filebrowser`)
- A local research/dev container (`limo_research`) for editing, building, and testing ROS 2 packages
- Shared external packages and your local robot packages in one place

In short: it is one workspace to run the robot services and do development side-by-side.

## Repo layout (high level)

- `docker-compose.yml`: Main multi-container setup
- `Dockerfile`: Build for the `limo_research` dev container
- `start.sh`: Startup logic inside the dev container
- `external/`: Upstream/shared ROS 2 packages and platform code
- `local/`: Your custom ROS 2 packages for this robot/project
- `tools/`: Optional helper tools (desktop shortcuts + compose status Conky add-on)

## Main containers

- `limo_drivers`: Core LIMO runtime and navigation launches
- `zenoh_router`: ROS 2 DDS bridge/router
- `filebrowser`: Web file browser
- `limo_research`: Interactive dev environment with mounted source code

## .env configuration

Create a `.env` file at the repo root to override compose variables.

Variables used by this repository:

- `ROBOT_NAME`: Hostname used inside `limo_drivers` (example: `LIMO-0001`)
- `DISPLAY`: X11 display target. Use `:0` for desktop X11, or `:1` for noVNC/virtual desktop (default: `:0`)
- `ROS_DOMAIN_ID`: ROS 2 DDS domain ID (default: `0`)
- `MAP_YAML_FILE`: Required map YAML for the Nav2 map server/localization launch. Use `external/environment_template/config/map/map.yaml`.
- `TMULE_FILE`: Optional tmule config path for `limo_research` (default: empty)
- `SLEEP_TIME`: How long `limo_research` stays alive (default: `infinity`)

Example `.env`:

```dotenv
ROBOT_NAME=LIMO-0001
DISPLAY=:0
ROS_DOMAIN_ID=0
MAP_YAML_FILE=external/environment_template/config/map/map.yaml
TMULE_FILE=
SLEEP_TIME=infinity
```

## Quick start

Run the installer once from the repo root:

```bash
sudo bash tools/desktop_shortcuts/install_desktop_shortcuts.sh
```

This sets up the Conky status widget and places shortcuts on the desktop. From then on use the desktop icons:

- **Research Docker On** — start all services
- **Research Docker Off** — stop all services
- **Remove Research Tools** — uninstall the shortcuts and Conky widget (with confirmation prompt)

## Notes

- This repo is intended for Linux with Docker and ROS 2 workflows.
- Service/package-level details are documented in the README files inside each subfolder.
