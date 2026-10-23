return {
    "folke/trouble.nvim",
    cmd = "Trouble",
    keys = {
        { "<leader>xx", "<cmd>Trouble diagnostics toggle<cr>", desc = "Диагностика" },
        { "<leader>xX", "<cmd>Trouble diagnostics toggle filter.buf=0<cr>", desc = "Диагностика буфера" },
    },
    opts = {},
}
