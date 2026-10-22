------------------
---- MONITORS ----
------------------

-- See https://wiki.hypr.land/configuring/core/monitors/
hl.monitor({
    output   = "eDP-1",
    mode     = "1920x1080@60",
    position = "0x0",
    scale    = "1",
})


---------------------
---- MY PROGRAMS ----
---------------------

local terminal    = "kitty"
local fileManager = "kitty yazi"
local menu        = "rofi -show drun -modi drun,calc"
local browser     = "firefox"

local mainMod     = "SUPER"
local step  = 20

-------------------
---- AUTOSTART ----
-------------------

-- See https://wiki.hypr.land/configuring/core/autostart/
hl.on("hyprland.start", function()
    hl.exec_cmd("wl-paste --type text --watch cliphist store -max-items 40")
    hl.exec_cmd("wl-paste --type image --watch cliphist store -max-items 40")
    hl.exec_cmd("hyprpaper")
    hl.exec_cmd("hypridle & ~/.config/hypr/scripts/low-battery.sh")
    hl.exec_cmd("~/.config/hypr/scripts/setup.sh")
    hl.exec_cmd("hyprpm reload -n")
    -- hl.exec_cmd("hyprpm enable Hyprspace")
end)

-------------------------------
---- ENVIRONMENT VARIABLES ----
-------------------------------

-- See https://wiki.hypr.land/configuring/core/environment-variables/
hl.env("XCURSOR_SIZE", "20")
hl.env("HYPRCURSOR_SIZE", "20")


-----------------------
----- PERMISSIONS -----
-----------------------

-- See https://wiki.hypr.land/configuring/core/advanced-configuration/permissions/
-- Please note permission changes here require a Hyprland restart and are not applied on-the-fly
-- for security reasons

-- hl.config({
--   ecosystem = {
--     enforce_permissions = true,
--   },
-- })

-- hl.permission("/usr/(bin|local/bin)/grim", "screencopy", "allow")
-- hl.permission("/usr/(lib|libexec|lib64)/xdg-desktop-portal-hyprland", "screencopy", "allow")
-- hl.permission("/usr/(bin|local/bin)/hyprpm", "plugin", "allow")


-----------------------
---- LOOK AND FEEL ----
-----------------------

-- Refer to https://wiki.hypr.land/configuring/core/config-options/
hl.config({
    general = {
        gaps_in  = 4,
        gaps_out = 4,

        border_size = 1,

        col = {
            active_border   = "rgba(e7e7e7ff)",
            inactive_border = "rgba(595959aa)",
        },

        resize_on_border = true,
        allow_tearing    = false,

        layout = "dwindle",
    },

    decoration = {
        rounding       = 10,
        rounding_power = 2,

        active_opacity   = 1.0,
        inactive_opacity = 0.76,

        shadow = {
            enabled      = true,
            range        = 4,
            render_power = 3,
            color        = "rgba(1a1a1aee)",
        },

        blur = {
            enabled           = true,
            size              = 3,
            passes            = 1,
            new_optimizations = true, -- ??????????
            vibrancy          = 0.1696,
        },
    },

    animations = {
        enabled = true,
    },
})

-- Default curves, see https://wiki.hypr.land/configuring/core/animations/
hl.curve("easeOutQuint",   { type = "bezier", points = { {0.23, 1},    {0.32, 1} } })
hl.curve("easeInOutCubic", { type = "bezier", points = { {0.65, 0.05}, {0.36, 1} } })
hl.curve("linear",         { type = "bezier", points = { {0, 0},       {1, 1}    } })
hl.curve("almostLinear",   { type = "bezier", points = { {0.5, 0.5},   {0.75, 1} } })
hl.curve("quick",          { type = "bezier", points = { {0.15, 0},    {0.1, 1}  } })

-- Default animations
hl.animation({ leaf = "global",        enabled = true, speed = 10,   bezier = "default" })
hl.animation({ leaf = "border",        enabled = true, speed = 5.39, bezier = "easeOutQuint" })
hl.animation({ leaf = "windows",       enabled = true, speed = 4.79, bezier = "easeOutQuint" })
hl.animation({ leaf = "windowsIn",     enabled = true, speed = 4.1,  bezier = "easeOutQuint", style = "popin 87%" })
hl.animation({ leaf = "windowsOut",    enabled = true, speed = 1.49, bezier = "linear",       style = "popin 87%" })
hl.animation({ leaf = "fadeIn",        enabled = true, speed = 1.73, bezier = "almostLinear" })
hl.animation({ leaf = "fadeOut",       enabled = true, speed = 1.46, bezier = "almostLinear" })
hl.animation({ leaf = "fade",          enabled = true, speed = 3.03, bezier = "quick" })
hl.animation({ leaf = "layers",        enabled = true, speed = 3.81, bezier = "easeOutQuint" })
hl.animation({ leaf = "layersIn",      enabled = true, speed = 4,    bezier = "easeOutQuint", style = "fade" })
hl.animation({ leaf = "layersOut",     enabled = true, speed = 1.5,  bezier = "linear",       style = "fade" })
hl.animation({ leaf = "fadeLayersIn",  enabled = true, speed = 1.79, bezier = "almostLinear" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 1.39, bezier = "almostLinear" })
hl.animation({ leaf = "workspaces",    enabled = true, speed = 1.94, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "workspacesIn",  enabled = true, speed = 1.21, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "workspacesOut", enabled = true, speed = 1.94, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "zoomFactor",    enabled = true, speed = 7,    bezier = "quick" })



