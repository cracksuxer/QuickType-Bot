from rich.console import Console
from quicktype.im2text import get_image_text_and_colors
from quicktype.gui import start_gui

console = Console()


def run():
    start_gui()
    console.print("Hello, [bold magenta]World[/bold magenta]!", soft_wrap=True)
    get_image_text_and_colors("img/test.png")
