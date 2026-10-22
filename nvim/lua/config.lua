vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.ignorecase = true
vim.opt.clipboard = "unnamedplus"
vim.opt.tabstop = 3
vim.opt.softtabstop = 3
vim.opt.shiftwidth = 4
vim.opt.termguicolors = true
vim.opt.signcolumn = "yes"

-- lazy.nvim
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

vim.g.mapleader = " "
vim.g.maplocalleader = "\\"

-- Setup lazy.nvim
require("lazy").setup({
	spec = {
		{ import = "plugins" },
		{ import = "plugins.lsp" },
	},
	install = { colorscheme = { "habamax" } },
	checker = { enabled = true, notify = false },
})

vim.cmd.colorscheme("kanagawa-dragon")

vim.api.nvim_create_autocmd("FileType", {
	pattern = "*",
	callback = function()
		vim.opt_local.formatoptions:remove({ "r", "o" })
	end,
})

vim.api.nvim_create_autocmd("BufReadPost", { -- Чтобы сразу работал treesitter
	callback = function()

		if vim.bo.filetype == "qf" then
			return
		end

		vim.treesitter.start()
	end,
})

local my_themes = {
	"gruvbox",
	"flexoki",
	"kanagawa-dragon",
	"habamax",
	"kanagawa-paper-ink",
	"kanagawa-paper-canvas",
	"lackluster",
	"lackluster-night",
	"lackluster-mint",
	"lackluster-dark",
	"lackluster-hack",
	"mellow",
	"unokai",
	"material-lighter",
	"everforest",
	"quiet",
	"bamboo",
	"bamboo-multiplex",
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
		vim.keymap.set("n", "<leader>r", ':w<CR>:TermExec cmd="python %" direction=vertical size=80<CR>', {
			buffer = true,
			desc = "Run Python file in vertical terminal",
		})
	end,
})
-- разобраться
vim.api.nvim_create_autocmd("FileType", {
	pattern = "cpp",
	callback = function()
		-- vim.keymap.set("n", "<leader>r", ':w<CR>:TermExec cmd="g++ -std=c++20 -O2 % -o %:r && ./%:r" direction=vertical size=80<CR>', {
		vim.keymap.set(
			"n",
			"<leader>r",
			':w<CR>:TermExec cmd="g++ -std=c++20 -O2 % -o %:r -lcrypto && ./%:r" direction=vertical size=80<CR>',
			{
				buffer = true,
				desc = "Compile and Run C++ in vertical terminal",
			}
		)
	end,
})

vim.api.nvim_create_autocmd("FileType", {
	pattern = "cs",
	callback = function()
		vim.keymap.set("n", "<leader>r", ':w<CR>:TermExec cmd="dotnet run" direction=vertical size=80<CR>', {
			buffer = true,
			desc = "Run C# project in vertical terminal",
		})
	end,
})

function _G.set_terminal_keymaps() -- работа с терминалом terminal
	local opts = { buffer = 0 }
	vim.keymap.set("t", "<esc>", [[<C-\><C-n>]], opts)
	vim.keymap.set("t", "<C-h>", [[<Cmd>wincmd h<CR>]], opts)
	vim.keymap.set("t", "<C-j>", [[<Cmd>wincmd j<CR>]], opts)
	vim.keymap.set("t", "<C-k>", [[<Cmd>wincmd k<CR>]], opts)
	vim.keymap.set("t", "<C-l>", [[<Cmd>wincmd l<CR>]], opts)
end

-- Применяем маппинги только при открытии терминала
vim.cmd("autocmd! TermOpen term://* lua set_terminal_keymaps()")
