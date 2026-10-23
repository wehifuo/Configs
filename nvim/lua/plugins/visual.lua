-- для красивого отображения терминала и уведомлений

return {
	-- {
	-- 	"VonHeikemen/fine-cmdline.nvim",
	-- 	dependencies = {
	-- 		"MunifTanjim/nui.nvim",
	-- 	},
	-- 	event = "VeryLazy",
	-- 	opts = {
	-- 		cmdline = {
	-- 			enable_keymaps = true,
	-- 			smart_history = true,
	-- 		},
	-- 		popup = {
	-- 			position = {
	-- 				row = "20%",
	-- 				col = "50%",
	-- 			},
	-- 			size = {
	-- 				width = "35%",
	-- 			},
	-- 			border = {
	-- 				style = "rounded",
	-- 			},
	-- 			win_options = {
	-- 				winhighlight = "Normal:Normal,FloatBorder:FloatBorder",
	-- 			},
	-- 		},
	-- 	},
	-- 	config = function(_, opts)
	-- 		require("fine-cmdline").setup(opts)
	--
	-- 		vim.keymap.set("n", ":", "<cmd>FineCmdline<CR>", { desc = "Cmdline по центру" })
	--
	-- 		-- vim.keymap.set("n", "/", function()
	-- 		-- 	require("fine-cmdline").open({ default_value = "/" })
	-- 		-- end, { desc = "Поиск по центру" })
	-- 	end,
	-- },
	{
		"rcarriga/nvim-notify",
		event = "VeryLazy",
		config = function()
			local notify = require("notify")

			notify.setup({
				stages = "fade",
				timeout = 2500,
				render = "compact",
				max_width = 40,
				max_height = 3,
			})

			vim.notify = notify
		end,
	},
	{
		"nvim-lualine/lualine.nvim",
		dependencies = { "nvim-tree/nvim-web-devicons" },
		event = "VeryLazy",
		opts = {
			options = {
				theme = "auto",
				component_separators = { left = "│", right = "│" },
				section_separators = { left = "", right = "" },
				disabled_filetypes = { statusline = { "neo-tree", "alpha","dashboard" } },
			},
			sections = {
				lualine_a = { "mode" },
				lualine_b = { "branch", "diff" },
				lualine_c = { { "filename", path = 1 } },
				lualine_x = { "diagnostics" },
				lualine_y = { "progress" },
				lualine_z = { "location" },
			},
		},
	},
	{
		"akinsho/bufferline.nvim",
		version = "*",
		dependencies = "nvim-tree/nvim-web-devicons",
		event = "VeryLazy",
		keys = {
			{ "<A-Right>", "<cmd>BufferLineCycleNext<CR>", desc = "Следующий буфер" },
			{ "<A-Left>", "<cmd>BufferLineCyclePrev<CR>", desc = "Предыдущий буфер" },
		},
		opts = {
			options = {
				mode = "tabs",
				separator_style = "thin",
				diagnostics = "nvim_lsp",
				always_show_bufferline = false,
				show_buffer_close_icons = false,
				show_close_icon = false,
				numbers = "ordinal", 
				number_style = "superscript", -- none
				offsets = {
					{
						filetype = "neo-tree",
						text = "File Explorer",
						text_align = "left",
						separator = true,
					},
				},
			},
		},
	},
}
