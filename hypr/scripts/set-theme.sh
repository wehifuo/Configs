#!/bin/bash

case $1 in
    "main")
        hyprctl keyword general:col.active_border "rgba(8990A4ff) rgba(cc7788ff) rgba(8990A4ff) 130deg"
        
        hyprctl hyprpaper wallpaper "eDP-1,/home/anton/Downloads/Telegram_Desktop/wallpaper-arch1.jpg"

 		ln -sf ~/.config/waybar/main.css ~/.config/waybar/style.css
        ;;
        
    "dark1")
        hyprctl keyword general:col.active_border "rgba(e7e7e7ff)"
        hyprctl hyprpaper wallpaper "eDP-1,/home/anton/Downloads/wallpaper1.jpg"

		ln -sf ~/.config/waybar/dark.css ~/.config/waybar/style.css
        ;;

    "dark2")
        hyprctl keyword general:col.active_border "rgba(e7e7e7ff)"
        hyprctl hyprpaper wallpaper "eDP-1,/home/anton/Downloads/wallpaper2.jpg"

		ln -sf ~/.config/waybar/dark.css ~/.config/waybar/style.css
        ;;

    "dark3")
        hyprctl keyword general:col.active_border "rgba(e7e7e7ff)"
        hyprctl hyprpaper wallpaper "eDP-1,/home/anton/Downloads/wallpaper3.jpg"

		ln -sf ~/.config/waybar/dark.css ~/.config/waybar/style.css
        ;;
esac


pkill waybar
sleep 0.2 # Даем системе "выдохнуть"
waybar &> /dev/null &
disown
