return {
	{
		"numToStr/Comment.nvim",
		opts = {
			-- add any options here
		},
	},

	{
		"nvim-mini/mini.surround",
		opts = {

			custom_surroundings = nil,

			highlight_duration = 500,

			mappings = {
				add = "sa", -- Add surrounding in Normal and Visual modes
				delete = "sd", -- Delete surrounding
				find = "sf", -- Find surrounding (to the right)
				find_left = "sF", -- Find surrounding (to the left)
				highlight = "sh", -- Highlight surrounding
				replace = "sr", -- Replace surrounding

				suffix_last = "l", -- Suffix to search with "prev" method
				suffix_next = "n", -- Suffix to search with "next" method
			},

			n_lines = 20,

			respect_selection_type = false,

			search_method = "cover",

			silent = false,
		},
	},
	{
		"windwp/nvim-autopairs",
		event = "InsertEnter",
		config = true,
		-- use opts = {} for passing setup options
		-- this is equivalent to setup({}) function
	},
	{
		"Wansmer/treesj",
		keys = {
			"<space>m",
			"<space>j",
			"<space>s",
		},
		dependencies = { "nvim-treesitter/nvim-treesitter" }, -- if you install parsers with `nvim-treesitter`
		config = function()
			require("treesj").setup({ --[[ your config ]]
			})
		end,
	},
	{
		{
			"ThePrimeagen/vim-be-good",
			cmd = "VimBeGood",
		},
	},
}
