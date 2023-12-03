from rich.console import Console
from quicktype.im2text import *

console = Console()


def run():
    console.print("Hello, [bold magenta]World[/bold magenta]!", soft_wrap=True)
    get_image_text_and_colors("img/test.png")
