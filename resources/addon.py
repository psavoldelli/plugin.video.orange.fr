import importlib

from codequick import run


def main():
    """Entry point function executed by Kodi for each menu of the addon"""

    # Let CodeQuick check for functions to register and call
    # the correct function according to the Kodi URL
    exception = run()
    if isinstance(exception, Exception):
        main = importlib.import_module('resources.lib.main')
        main.error_handler(exception)


if __name__ == "__main__":
    main()