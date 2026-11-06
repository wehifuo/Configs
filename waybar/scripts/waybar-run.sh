#!/usr/bin/env bash
# Единая точка запуска Waybar.
# Выбирает конфиг и CSS по файлу активной темы ~/.config/waybar/.theme
# Тема dark1 -> тонкая полоса (config.thin.jsonc + thin.css).

theme="$(cat "$HOME/.config/waybar/.theme" 2>/dev/null || echo dark1)"

case "$theme" in
    dark1)
        config="config.thin.jsonc"
        style="thin.css"
        ;;
    main)
        config="config.jsonc"
        style="main.css"
        ;;
    dark2|teeth)
        config="config.jsonc"
        style="dark.css"
        ;;
    *)
        config="config.thin.jsonc"
        style="thin.css"
        ;;
esac

exec /usr/bin/waybar \
    -c "$HOME/.config/waybar/$config" \
    -s "$HOME/.config/waybar/$style"
