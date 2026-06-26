# Minimal Windows shim for the Unix-only `tty` module.
# Companion to the termios shim so lemma-terminal 0.5.0 imports on Windows.
def setraw(fd, when=None):
    return None


def setcbreak(fd, when=None):
    return None
