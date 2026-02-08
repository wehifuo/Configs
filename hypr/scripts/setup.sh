#!/bin/bash

hyprctl dispatch exec "[workspace 3 silent] firefox"
hyprctl dispatch exec "[workspace 4 silent] ~/Downloads/Telegram/Telegram"
hyprctl dispatch exec "[workspace 2 silent] kitty -e 'nvim'"
