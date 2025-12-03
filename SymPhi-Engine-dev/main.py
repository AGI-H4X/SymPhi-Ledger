"""Compat shim so `python main.py` still works in repo checkouts."""

from gdk9.cli import main


if __name__ == "__main__":
    main()
