try:
    import vim
except ImportError:
    vim = None
    
def get_buffer():
    return vim.current.buffer
