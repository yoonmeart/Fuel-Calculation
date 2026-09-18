# สมมติว่าไฟล์โค้ดเดิม (ที่มีฟังก์ชัน main() สำหรับคำนวณน้ำมัน) ถูกเซฟไว้ในชื่อ fuel_tracker.py
# ถ้าไฟล์จริงชื่ออื่น ให้แก้บรรทัดนี้ให้ตรงกับชื่อไฟล์จริง
# ต้องติดตั้งก่อนใช้: pip install rich
from main import main as calculate_fuel

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

SHEET_LINK = "https://docs.google.com/spreadsheets/d/1kd_8lUj2pv3CBCygY5p6FdGjq5mQX9TVq8hHs_mfCrk/edit"
ROUTE_LINK = "https://maps.app.goo.gl/oWtgEoVZZwyXqnaq5"
ROUTE_DISTANCE = "112. km"


def show_menu() -> None:
    menu_text = (
        "[bold cyan]1.[/bold cyan] ⛽  Calculate Fuel\n"
        "[bold cyan]2.[/bold cyan] 📊  View Data\n"
        "[bold cyan]3.[/bold cyan] 🗺️   Get Route\n"
        "[bold cyan]4.[/bold cyan] 🚪  Exit"
    )
    console.print(
        Panel(
            menu_text,
            title="[bold yellow]🚗 Fuel Calculation Menu[/bold yellow]",
            border_style="bright_blue",
            expand=False,
        )
    )


def view_data() -> None:
    console.print(
        Panel(
            f"ดูข้อมูลได้ที่ลิงก์นี้:\n[green underline]{SHEET_LINK}[/green underline]",
            title="[bold]📊 View Data[/bold]",
            border_style="green",
            expand=False,
        )
    )


def get_route() -> None:
    console.print(
        Panel(
            f"ระยะทาง: [bold yellow]{ROUTE_DISTANCE}[/bold yellow]\n"
            f"เส้นทาง:\n[magenta underline]{ROUTE_LINK}[/magenta underline]",
            title="[bold]🗺️  Route[/bold]",
            border_style="magenta",
            expand=False,
        )
    )


def main() -> None:
    console.print(
        Panel(
            "[bold white]Fuel Calculation Program[/bold white]",
            style="on blue",
            expand=False,
        )
    )
    while True:
        show_menu()
        choice = Prompt.ask(
            "[bold]เลือกเมนู[/bold]",
            choices=["1", "2", "3", "4"],
            show_choices=False,
        )

        if choice == "1":
            calculate_fuel()
        elif choice == "2":
            view_data()
        elif choice == "3":
            get_route()
        elif choice == "4":
            console.print("[bold red]👋 ออกจากโปรแกรม[/bold red]")
            break

        console.print()  # เว้นบรรทัดให้อ่านง่ายก่อนวนกลับเมนู


if __name__ == "__main__":
    main()