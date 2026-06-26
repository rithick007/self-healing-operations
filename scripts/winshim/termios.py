# Minimal Windows shim for the Unix-only `termios` module.
# Lets lemma-terminal 0.5.0 import on Windows. Interactive raw-mode key
# selection is NOT supported by this shim — use non-interactive flags
# (explicit args + --json) for every command.
TCSADRAIN = 1
TCSANOW = 0
TCSAFLUSH = 2

error = Exception


def tcgetattr(fd):
    return []


def tcsetattr(fd, when, attributes):
    return None


def tcdrain(fd):
    return None


def tcflush(fd, queue):
    return None


def tcsendbreak(fd, duration):
    return None
