if __name__ == '__main__':
    import sys
    import os.path as p

    #Vimscript passes in script filename as an argument
    #as __file__ is not set by vim's python interpreter
    SCRIPT_FILE = sys.argv[0]

    SCRIPT_FOLDER = p.dirname(p.abspath(SCRIPT_FILE))
    sys.path.append(SCRIPT_FOLDER)

    import vim_adaptor
