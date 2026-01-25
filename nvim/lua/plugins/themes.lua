return {	
  -- Тема Flexoki
	{
            		'kepano/flexoki-neovim', 
		name = 'flexoki',
		priority = 1000, 
	},
	{ 
		"slugbyte/lackluster.nvim",
		lazy = false,
		priority = 1000,
		init = function()
			vim.cmd.colorscheme("lackluster")
			-- vim.cmd.colorscheme("lackluster-hack") -- my favorite
			-- vim.cmd.colorscheme("lackluster-mint")
		end,
	},
	{
	  "thesimonho/kanagawa-paper.nvim",
	  lazy = false,
	  priority = 1000,
	  opts = {},
	},
	{
		"ellisonleao/gruvbox.nvim",
		priority = 1000,
		config = true,
		opts = {},
	}
}
