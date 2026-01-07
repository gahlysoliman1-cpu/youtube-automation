from rich.console import Console

console = Console()


def info(message: str) -> None:
    console.print(f"[bold cyan]INFO[/bold cyan] {message}")


def warn(message: str) -> None:
    console.print(f"[bold yellow]WARN[/bold yellow] {message}")


def error(message: str) -> None:
    console.print(f"[bold red]ERROR[/bold red] {message}")
