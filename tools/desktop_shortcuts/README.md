# Desktop Shortcuts

This is an additive setup that does not modify existing compose or Conky config files.

## What it adds

- `Limo Compose Up.desktop`
- `Limo Compose Down.desktop`
- `Limo Compose Logs.desktop`
- `Limo Compose Conky Restart.desktop`
- `~/scripts/check_compose_services.sh` (for Conky status display)
- `~/scripts/start_compose_conky.sh` (starts the dedicated Conky instance)
- `~/.config/conky/limo-compose.conkyrc` (center-screen Conky config)
- `~/.config/autostart/limo-compose-conky.desktop` (auto-start)

## Install

Run:

```bash
bash tools/desktop_shortcuts/install_desktop_shortcuts.sh
```

This writes launchers to:

- `~/Desktop`
- `~/.local/share/applications`