-- Чтобы убрать рамки когда одно окно на экране
hl.workspace_rule({ workspace = "w[tv1]", gaps_out = 1, gaps_in = 1 })


-- See https://wiki.hypr.land/configuring/layouts/master-layout/ for more
hl.config({
    master = {
        new_status = "master",
    },
})

hl.config({
    dwindle = {
        preserve_split = true,
    },
})

---------------
---- INPUT ----
---------------

hl.config({
    input = {
        kb_layout  = "us,ru",
        kb_variant = "",
        kb_model   = "",
        kb_options = "grp:alt_shift_toggle",
        kb_rules   = "",

        repeat_delay = 200,
        repeat_rate  = 50,

        follow_mouse  = 1,
        sensitivity   = 0.1,
        scroll_factor = 1.5,

        touchpad = {
            natural_scroll       = true,
            disable_while_typing = true,
        },
    },
})

hl.gesture({
    fingers   = 3,
    direction = "horizontal",
    action    = "workspace",
})

hl.device({
    name        = "epic-mouse-v1",
    sensitivity = -0.5,
})


---------------------
---- KEYBINDINGS ----
---------------------

-- Swap window
hl.bind(mainMod .. " + left",  hl.dsp.window.swap({ direction = "left" }))
hl.bind(mainMod .. " + right", hl.dsp.window.swap({ direction = "right" }))
hl.bind(mainMod .. " + up",    hl.dsp.window.swap({ direction = "up" }))
hl.bind(mainMod .. " + down",  hl.dsp.window.swap({ direction = "down" }))

-- Core apps and actions
hl.bind(mainMod .. " + Q", hl.dsp.exec_cmd(terminal))
hl.bind(mainMod .. " + C", hl.dsp.window.close())
hl.bind(mainMod .. " + M", hl.dsp.exec_cmd("systemctl suspend"))
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd(fileManager))
hl.bind(mainMod .. " + B", hl.dsp.exec_cmd(browser))
hl.bind(mainMod .. " + P", hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + R", hl.dsp.exec_cmd("pkill rofi || " .. menu))

hl.bind(mainMod .. " + D",  function() hl.plugin.overview.toggle() end)
hl.bind("SUPER + TAB", function() hl.plugin.overview.toggle() end, { description = "Toggle Hyprspace overview" })
-- hl.bind(mainMod .. " + P", hl.dsp.window.pseudo())
hl.bind(mainMod .. " + G", hl.dsp.layout("togglesplit"))

hl.bind(mainMod .. " + T", hl.dsp.exec_cmd("Telegram"))
hl.bind(mainMod .. " + W", hl.dsp.exec_cmd("~/.config/waybar/scripts/toogle.sh"))
hl.bind(mainMod .. " + SHIFT + B", hl.dsp.exec_cmd("hyprlock"))

-- Clipboard history
hl.bind(mainMod .. " + V", hl.dsp.exec_cmd('cliphist list | head -n 10 | rofi -dmenu -display-columns 2 -p "Clipboard" -config ~/.config/rofi/config.rasi | cliphist decode | wl-copy'))

-- Screenshots
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.exec_cmd("env HYPRSHOT_DIR=/home/anton/Screenshots hyprshot -m region"))

-- Fullscreen modes
hl.bind(mainMod .. " + F", hl.dsp.window.fullscreen({ mode = 0 }))
hl.bind(mainMod .. " + SHIFT + F", hl.dsp.window.fullscreen({ mode = 1 }))
hl.bind(mainMod .. " + CTRL + F", hl.dsp.exec_cmd("hyprctl dispatch fullscreenstate 0 2"))

-- Move focus
hl.bind(mainMod .. " + H", hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + L", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + J", hl.dsp.focus({ direction = "down" }))
hl.bind(mainMod .. " + K", hl.dsp.focus({ direction = "up" }))

