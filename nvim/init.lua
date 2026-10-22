require("lsp")
require("config")
require("keymappings")

vim.api.nvim_create_autocmd("FileType", {
  pattern = "qf",
  callback = function()
    pcall(vim.treesitter.stop)
  end,
})
