return {
	"karb94/neoscroll.nvim",
	event = "VeryLazy",
	config = function()
		local neoscroll = require("neoscroll")

		neoscroll.setup({
			hide_cursor = true, -- Прятать курсор во время полета
			stop_eof = true, 
			respect_scrolloff = false,
			cursor_scrolls_alone = true,
			easing = "quadratic", -- Стиль анимации по умолчанию
		})

		local keymap = {
			["<C-u>"] = function() neoscroll.ctrl_u({ duration = 200 }) end,
			["<C-d>"] = function() neoscroll.ctrl_d({ duration = 200 }) end,
			["<C-b>"] = function() neoscroll.ctrl_b({ duration = 400 }) end,
			["<C-f>"] = function() neoscroll.ctrl_f({ duration = 400 }) end,
			["<C-y>"] = function() neoscroll.scroll(-0.1, { move_cursor = false, duration = 100 }) end,
			["<C-e>"] = function() neoscroll.scroll(0.1, { move_cursor = false, duration = 100 }) end,
			["zt"] = function() neoscroll.zt({ half_win_duration = 200 }) end,
			["zz"] = function() neoscroll.zz({ half_win_duration = 200 }) end,
			["zb"] = function() neoscroll.zb({ half_win_duration = 200 }) end,
		}
		local modes = { "n", "v", "x" }
		for key, func in pairs(keymap) do
			vim.keymap.set(modes, key, func)
		end
	end,
}
