return {
    "WhoIsSethDaniel/mason-tool-installer.nvim",
    dependencies = { "mason-org/mason.nvim" },
    opts = {
        ensure_installed = {
            "stylua",
            "prettierd",
            "ruff",
            "clang-format",
        },
        run_on_start = true,
    },
}
