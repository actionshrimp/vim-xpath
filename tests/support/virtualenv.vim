py << EOF
import vim
try:
    import lxml
except ImportError:
    activate_this = '~/virtualenv/python2.7/bin/activate'
    execfile(activate_this, dict(__file__=activate_this))
EOF
