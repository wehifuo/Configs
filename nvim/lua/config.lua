-- vim.api.nvim_set_hl(0, "Normal", {bg = "#1e1e1e"})
-- vim.api.nvim_set_hl(0, "NormalNC", { bg = "#1e1e1e" })
-- vim.api.nvim_set_hl(0, "EndOfBuffer", { bg = "#1e1e1e" })

vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.ignorecase = true
vim.opt.clipboard = "unnamedplus"
vim.opt.tabstop = 3
vim.opt.softtabstop = 3
vim.opt.shiftwidth = 4

vim.opt.signcolumn = "yes"
-- Bootstrap lazy.nvim
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
	local lazyrepo = "https://github.com/folke/lazy.nvim.git"
	local out = vim.fn.system({ "git", "clone", "--filter=blob:none", "--branch=stable", lazyrepo, lazypath })
	if vim.v.shell_error ~= 0 then
		vim.api.nvim_echo({
			{ "Failed to clone lazy.nvim:\n", "ErrorMsg" },
			{ out, "WarningMsg" },
			{ "\nPress any key to exit..." },
		}, true, {})
		vim.fn.getchar()
		os.exit(1)
	end
end
vim.opt.rtp:prepend(lazypath)

-- Make sure to setup `mapleader` and `maplocalleader` before
-- loading lazy.nvim so that mappings are correct.
-- This is also a good place to setup other settings (vim.opt)
vim.g.mapleader = " "
vim.g.maplocalleader = "\\"

-- Setup lazy.nvim
require("lazy").setup({
	spec = {
		-- import your plugins
		{ import = "plugins" },
		{ import = "plugins.lsp" },
	},
	-- Configure any other settings here. See the documentation for more details.
	-- colorscheme that will be used when installing plugins.
	install = { colorscheme = { "habamax" } },
	-- automatically check for plugin updates
	checker = { enabled = true },
})

vim.cmd.colorscheme("flexoki")

vim.api.nvim_create_autocmd("FileType", {
	pattern = "*",
	callback = function()
		vim.opt_local.formatoptions:remove({ "r", "o" })
	end,
})

vim.api.nvim_create_autocmd("BufReadPost", { -- Чтобы сразу работал treesitter
	callback = function()
		vim.treesitter.start()
	end,
})

local my_themes = {
	"default",
	"gruvbox",
	"desert",
	"flexoki",
	"habamax",
	"kanagawa-paper-ink",
	"kanagawa-paper-canvas",
	"lackluster",
	"lackluster-night",
	"lackluster-mint",
	"lackluster-dark",
	"lackluster-hack",
	"mellow",
	"slate",
	"sorbet",
	"unokai",
	"material-darker",
	"material-lighter",
}

vim.api.nvim_create_user_command("MyThemes", function()
	vim.ui.select(my_themes, {
		prompt = "Выберите тему из списка избранных:",
	}, function(choice)
		if choice then
			vim.cmd.colorscheme(choice)
		end
	end)
end, {})

vim.api.nvim_create_autocmd("FileType", {
	pattern = "python",
	callback = function()
		-- Настройка: vertical (вертикально), size (ширина в колонках)
		vim.keymap.set("n", "<leader>r", ':w<CR>:TermExec cmd="python %" direction=vertical size=80<CR>', {
			buffer = true,
			desc = "Run Python file in vertical terminal",
		})
	end,
})

function _G.set_terminal_keymaps()
	local opts = { buffer = 0 }
	-- Esc выход из режима вставки в терминале (чтобы можно было перемещаться)
	vim.keymap.set("t", "<esc>", [[<C-\><C-n>]], opts)
	-- Быстрая навигация между окнами из режима терминала
	vim.keymap.set("t", "<C-h>", [[<Cmd>wincmd h<CR>]], opts)
	vim.keymap.set("t", "<C-j>", [[<Cmd>wincmd j<CR>]], opts)
	vim.keymap.set("t", "<C-k>", [[<Cmd>wincmd k<CR>]], opts)
	vim.keymap.set("t", "<C-l>", [[<Cmd>wincmd l<CR>]], opts)
end

-- Применяем маппинги только при открытии терминала
vim.cmd("autocmd! TermOpen term://* lua set_terminal_keymaps()")
