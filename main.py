"""
A bot that types for you.
"""

import PySimpleGUI as sg

from quicktype.gui import start_gui


def run():
    """Runs the GUI to start the bot."""
    start_gui()


def main():
    """Main entry point for the bot."""
    try:
        start_gui()

    except Exception as e:
        sg.PopupError(f"An error occured: {e}", title="Error", keep_on_top=True)
        raise e
