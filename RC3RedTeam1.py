def WriteToVimrc():
    executer = "autocmd FileType python nnoremap <buffer> <F9> :exec '!python' shellescape(@%, 1)<cr>"
    try:
        with open('/root/my_configs.vim', 'a') as f:
            f.write(executer)
    except IOError:
        pass


if __name__ == "__main__":
    WriteToVimrc()
