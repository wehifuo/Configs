# Control Center для Hyprland

Полноценный центр управления Wi-Fi и Bluetooth в стиле Orbit: GTK4 + `gtk4-layer-shell`, без AGS/Eww и без блокирующих вызовов в UI-потоке.

![pages](https://img.shields.io/badge/pages-overview%20%C2%B7%20wifi%20%C2%B7%20bluetooth-f2f2f2)

## Что умеет

### Wi-Fi (`nmcli` + `rfkill`)
- Быстрый On/Off через `nmcli radio wifi`.
- Текущая сеть, SSID, динамическая иконка сигнала 0–100 %, IPv4 и тип защиты.
- Список сетей с сортировкой по силе сигнала, метками «открытая/закрытая» и «сохранено».
- Сканирование по кнопке с индикатором загрузки (не блокирует интерфейс).
- Подключение: открытые сети — сразу, защищённые — inline-поле пароля с проверкой и человекочитаемой ошибкой. Сохранённые сети подключаются без повторного ввода пароля.
- «Отключиться» и «Забыть» (двойное подтверждение) для активной сети.
- Автообновление статуса, пока панель открыта.

### Bluetooth (`bluetoothctl` / BlueZ)
- Power On/Off адаптера.
- Статус адаптера, количество подключённых устройств, alias и MAC.
- Разделы «Подключённые», «Сопряжённые», «Рядом».
- Connect / Disconnect, Pair, Trust, Remove (с подтверждением).
- Процент батареи, если устройство отдаёт `Battery Percentage` через BlueZ.
- Scan On/Off на 20 секунд с живым обновлением списка.
- Режим видимости компьютера (`discoverable`).

### UX / Wayland
- Окно — layer-shell поверхность `control-center` в правом верхнем углу.
- Полноэкранный прозрачный слой-перехватчик: клик мимо панели закрывает её.
- `Esc` закрывает панель.
- Hyprland blur для панели через `layerrule`.
- Внутренние тосты + `notify-send` при ошибках.
- Один экземпляр приложения (D-Bus), повторный запуск переключает/навигацию, а не плодит процессы.
- Все внешние команды выполняются асинхронно через `Gio.Subprocess`; UI не подвисает.

## Архитектура

```
~/.config/control-center/
├── main.py                 # entry point + LD_PRELOAD re-exec для layer-shell
├── launch.sh               # единая точка запуска для Hyprland/Waybar
├── style.css               # монохромная Orbit-тема
├── assets/clown-bw.png     # чёрно-белый клоун для заголовка
├── waybar-bluetooth.py     # JSON-модуль Waybar
└── cc/
    ├── app.py              # Gtk.Application, layer-shell, click-away, тосты, single-instance
    ├── pages.py            # Overview / Wi-Fi / Bluetooth, строки списков
    ├── widgets.py          # общие GTK-виджеты и хелперы
    ├── nm.py               # async NetworkManager backend (nmcli)
    ├── bt.py               # async BlueZ backend (bluetoothctl)
    └── runner.py           # Gio.Subprocess: run / run_parallel / notify
```

Почему не AGS/Eww: в системе уже используется Waybar, а `gtk4`, `gtk4-layer-shell` и `python-gobject` установлены. Standalone GTK4-приложение не тянет новый рантайм и даёт нативный layer-shell, blur и клавиатурный захват.

## Зависимости

Всё уже установлено в этой системе. Для чистой Arch:

```bash
sudo pacman -S --needed \
    networkmanager bluez bluez-utils \
    gtk4 gtk4-layer-shell python python-gobject \
    libnotify waybar
```

`rfkill` входит в `util-linux` и уже есть в базовой системе.

Шрифт иконок: **JetBrainsMono Nerd Font** (уже установлен). Если нет:

```bash
sudo pacman -S --needed ttf-jetbrains-mono-nerd
```

Проверка:

```bash
command -v nmcli bluetoothctl rfkill notify-send
systemctl is-active NetworkManager bluetooth
python3 -c "import gi; gi.require_version('Gtk4LayerShell','1.0'); print('layer-shell ok')"
```

## Запуск

```bash
# обзор
~/.config/control-center/launch.sh

# сразу страница Wi-Fi / Bluetooth
~/.config/control-center/launch.sh --page wifi
~/.config/control-center/launch.sh --page bluetooth

# только показать (не переключать)
~/.config/control-center/launch.sh --page wifi --show

# закрыть, если открыто
~/.config/control-center/launch.sh --toggle
```

Прямой запуск тоже работает:

```bash
python3 ~/.config/control-center/main.py --page wifi
```

`main.py` сам перезапускается с `LD_PRELOAD=/usr/lib/libgtk4-layer-shell.so`, потому что gtk4-layer-shell должен быть слинкован раньше `libwayland-client`. `launch.sh` делает то же самое сразу, без лишнего exec.

## Интеграция с Hyprland

В `~/.config/hypr/hyprland.lua` уже добавлены:

```lua
-- Панель почти непрозрачная (rgba 0.94), поэтому blur для неё не обязателен.
-- Оставляем только отключение анимации у полноэкранного click-away слоя.
hl.layer_rule({
    name = "control-center-overlay",
    match = { namespace = "^control-center-overlay$" },
    no_anim = true,
})

-- хоткей
hl.bind(
    mainMod .. " + SHIFT + W",
    hl.dsp.exec_cmd("~/.config/control-center/launch.sh --toggle"),
    { description = "Control Center (Wi-Fi / Bluetooth)" }
)
```

Применить без перезапуска сессии:

```bash
hyprctl reload
hyprctl configerrors   # должно быть пусто
hyprctl layers         # появятся namespace control-center / control-center-overlay
```

Если используете классический `hyprland.conf`, эквивалент:

```ini
layerrule = noanim, ^control-center-overlay$

bind = SUPER SHIFT, W, exec, ~/.config/control-center/launch.sh --toggle
```

Если позже захотите вернуть полупрозрачность и blur, сделайте панель полупрозрачной в `style.css` и добавьте:

```ini
layerrule = blur, ^control-center$
layerrule = ignorealpha 0.15, ^control-center$
```

Панель не является обычным окном, поэтому `windowrule`/`float` ей не нужны. Она сама позиционируется layer-shell-якорем `TOP | RIGHT` с отступами 10/12 px.

## Интеграция с Waybar

В `config.thin.jsonc` и `config.jsonc` добавлен модуль `custom/bluetooth` и клики у `network`:

```jsonc
"modules-right": [
    "custom/spotify",
    "backlight",
    "pulseaudio",
    "custom/bluetooth",
    "network",
    "battery"
],

"custom/bluetooth": {
    "exec": "$HOME/.config/control-center/waybar-bluetooth.py",
    "return-type": "json",
    "interval": 5,
    "tooltip": true,
    "on-click": "$HOME/.config/control-center/launch.sh --page bluetooth"
},

"network": {
    // ...
    "on-click": "$HOME/.config/control-center/launch.sh --page wifi",
    "on-click-right": "$HOME/.config/control-center/launch.sh --page bluetooth"
}
```

Иконка в баре показывает:
- `󰂯` — адаптер включён, подключений нет;
- `󰂯 N` — N подключённых устройств;
- `󰂲` — Bluetooth выключен/недоступен.

Tooltip содержит имена подключённых устройств и заряд, если он отдаётся профилем.

После правки:

```bash
systemctl --user restart waybar.service
# или
killall -SIGUSR2 waybar
```

CSS-блоки `#custom-bluetooth` добавлены во все три темы: `thin.css`, `dark.css`, `main.css`.

## Как это не блокирует UI

- `nmcli` и `bluetoothctl` запускаются через `Gio.SubprocessLauncher` + `communicate_utf8_async`; GTK main loop продолжает обрабатывать кадры.
- Долгие операции имеют таймауты и могут быть прерваны (например, повторный клик по «Остановить» у Bluetooth-скана вызывает `force_exit()`).
- Список Wi-Fi обновляется из кэша (`--rescan no`) каждые 5 секунд, полный скан — только по кнопке.
- Информация об устройствах BlueZ собирается параллельно (`run_parallel`), а не последовательно.
- Из окружения дочерних процессов удаляется `LD_PRELOAD`, чтобы preload layer-shell не влиял на `nmcli`, `bluetoothctl` и `notify-send`.

## Ошибки и уведомления

- Неверный пароль → поле пароля раскрывается снова с подсветкой ошибки + toast.
- Нет прав / rfkill / таймаут / адаптер выключен → короткое сообщение в toast и `notify-send`.
- Действия, требующие разрушения данных (forget / remove), просят повторное нажатие в течение 3 секунд.
- Ошибки не залипают в UI: тост исчезает через 4 секунды.

## Настройка внешнего вида

Тема монохромная, под чёрно-белое окружение: background `#0b0b0c`, surface `#141415`, текст `#f2f2f2`, акцент — белый `#f2f2f2`. Панель — `rgba(13,13,14,0.94)`: лёгкая прозрачность без «стеклянного» прямоугольника. Меняйте `@define-color` и alpha в начале `style.css`. Размер панели — `PANEL_WIDTH` / `PANEL_HEIGHT` в `cc/app.py` (по умолчанию 410×640).

Клоун в заголовке — `assets/clown-bw.png`, чёрно-белый PNG с прозрачностью. Если захотите заменить его на ASCII-арт из Neovim: положите картинку/текст в `assets/` и поправьте блок `_page_header` в `cc/pages.py`.

## Диагностика

```bash
# запустить вручную и смотреть stderr
python3 ~/.config/control-center/main.py --page wifi

# проверить layer surfaces и blur
hyprctl layers
hyprctl configerrors

# проверить бэкенды отдельно
nmcli -t -f IN-USE,SSID,SIGNAL,SECURITY,DEVICE device wifi list --rescan yes
bluetoothctl show
bluetoothctl devices
bluetoothctl info <MAC>

# модуль Waybar
~/.config/control-center/waybar-bluetooth.py
```

Если панель появилась как обычное окно, а не layer surface — проверьте, что запуск идёт через `launch.sh` (или `main.py`, который сам делает re-exec) и что в `LD_PRELOAD` есть `/usr/lib/libgtk4-layer-shell.so`. Альтернатива для отладки:

```bash
LD_PRELOAD=/usr/lib/libgtk4-layer-shell.so python3 ~/.config/control-center/main.py
```
