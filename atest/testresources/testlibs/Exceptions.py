class FatalCatastrophyException(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = True

def exit_on_failure():
    raise FatalCatastrophyException()
