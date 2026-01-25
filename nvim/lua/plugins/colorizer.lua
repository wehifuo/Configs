return {
    "catgoose/nvim-colorizer.lua",
    event = "BufReadPre",
    opts = { -- set to setup table-- Звездочка "*" означает "все типы файлов"
	    filetypes = { "*" }, 
    
	    user_default_options = {
			RGB      = true,         -- #RGB hex коды
			RRGGBB   = true,         -- #RRGGBB hex коды
			names    = false,        -- Подсветка слов (например, "Blue"). Лучше false, чтобы не красить обычный текст
			RRGGBBAA = true,         -- #RRGGBBAA hex коды
			AARRGGBB = true,         -- 0xAARRGGBB hex коды
			rgb_fn   = true,         -- CSS rgb() и rgba() функции
			hsl_fn   = true,         -- CSS hsl() и hsla() функции
			css      = true,         -- Парсить все CSS-подобные цвета
			css_fn   = true,         -- Парсить все CSS-функции
		 -- Важно для файлов, которые не являются CSS (например, .lua, .js, .txt)
			mode = "background",     -- "background" (весь текст), "foreground" (только буквы) или "virtualtext"
      
      -- Если вы используете Tailwind CSS
			tailwind = true,         -- Поддержка Tailwind цветов в любых файлах
		},
	},

}
