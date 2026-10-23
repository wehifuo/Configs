vim.keymap.set("n", "<leader>e", function()
	vim.cmd("Neotree toggle")
end, { desc = "Neotree" })

vim.keymap.set("i", "jk", "<Esc>", { silent = true })

vim.keymap.set("n", "<C-h>", "<C-w>h", { desc = "Окно влево" })
vim.keymap.set("n", "<C-l>", "<C-w>l", { desc = "Окно вправо" })
vim.keymap.set("n", "<C-j>", "<C-w>j", { desc = "Окно вниз" })
vim.keymap.set("n", "<C-k>", "<C-w>k", { desc = "Окно вверх" })

-- <C-d>/<C-u>/<C-f>/<C-b> теперь обрабатывает neoscroll

-- Telescope
vim.keymap.set("n", "<leader>fn", function() require("telescope.builtin").find_files() end, { desc = "Файлы" })
vim.keymap.set("n", "<leader>fg", function() require("telescope.builtin").live_grep() end, { desc = "Grep" })
vim.keymap.set("n", "<leader>fb", function() require("telescope.builtin").buffers() end, { desc = "Буферы" })
vim.keymap.set("n", "<leader>fo", function() require("telescope.builtin").oldfiles() end, { desc = "Недавние файлы" })
vim.keymap.set("n", "<leader>fd", function() require("telescope.builtin").diagnostics() end, { desc = "Диагностика" })
vim.keymap.set("n", "<leader>fh", function() require("telescope.builtin").help_tags() end, { desc = "Help" })

-- Форматирование и references
vim.keymap.set("n", "<leader>fr", function()
	local ok, conform = pcall(require, "conform")
	if ok then
		conform.format({ async = true, lsp_format = "fallback" })
	else
		vim.lsp.buf.format({ async = true })
	end
end, { desc = "Форматировать буфер" })

vim.keymap.set("n", "<leader>fm", function()
	require("telescope.builtin").lsp_references()
end, { desc = "LSP references" })

vim.keymap.set("n", "<leader>t", "<cmd>tabnew<CR>", { silent = true, desc = "Новая вкладка" })
vim.keymap.set("x", "p", [["_dP]])

-- load the session for the current directory
vim.keymap.set("n", "<leader>qs", function() require("persistence").load() end)
-- select a session to load
vim.keymap.set("n", "<leader>qS", function() require("persistence").select() end)
-- load the last session
vim.keymap.set("n", "<leader>ql", function() require("persistence").load({ last = true }) end)