-- Resize active window
hl.bind(mainMod .. " + SHIFT + L", hl.dsp.window.resize({ x = step, y = 0, relative = true}), { repeating = true })
hl.bind(mainMod .. " + SHIFT + H", hl.dsp.window.resize({ x = -step, y = 0, relative = true}), { repeating = true })
hl.bind(mainMod .. " + SHIFT + K", hl.dsp.window.resize({ x = 0, y = -step, relative = true}), { repeating = true })
hl.bind(mainMod .. " + SHIFT + J", hl.dsp.window.resize({ x = 0, y = step, relative = true}), { repeating = true })

-- Switch workspaces 1-10
for i = 1, 10 do
    local key = i % 10
    hl.bind(mainMod .. " + " .. key, hl.dsp.focus({ workspace = i }))
    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = i }))
end

hl.bind("ALT + TAB", hl.dsp.focus({ workspace = "previous" }))

-- Special workspace (scratchpad)
-- hl.bind(mainMod .. " + S", hl.dsp.workspace.toggle_special("magic"))
-- hl.bind(mainMod .. " + SHIFT + S", hl.dsp.window.move({ workspace = "special:magic" }))

-- Scroll through existing workspaces
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up",   hl.dsp.focus({ workspace = "e-1" }))

-- Move/resize windows with mouse dragging
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Multimedia keys
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 4%+"), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 4%-"),      { locked = true, repeating = true })
hl.bind("XF86AudioMute",        hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),     { locked = true, repeating = true })
hl.bind("XF86AudioMicMute",     hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"),   { locked = true, repeating = true })
hl.bind("XF86MonBrightnessUp",  hl.dsp.exec_cmd("brightnessctl set 4%+"),                          { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown",hl.dsp.exec_cmd("brightnessctl set 4%-"),                          { locked = true, repeating = true })

-- Playerctl
hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"),                           { locked = true })
hl.bind("Print",          hl.dsp.exec_cmd("playerctl --player=spotify play-pause"),   { locked = true })
-- hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"),                 { locked = true })
hl.bind("XF86AudioPlay",  hl.dsp.exec_cmd("playerctl play-pause"),                 { locked = true })
hl.bind("XF86AudioPrev",  hl.dsp.exec_cmd("playerctl previous"),                   { locked = true })


--------------------------------
---- WINDOWS AND WORKSPACES ----
--------------------------------
--
-- hl.window_rule({
--     name = "float-kitty-rule",
--     match = { class = "float-kitty" },
--     float = true,
--     size  = "1100 650",
-- })
--

---------------
---- PLUGINS ---
---------------
hl.config({
    plugin = {
        overview = {
            panelColor = "rgba(0, 0, 0, 0.6)",                -- Полностью прозрачная верхняя панель
            panelBorderColor = "rgba(0, 0, 0, 1)",          -- Без рамки у панели
            workspaceActiveBackground = "rgba(255, 255, 255, 0.5)", -- Легкая подсветка активного воркспейса
            workspaceInactiveBackground = "rgba(0, 0, 0, 0.2)",
            workspaceActiveBorder = "rgba(255, 255, 255, 0.8)",
            workspaceInactiveBorder = "rgba(0, 0, 0, 0.1)",
            dragAlpha = 0.8,
            disableBlur = false,

            -- 2. Размеры и макет панели
            panelHeight = 160,                              -- Высота верхней панели с воркспейсами
            panelBorderWidth = 0,                           -- Убираем толщину рамки
            workspaceBorderSize = 2,
            onBottom = false,
            centerAligned = true,                           -- Воркспейсы по центру
            workspaceMargin = 10,
            reservedArea = 0,

            hideBackgroundLayers = false,
            hideTopLayers = true,
            hideOverlayLayers = false,
            hideRealLayers = false,
            drawActiveWorkspace = true,

            -- 4. Сдвиг реальных окон (как на скриншоте)
            affectStrut = true,                             -- Окна сдвигаются вниз под панель
            overrideGaps = true,                            -- Включаем кастомные отступы при открытии
            gapsIn = 7,                                    -- Отступы между окнами в режиме обзора
            gapsOut = 30,                                   -- Внешние отступы (сжиฝают рабочий стол снизу)

            -- 5. Поведение
            autoDrag = true,
            autoScroll = true,
            exitOnClick = true,
            switchOnDrop = true,
            exitOnSwitch = true,
            showNewWorkspace = true,
            showEmptyWorkspace = true,
            showSpecialWorkspace = false,
            disableGestures = false,
            reverseSwipe = false,
            exitKey = "Escape"
        }
    }
})


-- hl.plugin({
--     hyprexpo = {
--         columns          = 3,
--         gap_size         = 10,
--         bg_col           = "rgb(000000)",
--         workspace_method = "first 1",
--         skip_empty       = false,
--         gesture_distance = 300,
--     },
--     hyprscrolling = {
--         column_width             = 0.9,
--         direction                = "right",
--         focus_fit_method         = 1,
--         follow_focus             = true,
--         fullscreen_on_one_column = true,
--     },
-- })
