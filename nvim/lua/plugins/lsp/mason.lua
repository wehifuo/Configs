return{
	"mason-org/mason-lspconfig.nvim",
    opts = {
		ensure_installed = {
			"ts_ls",
			"html",
			"tailwindcss",
			"lua_ls",
			"pyright"
		}
	},
    dependencies = {
        { "mason-org/mason.nvim", 
			opts = {
				ui = {
					icons = {
						package_installed = "✓",
						package_pending = "➜",
						package_uninstalled = "✗",
					},
				},
			},
		},
		{
			"neovim/nvim-lspconfig",
		}, 
	},
}
