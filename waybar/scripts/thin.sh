#!/usr/bin/env bash
# Запуск Waybar с отдельным тонким конфигом и темой.
# Старые config.jsonc / dark.css не изменяются.

pkill -x waybar 2>/dev/null
sleep 0.3
setsid waybar \
    -c "$HOME/.config/waybar/config.thin.jsonc" \
    -s "$HOME/.config/waybar/thin.css" \
    >/dev/null 2>&1 &
