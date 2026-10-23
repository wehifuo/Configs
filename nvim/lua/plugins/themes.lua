return {
	-- Тема по умолчанию: должна загружаться сразу
	{
		"rebelot/kanagawa.nvim",
		lazy = false,
		priority = 1000,
	},

	-- Остальные темы грузятся по требованию через :MyThemes
	{
		"kepano/flexoki-neovim",
		name = "flexoki",
		lazy = true,
		priority = 1000,
	},
	{
		"slugbyte/lackluster.nvim",
		lazy = true,
		priority = 1000,
	},
	{
		"thesimonho/kanagawa-paper.nvim",
		lazy = true,
		priority = 1000,
		opts = {},
	},
	{
		"ellisonleao/gruvbox.nvim",
		lazy = true,
		priority = 1000,
		config = true,
		opts = {},
	},
	{ "mellow-theme/mellow.nvim", lazy = true },
	{ "marko-cerovac/material.nvim", lazy = true },
	{ "sainnhe/everforest", lazy = true },
	{ "ribru17/bamboo.nvim", lazy = true },
}
