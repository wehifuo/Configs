#!/bin/bash

# 1. Получаем погоду с цветами
RAW_WEATHER=$(curl -s "wttr.in/?0&Q")

# 2. Переводим ESC-последовательности в Pango-разметку Waybar
# - \x1b\[38;5;226m  -> Желтый (Солнце)
# - \x1b\[38;5;154m  -> Зеленый (Температура/данные)
# - \x1b\[0m         -> Сброс цвета
# - \x1b\[1m         -> Жирный шрифт
TEXT_WEATHER=$(echo "$RAW_WEATHER" | sed \
    -e 's/\x1b\[38;5;226m/<span foreground="#ffff00">/g' \
    -e 's/\x1b\[38;5;154m/<span foreground="#a7ff57">/g' \
    -e 's/\x1b\[0m/<\/span>/g' \
    -e 's/\x1b\[1m/<b>/g' \
    -e 's/\x1b\[22m/<\/b>/g')

# 3. Экранируем символы для корректного JSON-формата
TEXT_WEATHER=$(echo "$TEXT_WEATHER" | sed 's/\\/\\\\/g' | sed ':a;N;$!ba;s/\n/\\n/g' | sed 's/"/\\"/g')

# 4. Выводим результат
echo "{\"text\": \"🌤️\", \"tooltip\": \"${TEXT_WEATHER}\"}"

