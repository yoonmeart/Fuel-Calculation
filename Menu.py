from main import main as calculate_fuel


SHEET_LINK = "https://docs.google.com/spreadsheets/d/1kd_8lUj2pv3CBCygY5p6FdGjq5mQX9TVq8hHs_mfCrk/edit"
ROUTE_LINK = "https://maps.app.goo.gl/oWtgEoVZZwyXqnaq5"
ROUTE_DISTANCE = "112. km"


def show_menu() -> None:
    print("=" * 40)
    print("เมนูหลัก")
    print("1. Calculate Fuel")
    print("2. View Data")
    print("3. Get Route")
    print("4. Exit")
    print("=" * 40)


def view_data() -> None:
    print(f"ดูข้อมูลได้ที่ลิงก์นี้: {SHEET_LINK}")


def get_route() -> None:
    print(f"ระยะทาง: {ROUTE_DISTANCE}")
    print(f"เส้นทาง: {ROUTE_LINK}")


def main() -> None:
    while True:
        show_menu()
        choice = input("เลือกเมนู (1-4): ").strip()

        if choice == "1":
            calculate_fuel()
        elif choice == "2":
            view_data()
        elif choice == "3":
            get_route()
        elif choice == "4":
            print("ออกจากโปรแกรม")
            break
        else:
            print("กรุณาเลือกเมนูที่ถูกต้อง (1-4)")


if __name__ == "__main__":
    main()