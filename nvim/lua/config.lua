vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.ignorecase = true
vim.opt.clipboard = "unnamedplus"
vim.opt.tabstop = 4
vim.opt.softtabstop = 4
vim.opt.shiftwidth = 4
vim.opt.expandtab = true
vim.opt.termguicolors = true
vim.opt.signcolumn = "yes"

vim.opt.smartcase = true
vim.opt.incsearch = true
vim.opt.hlsearch = true
vim.opt.scrolloff = 8
vim.opt.sidescrolloff = 8
vim.opt.undofile = true
vim.opt.swapfile = false
vim.opt.splitright = true
vim.opt.splitbelow = true
vim.opt.updatetime = 250
vim.opt.timeoutlen = 300
vim.opt.mouse = "a"
vim.opt.cursorline = false
vim.opt.list = true
vim.opt.listchars = { tab = "» ", trail = "·", nbsp = "␣" }

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

-- LSP capabilities through cmp-nvim-lsp (loaded eagerly in plugins/lsp/lsp.lua)
local capabilities = vim.lsp.protocol.make_client_capabilities()
local ok_cmp_lsp, cmp_lsp = pcall(require, "cmp_nvim_lsp")
if ok_cmp_lsp then
	capabilities = cmp_lsp.default_capabilities(capabilities)
end
vim.lsp.config("*", { capabilities = capabilities })

vim.cmd.colorscheme("kanagawa-dragon")

vim.api.nvim_create_autocmd("FileType", {
	pattern = "*",
	callback = function()
		vim.opt_local.formatoptions:remove({ "r", "o" })
	end,
})

-- Make и Go требуют табы
vim.api.nvim_create_autocmd("FileType", {
	pattern = { "make", "go" },
	callback = function()
		vim.opt_local.expandtab = false
		vim.opt_local.tabstop = 4
		vim.opt_local.softtabstop = 4
		vim.opt_local.shiftwidth = 4
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

-- Какая тема в каком lazy-плагине лежит
local theme_plugins = {
	gruvbox = "gruvbox.nvim",
	flexoki = "flexoki",
	["kanagawa-dragon"] = "kanagawa.nvim",
	kanagawa = "kanagawa.nvim",
	["kanagawa-paper-ink"] = "kanagawa-paper.nvim",
	["kanagawa-paper-canvas"] = "kanagawa-paper.nvim",
	lackluster = "lackluster.nvim",
	["lackluster-night"] = "lackluster.nvim",
	["lackluster-mint"] = "lackluster.nvim",
	["lackluster-dark"] = "lackluster.nvim",
	["lackluster-hack"] = "lackluster.nvim",
	mellow = "mellow.nvim",
	material = "material.nvim",
	["material-lighter"] = "material.nvim",
	everforest = "everforest",
	bamboo = "bamboo.nvim",
	["bamboo-multiplex"] = "bamboo.nvim",
}

vim.api.nvim_create_user_command("MyThemes", function()
	vim.ui.select(my_themes, {
		prompt = "Выберите тему из списка избранных:",
	}, function(choice)
		if choice then
			local plugin = theme_plugins[choice]
			if plugin then
				pcall(function()
					require("lazy").load({ plugins = { plugin } })
				end)
			end
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
