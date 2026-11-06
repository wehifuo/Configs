#!/bin/bash

STATE="$HOME/.config/waybar/.theme"

restart_waybar() {
    systemctl --user stop waybar.service >/dev/null 2>&1
    pkill -x waybar >/dev/null 2>&1
    sleep 0.2
    systemctl --user start waybar.service >/dev/null 2>&1
}

case $1 in
    "main")
        hyprctl keyword general:col.active_border "rgba(8990A4ff) rgba(cc7788ff) rgba(8990A4ff) 130deg"
        hyprctl hyprpaper wallpaper "eDP-1,/home/anton/Downloads/old_tg/wallpaper-arch1.jpg"

 		ln -sf ~/.config/waybar/main.css ~/.config/waybar/style.css
        echo main > "$STATE"
        restart_waybar
        ;;
        
    "dark1")
        hyprctl keyword general:col.active_border "rgba(e7e7e7ff)"
        hyprctl hyprpaper wallpaper "eDP-1,/home/anton/Downloads/wallpaper1.jpg"

		ln -sf ~/.config/waybar/thin.css ~/.config/waybar/style.css
        echo dark1 > "$STATE"
        restart_waybar
        ;;

    "dark2")
        hyprctl keyword general:col.active_border "rgba(e7e7e7ff)"
        hyprctl hyprpaper wallpaper "eDP-1,/home/anton/Downloads/wallpaper2.jpg"

		ln -sf ~/.config/waybar/dark.css ~/.config/waybar/style.css
        echo dark2 > "$STATE"
        restart_waybar
        ;;

    "teeth")
        hyprctl keyword general:col.active_border "rgba(e7e7e7ff)"
        hyprctl hyprpaper wallpaper "eDP-1,/home/anton/Downloads/teeth_wallpaper.jpg"

		ln -sf ~/.config/waybar/dark.css ~/.config/waybar/style.css
        echo teeth > "$STATE"
        restart_waybar
        ;;

    "win")
        hyprctl hyprpaper wallpaper "eDP-1,/home/anton/Downloads/wallpaper4.jpg"

        ;;
esac


# systemctl --user restart waybar.service
