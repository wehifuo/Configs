#!/bin/bash
# Показать/скрыть Waybar, всегда с конфигом активной темы.
if pgrep -x "waybar" > /dev/null;
then
    systemctl --user stop waybar.service >/dev/null 2>&1
    pkill -x waybar >/dev/null 2>&1
else
    systemctl --user start waybar.service >/dev/null 2>&1
fi
