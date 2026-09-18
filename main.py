
import gspread
import time
from google.oauth2.service_account import Credentials
from datetime import datetime
from calculations import (
    calculate_fuel_price,
    calculate_distance,
    calculate_fuel_efficiency
)
from summary import update_summary

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = "1kd_8lUj2pv3CBCygY5p6FdGjq5mQX9TVq8hHs_mfCrk"
sheet = client.open_by_key(sheet_id)




default_data:dict[str, str | float] = {
    "FUEL_TYPE": "E20",
    "FUEL_PRICE": 32.69,
    "CAR_MODEL" : "Mitsubishi Mirage",
    "TANK_CAPACITY" : 35.0
}


# ======================== READ FORM DATA =================================
def read_sheet() -> int:
    worksheet = sheet.sheet1
    values = worksheet.get("D:D")
    if values: 
        last_values = int(values[-1][0].replace(" km", ""))
        print(f"last values is: {last_values}")
    else: 
        print("ไม่พบข้อมูล")
        time.sleep(.5)
        print("กำลังค้นหา...")
        time.sleep(2.5)
        return read_sheet()
    return last_values

def get_previous_odometer() -> int:
    return read_sheet()
# ========================================================================


# ======================== Creatable =================================
def create_table(fuel_data:dict[str, str|float|int]) -> list[str|int|float]:
    tables = [str(datetime.now()), default_data["FUEL_TYPE"],default_data["CAR_MODEL"],fuel_data["CurrentOdometer"] ,get_previous_odometer(), fuel_data["Distance"],fuel_data["Liters"],fuel_data["ActualPrice"],fuel_data["TotalPrice"]]
    return tables
# ========================================================================


# ======================== Sent To Sheet =================================

def append_to_sheet(tables: list[str|int|float]) -> None:
    worksheet = sheet.sheet1
    worksheet.append_row(tables, value_input_option="USER_ENTERED")
    print("Row appended successfully!")

# ========================================================================


# ======================== Discord Bot =================================
def record_fuel(current_odometer:int, liters:float, total_price:int) -> list[str|int|float]:
    fuel_data: dict[str, str|float|int] = {"CurrentOdometer": current_odometer,"Liters": liters,"TotalPrice": total_price}
    update_fuel_data(fuel_data)
    update_summary()
    return append_to_sheet(create_table(fuel_data))

# ======================================================================


def update_fuel_data(fuel_data: dict[str, str | float | int]) -> None:
    previous_odometer: int = get_previous_odometer()
    fuel_data.update({"ActualPrice": round(calculate_fuel_price(fuel_data["TotalPrice"], fuel_data["Liters"]), 2)})
    fuel_data.update({"PreviousOdometer": previous_odometer})
    fuel_data.update({"Distance": calculate_distance(fuel_data["CurrentOdometer"], fuel_data["PreviousOdometer"])})
    fuel_data.update({"FuelEffiency": round(calculate_fuel_efficiency(fuel_data["Distance"], fuel_data["Liters"]), 2)})

def process_fuel_data(fuel_data: dict[str, str | float | int]) -> None:
    print(create_table(fuel_data))
    append_to_sheet(create_table(fuel_data))
    update_summary()
    
def main() -> None:
    
    fuel_data:dict[str, str|float|int] = {}  
    
    #=========================================== Input =======================================================
    
    fuel_data.update({"CurrentOdometer": int(input("เลขไมล์ปัจจุบัน: "))})
    fuel_data.update({"Liters":float(input("เติมน้ำมันกี่ลิตร: "))})
    fuel_data.update({"TotalPrice":int(input("เติมน้ำมันกี่บาท: "))})
    update_fuel_data(fuel_data)
    #========================================== Method =================================================

    process_fuel_data(fuel_data)
    
    
    
if __name__ == '__main__':
    main()
