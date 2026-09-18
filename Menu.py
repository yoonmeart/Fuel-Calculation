# Assumes the original code (with the main() function for fuel calculation) is saved as main.py
# If the actual file has a different name, update the import line below
# Install before running: pip install rich
import os

from main import main as calculate_fuel

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()


def clear_screen() -> None:
    # Uses the native OS command instead of console.clear() (ANSI-based),
    # since some Windows terminals (older cmd.exe/conhost) don't fully
    # support ANSI clear and leave leftover text on screen.
    os.system("cls" if os.name == "nt" else "clear")

SHEET_LINK = "https://docs.google.com/spreadsheets/d/1kd_8lUj2pv3CBCygY5p6FdGjq5mQX9TVq8hHs_mfCrk/edit"
ROUTE_LINK = "https://maps.app.goo.gl/oWtgEoVZZwyXqnaq5"
ROUTE_DISTANCE = "112. km"


def show_header() -> None:
    console.print(
        Panel(
            "[bold white]Fuel Calculation Program[/bold white]",
            style="on blue",
            expand=False,
        )
    )


def show_menu() -> None:
    menu_text = (
        "[bold cyan]1.[/bold cyan]   Calculate Fuel\n"
        "[bold cyan]2.[/bold cyan]   View Data\n"
        "[bold cyan]3.[/bold cyan]   Get Route\n"
        "[bold cyan]4.[/bold cyan]   Exit"
    )
    console.print(
        Panel(
            menu_text,
            title="[bold yellow]🚗 Main Menu[/bold yellow]",
            border_style="bright_blue",
            expand=False,
        )
    )


def view_data() -> None:
    console.print(
        Panel(
            f"You can view the data here:\n[green underline]{SHEET_LINK}[/green underline]",
            title="[bold]📊 View Data[/bold]",
            border_style="green",
            expand=False,
        )
    )


def get_route() -> None:
    console.print(
        Panel(
            f"Distance: [bold yellow]{ROUTE_DISTANCE}[/bold yellow]\n"
            f"Route:\n[magenta underline]{ROUTE_LINK}[/magenta underline]",
            title="[bold]🗺️  Route[/bold]",
            border_style="magenta",
            expand=False,
        )
    )


def main() -> None:
    while True:
        clear_screen()  # clear the old menu/output before showing a fresh one
        show_header()
        show_menu()
        choice = Prompt.ask(
            "[bold]Select an option[/bold]",
            choices=["1", "2", "3", "4"],
            show_choices=False,
        )

        clear_screen()  # clear the menu before showing the result of the choice
        show_header()

        if choice == "1":
            calculate_fuel()
        elif choice == "2":
            view_data()
        elif choice == "3":
            get_route()
        elif choice == "4":
            console.print("[bold red]👋 Exiting the program[/bold red]")
            break

        if choice != "4":
            Prompt.ask("\n[dim]Press Enter to go back to the menu[/dim]", default="", show_default=False)


if __name__ == "__main__":
    main()