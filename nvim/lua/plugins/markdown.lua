return {
	"MeanderingProgrammer/render-markdown.nvim",
	dependencies = { "nvim-treesitter/nvim-treesitter", "nvim-mini/mini.nvim" },
	opts = {
		debounce = 350,

		pipe_table = {
			cell = "trimmed",
		},
	},
}
