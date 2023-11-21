from rich.console import Console

console = Console()

def run():
    console.print("Hello, [bold magenta]World[/bold magenta]!", soft_wrap=True)