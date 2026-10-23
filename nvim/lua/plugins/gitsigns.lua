return {
    "lewis6991/gitsigns.nvim",
    event = { "BufReadPre", "BufNewFile" },
    opts = {
        signcolumn = false,
        on_attach = function(bufnr)
            local gs = package.loaded.gitsigns
            local map = function(mode, lhs, rhs, desc)
                vim.keymap.set(mode, lhs, rhs, { buffer = bufnr, desc = desc })
            end

            map("n", "]h", gs.next_hunk, "Следующий хунк")
            map("n", "[h", gs.prev_hunk, "Предыдущий хунк")
            map("n", "<leader>hs", gs.stage_hunk, "Stage hunk")
            map("n", "<leader>hr", gs.reset_hunk, "Reset hunk")
            map("n", "<leader>hp", gs.preview_hunk, "Preview hunk")
            map("n", "<leader>hb", function()
                gs.blame_line({ full = true })
            end, "Blame line")
        end,
    },
}
