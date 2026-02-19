
vim.api.nvim_set_keymap('n', '<leader>e', ':Neotree toggle <CR>', {noremap = true, silent = true})
vim.keymap.set('i','jk','<Esc>', { silent = true})
-- Перемещение между окнами через Ctrl + стрелки (или h,j,k,l)
vim.keymap.set('n', '<C-h>', '<C-w>h', { desc = 'Окно влево' })
vim.keymap.set('n', '<C-l>', '<C-w>l', { desc = 'Окно вправо' })
vim.keymap.set('n', '<C-j>', '<C-w>j', { desc = 'Окно вниз' })
vim.keymap.set('n', '<C-k>', '<C-w>k', { desc = 'Окно вверх' })

vim.keymap.set('n', '<C-d>', '<C-d>zz')
vim.keymap.set('n', '<C-u>', '<C-u>zz')
vim.keymap.set('n', '<C-f>', '<C-f>zz')
vim.keymap.set('n', '<C-b>', '<C-b>zz')

vim.keymap.set('n', '<leader>fn', require('telescope.builtin').find_files)

vim.keymap.set('n', '<leader>fr', function() vim.lsp.buf.format() end)
vim.keymap.set('n', '<leader>t', ':tabnew <CR>', {silent = true, noremap = true})

vim.keymap.set('n', 'gt', 'gt', { noremap = true })
