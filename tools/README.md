# Limo Control Systems Add-ons

These add-ons are non-disruptive and do not alter existing setup.

## Conky compose status

- Script source: `tools/conky_compose_status/check_compose_services.sh`
- Installed script path: `~/scripts/check_compose_services.sh`
- Separate Conky config template: `tools/conky_compose_status/conkyrc.compose_status`
- Installed Conky config path: `~/.config/conky/limo-compose.conkyrc`
- Conky launcher: `~/scripts/start_compose_conky.sh`

This add-on runs as a second Conky instance centered on screen and does not edit your existing `~/.conkyrc`.

If you still want to embed it into existing Conky, a snippet is in:

- `tools/conky_compose_status/conky_text_block.txt`

Snippet:

```conky
${execpi 5 ~/scripts/check_compose_services.sh}
```

## Desktop shortcuts

- Installer: `tools/desktop_shortcuts/install_desktop_shortcuts.sh`
- Docs: `tools/desktop_shortcuts/README.md`

Install with:

```bash
bash tools/desktop_shortcuts/install_desktop_shortcuts.sh
```

The installer also copies the compose status script into `~/scripts/`.
It also creates autostart entry `~/.config/autostart/limo-compose-conky.desktop`.
