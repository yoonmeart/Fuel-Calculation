import gspread

from collections import defaultdict
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

from google.oauth2.service_account import Credentials


# ============================================================
# CONFIG
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

SHEET_ID = "1kd_8lUj2pv3CBCygY5p6FdGjq5mQX9TVq8hHs_mfCrk"

SUMMARY_SHEET_NAME = "Summary"

TIMEZONE = ZoneInfo("Asia/Bangkok")


# ============================================================
# SHEET 1 COLUMNS
# ============================================================
#
# A = วันที่
# B = ประเภทเชื้อเพลิง
# C = รุ่นรถ
# D = เลขไมล์ปัจจุบัน
# E = เลขไมล์ครั้งก่อน
# F = ระยะทาง
# G = จำนวนลิตร
# H = ราคาน้ำมันต่อลิตร
# I = ราคารวม
#
# ============================================================

DATE_COL = 0
FUEL_TYPE_COL = 1
CAR_MODEL_COL = 2
CURRENT_ODOMETER_COL = 3
PREVIOUS_ODOMETER_COL = 4
DISTANCE_COL = 5
LITERS_COL = 6
PRICE_PER_LITER_COL = 7
TOTAL_PRICE_COL = 8


# ============================================================
# SUMMARY HEADERS
# ============================================================

SUMMARY_HEADERS = [
    "ช่วงเวลา",
    "วันที่",
    "จำนวนครั้งเติม",
    "จำนวนลิตร",
    "ค่าใช้จ่ายรวม",
    "ระยะทางรวม",
    "ราคาเฉลี่ยต่อลิตร",
    "อัตราสิ้นเปลืองเฉลี่ย",
    "ค่าใช้จ่ายเฉลี่ยต่อ km"
]


# ============================================================
# GOOGLE SHEETS CONNECTION
# ============================================================

def connect_google_sheet():

    credentials = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )

    client = gspread.authorize(
        credentials
    )

    spreadsheet = client.open_by_key(
        SHEET_ID
    )

    return spreadsheet


# ============================================================
# GET SUMMARY SHEET
# ============================================================

def get_summary_sheet(spreadsheet):

    try:

        return spreadsheet.worksheet(
            SUMMARY_SHEET_NAME
        )

    except gspread.WorksheetNotFound:

        print(
            f"ไม่พบชีต '{SUMMARY_SHEET_NAME}'"
        )

        print(
            "กำลังสร้าง Summary..."
        )

        return spreadsheet.add_worksheet(
            title=SUMMARY_SHEET_NAME,
            rows=1000,
            cols=20
        )


# ============================================================
# PARSE NUMBER
# ============================================================

def parse_number(value) -> float:
    """
    Convert value -> float

    รองรับตัวอย่าง:

        32.84
        32.84/
        32.84 / 
        1,250
        1,250.50
        35 L
        100 km
        1,000 บาท
    """

    if value is None:

        raise ValueError(
            "ไม่มีข้อมูลตัวเลข"
        )


    text = str(value).strip()


    if not text:

        raise ValueError(
            "ไม่มีข้อมูลตัวเลข"
        )


    # --------------------------------------------------------
    # Remove common text
    # --------------------------------------------------------

    text = (
        text
        .replace(",", "")
        .replace(" km", "")
        .replace("km", "")
        .replace(" L", "")
        .replace("L", "")
        .replace(" บาท", "")
        .replace("บาท", "")
    )


    # --------------------------------------------------------
    # IMPORTANT
    #
    # Sheet ของคุณมีค่าแบบ:
    #
    # 32.84/
    #
    # จึงต้องเอา / ออก
    # --------------------------------------------------------

    text = text.replace("/", "")


    # --------------------------------------------------------
    # Remove spaces
    # --------------------------------------------------------

    text = text.strip()


    return float(text)


# ============================================================
# PARSE DATE
# ============================================================

def parse_date(value) -> datetime:
    """
    รองรับ datetime และ date
    รวมถึง format จาก datetime.now()
    """

    # --------------------------------------------------------
    # datetime
    # --------------------------------------------------------

    if isinstance(value, datetime):

        return value


    # --------------------------------------------------------
    # date
    # --------------------------------------------------------

    if isinstance(value, date):

        return datetime(
            value.year,
            value.month,
            value.day
        )


    text = str(value).strip()


    if not text:

        raise ValueError(
            "วันที่ว่าง"
        )


    formats = [

        # datetime.now()

        "%Y-%m-%d %H:%M:%S.%f",

        "%Y-%m-%d %H:%M:%S",

        "%Y-%m-%d %H:%M",

        "%Y-%m-%d",


        # DD/MM/YYYY

        "%d/%m/%Y %H:%M:%S.%f",

        "%d/%m/%Y %H:%M:%S",

        "%d/%m/%Y %H:%M",

        "%d/%m/%Y",


        # DD-MM-YYYY

        "%d-%m-%Y %H:%M:%S.%f",

        "%d-%m-%Y %H:%M:%S",

        "%d-%m-%Y %H:%M",

        "%d-%m-%Y",
    ]


    for date_format in formats:

        try:

            return datetime.strptime(
                text,
                date_format
            )

        except ValueError:

            continue


    raise ValueError(
        f"ไม่สามารถอ่านวันที่ได้: {value}"
    )


# ============================================================
# READ FUEL DATA
# ============================================================

def get_fuel_data(
    worksheet
) -> list[dict]:

    values = worksheet.get_all_values()


    if not values:

        print(
            "ไม่พบข้อมูลใน Sheet1"
        )

        return []


    print(
        f"พบข้อมูลทั้งหมด {len(values)} rows"
    )


    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    header = values[0]

    print(
        f"Header: {header}"
    )


    # --------------------------------------------------------
    # Data
    # --------------------------------------------------------

    rows = values[1:]


    fuel_data = []


    for row_number, row in enumerate(
        rows,
        start=2
    ):

        # ----------------------------------------------------
        # Check columns
        # ----------------------------------------------------

        if len(row) < 9:

            print(
                f"[WARNING] Row {row_number}: "
                f"มี {len(row)} columns "
                f"(ต้องการ 9) - ข้าม"
            )

            continue


        try:

            # ------------------------------------------------
            # Date
            # ------------------------------------------------

            parsed_date = parse_date(
                row[DATE_COL]
            )


            # ------------------------------------------------
            # Fuel
            # ------------------------------------------------

            fuel_type = str(
                row[FUEL_TYPE_COL]
            ).strip()


            # ------------------------------------------------
            # Car
            # ------------------------------------------------

            car_model = str(
                row[CAR_MODEL_COL]
            ).strip()


            # ------------------------------------------------
            # Distance
            # ------------------------------------------------

            distance = parse_number(
                row[DISTANCE_COL]
            )


            # ------------------------------------------------
            # Liters
            # ------------------------------------------------

            liters = parse_number(
                row[LITERS_COL]
            )


            # ------------------------------------------------
            # Price / Liter
            # ------------------------------------------------

            price_per_liter = parse_number(
                row[PRICE_PER_LITER_COL]
            )


            # ------------------------------------------------
            # Total
            # ------------------------------------------------

            total_price = parse_number(
                row[TOTAL_PRICE_COL]
            )


            # ------------------------------------------------
            # Validation
            # ------------------------------------------------

            if distance < 0:

                raise ValueError(
                    "ระยะทางติดลบ"
                )


            if liters < 0:

                raise ValueError(
                    "จำนวนลิตรติดลบ"
                )


            if price_per_liter < 0:

                raise ValueError(
                    "ราคาต่อลิตรติดลบ"
                )


            if total_price < 0:

                raise ValueError(
                    "ราคารวมติดลบ"
                )


            # ------------------------------------------------
            # Store
            # ------------------------------------------------

            data = {

                "date": parsed_date,

                "fuel_type": fuel_type,

                "car_model": car_model,

                "distance": distance,

                "liters": liters,

                "price_per_liter": price_per_liter,

                "total_price": total_price
            }


            fuel_data.append(
                data
            )


            print(
                f"[OK] Row {row_number}: "
                f"{parsed_date} | "
                f"{distance} km | "
                f"{liters} L | "
                f"{price_per_liter}/L | "
                f"{total_price} บาท"
            )


        except Exception as e:

            print(
                f"[WARNING] Row {row_number}: "
                f"{e} - ข้าม"
            )


    print(
        f"อ่านข้อมูลสำเร็จ: "
        f"{len(fuel_data)} รายการ"
    )


    return fuel_data


# ============================================================
# GET MONDAY
# ============================================================

def get_monday(
    value: datetime
) -> datetime:

    days_from_monday = (
        value.weekday()
    )


    monday = (
        value
        - timedelta(
            days=days_from_monday
        )
    )


    return monday.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )


# ============================================================
# GET SUNDAY
# ============================================================

def get_sunday(
    monday: datetime
) -> datetime:

    return (
        monday
        + timedelta(days=6)
    ).replace(
        hour=23,
        minute=59,
        second=59,
        microsecond=999999
    )


# ============================================================
# WEEK NUMBER IN MONTH
# ============================================================

def get_week_number_in_month(
    monday: datetime,
    year: int,
    month: int
) -> int:

    first_day = datetime(
        year,
        month,
        1
    )


    first_monday = get_monday(
        first_day
    )


    difference = (
        monday.date()
        - first_monday.date()
    ).days


    return (
        difference // 7
    ) + 1


# ============================================================
# GET WEEKS OF MONTH
# ============================================================

def get_month_weeks(
    year: int,
    month: int
) -> list[dict]:

    first_day = datetime(
        year,
        month,
        1
    )


    # --------------------------------------------------------
    # Next month
    # --------------------------------------------------------

    if month == 12:

        next_month = datetime(
            year + 1,
            1,
            1
        )

    else:

        next_month = datetime(
            year,
            month + 1,
            1
        )


    last_day = (
        next_month
        - timedelta(days=1)
    )


    # --------------------------------------------------------
    # Monday
    # --------------------------------------------------------

    first_monday = get_monday(
        first_day
    )


    last_monday = get_monday(
        last_day
    )


    weeks = []


    current_monday = first_monday


    while current_monday <= last_monday:

        current_sunday = get_sunday(
            current_monday
        )


        week_number = (
            get_week_number_in_month(
                current_monday,
                year,
                month
            )
        )


        weeks.append({

            "number": week_number,

            "monday": current_monday,

            "sunday": current_sunday
        })


        current_monday += timedelta(
            days=7
        )


    return weeks


# ============================================================
# GROUP WEEKLY
# ============================================================

def group_weekly(
    fuel_data: list[dict]
) -> dict:

    weekly = defaultdict(
        lambda: {

            "refuels": 0,

            "liters": 0.0,

            "total_price": 0.0,

            "distance": 0.0
        }
    )


    for data in fuel_data:

        monday = get_monday(
            data["date"]
        )


        key = monday.date()


        weekly[key]["refuels"] += 1

        weekly[key]["liters"] += (
            data["liters"]
        )

        weekly[key]["total_price"] += (
            data["total_price"]
        )

        weekly[key]["distance"] += (
            data["distance"]
        )


    return weekly


# ============================================================
# CALCULATE SUMMARY
# ============================================================

def calculate_summary(
    data: dict
) -> dict:

    refuels = data["refuels"]

    liters = data["liters"]

    total_price = data["total_price"]

    distance = data["distance"]


    # --------------------------------------------------------
    # Average price / Liter
    # --------------------------------------------------------

    if liters > 0:

        average_price = (
            total_price
            / liters
        )

    else:

        average_price = 0.0


    # --------------------------------------------------------
    # Fuel Efficiency
    # --------------------------------------------------------

    if liters > 0:

        fuel_efficiency = (
            distance
            / liters
        )

    else:

        fuel_efficiency = 0.0


    # --------------------------------------------------------
    # Cost / KM
    # --------------------------------------------------------

    if distance > 0:

        cost_per_km = (
            total_price
            / distance
        )

    else:

        cost_per_km = 0.0


    return {

        "refuels": refuels,

        "liters": round(
            liters,
            2
        ),

        "total_price": round(
            total_price,
            2
        ),

        "distance": round(
            distance,
            2
        ),

        "average_price": round(
            average_price,
            2
        ),

        "fuel_efficiency": round(
            fuel_efficiency,
            2
        ),

        "cost_per_km": round(
            cost_per_km,
            2
        )
    }


# ============================================================
# CREATE WEEKLY ROWS
# ============================================================

def create_weekly_rows(
    fuel_data: list[dict],
    weekly_data: dict
) -> list[list]:

    rows = []


    if not fuel_data:

        return rows


    # --------------------------------------------------------
    # Find months with data
    # --------------------------------------------------------

    months = sorted(
        set(
            (
                data["date"].year,
                data["date"].month
            )
            for data in fuel_data
        )
    )


    # --------------------------------------------------------
    # Current date
    # --------------------------------------------------------

    now = datetime.now(
        TIMEZONE
    )


    current_monday = get_monday(
        now
    )


    # --------------------------------------------------------
    # Track weeks already added
    #
    # ป้องกันสัปดาห์ซ้ำ กรณีสัปดาห์คาบเกี่ยว
    # ระหว่างเดือน (เช่น 31/08 - 06/09)
    # ซึ่งจะถูกสร้างซ้ำทั้งจากเดือนก่อนหน้า
    # และเดือนถัดไป
    # --------------------------------------------------------

    seen_weeks = set()


    # --------------------------------------------------------
    # Create Week
    # --------------------------------------------------------

    for year, month in months:

        month_weeks = get_month_weeks(
            year,
            month
        )


        for week in month_weeks:

            monday = week["monday"]

            sunday = week["sunday"]


            key = monday.date()


            # ------------------------------------------------
            # Skip duplicate week
            # ------------------------------------------------

            if key in seen_weeks:

                continue


            seen_weeks.add(
                key
            )


            data = weekly_data.get(

                key,

                {

                    "refuels": 0,

                    "liters": 0.0,

                    "total_price": 0.0,

                    "distance": 0.0
                }
            )


            summary = calculate_summary(
                data
            )


            # ------------------------------------------------
            # Current week
            # ------------------------------------------------

            is_current_week = (
                monday.date()
                == current_monday.date()
            )


            # ------------------------------------------------
            # Has data
            # ------------------------------------------------

            has_data = (
                summary["refuels"] > 0
            )


            # ------------------------------------------------
            # Show:
            #
            # - Week with data
            # - Current week
            # ------------------------------------------------

            if (
                not has_data
                and not is_current_week
            ):

                continue


            date_range = (
                monday.strftime(
                    "%d/%m/%Y"
                )
                + " - "
                + sunday.strftime(
                    "%d/%m/%Y"
                )
            )


            rows.append([

                f"{week['number']}W",

                date_range,

                summary["refuels"],

                summary["liters"],

                summary["total_price"],

                summary["distance"],

                summary["average_price"],

                summary["fuel_efficiency"],

                summary["cost_per_km"]
            ])


    return rows


# ============================================================
# BUILD SUMMARY SHEET
# ============================================================

def build_summary_sheet(
    worksheet,
    weekly_rows: list[list]
) -> None:

    # --------------------------------------------------------
    # Clear
    # --------------------------------------------------------

    worksheet.clear()


    rows = []


    # ========================================================
    # WEEKLY
    # ========================================================

    rows.append([

        "WEEKLY SUMMARY",

        "",

        "",

        "",

        "",

        "",

        "",

        "",

        ""
    ])


    rows.append(
        SUMMARY_HEADERS
    )


    if weekly_rows:

        rows.extend(
            weekly_rows
        )

    else:

        rows.append([

            "ไม่มีข้อมูล",

            "",

            "",

            "",

            "",

            "",

            "",

            "",

            ""
        ])


    # ========================================================
    # WRITE
    # ========================================================
    #
    # ใช้ named arguments
    # เพื่อไม่เจอ DeprecationWarning
    #

    worksheet.update(
        range_name="A1",
        values=rows,
        value_input_option="USER_ENTERED"
    )


# ============================================================
# FORMAT SUMMARY
# ============================================================

def format_summary_sheet(
    worksheet
) -> None:

    try:

        # ====================================================
        # NUMBER FORMAT
        # ====================================================
        #
        # C = จำนวนครั้งเติม
        # D = จำนวนลิตร
        # E = ค่าใช้จ่ายรวม
        # F = ระยะทางรวม
        # G = ราคาเฉลี่ยต่อลิตร
        # H = อัตราสิ้นเปลืองเฉลี่ย
        # I = ค่าใช้จ่ายเฉลี่ยต่อ km
        #
        # ใช้ Custom Number Format ของ Google Sheets
        # ดังนั้นค่าจริงใน Cell ยังคงเป็นตัวเลข
        # ====================================================


        # ----------------------------------------------------
        # จำนวนครั้งเติม
        # ----------------------------------------------------

        worksheet.format(
            "C:C",
            {
                "numberFormat": {
                    "type": "NUMBER",
                    "pattern": "0"
                }
            }
        )


        # ----------------------------------------------------
        # จำนวนลิตร
        # ----------------------------------------------------

        worksheet.format(
            "D:D",
            {
                "numberFormat": {
                    "type": "NUMBER",
                    "pattern": '0.00 "L"'
                }
            }
        )


        # ----------------------------------------------------
        # ค่าใช้จ่ายรวม
        # ----------------------------------------------------

        worksheet.format(
            "E:E",
            {
                "numberFormat": {
                    "type": "NUMBER",
                    "pattern": '0.00 "บาท"'
                }
            }
        )


        # ----------------------------------------------------
        # ระยะทางรวม
        # ----------------------------------------------------

        worksheet.format(
            "F:F",
            {
                "numberFormat": {
                    "type": "NUMBER",
                    "pattern": '0.00 "km"'
                }
            }
        )


        # ----------------------------------------------------
        # ราคาเฉลี่ยต่อลิตร
        # ----------------------------------------------------

        worksheet.format(
            "G:G",
            {
                "numberFormat": {
                    "type": "NUMBER",
                    "pattern": '0.00 "บาท/L"'
                }
            }
        )


        # ----------------------------------------------------
        # อัตราสิ้นเปลืองเฉลี่ย
        # ----------------------------------------------------

        worksheet.format(
            "H:H",
            {
                "numberFormat": {
                    "type": "NUMBER",
                    "pattern": '0.00 "km/L"'
                }
            }
        )


        # ----------------------------------------------------
        # ค่าใช้จ่ายเฉลี่ยต่อ km
        # ----------------------------------------------------

        worksheet.format(
            "I:I",
            {
                "numberFormat": {
                    "type": "NUMBER",
                    "pattern": '0.00 "บาท/km"'
                }
            }
        )


        print(
            "ตั้งค่า Number Format สำเร็จ"
        )


    except Exception as e:

        print(
            "[WARNING] "
            f"Number formatting failed: {e}"
        )


# ============================================================
# UPDATE SUMMARY
# ============================================================

def update_summary():

    print(
        "========================================"
    )

    print(
        "         FUEL WEEKLY SUMMARY"
    )

    print(
        "========================================"
    )


    try:

        # ----------------------------------------------------
        # Connect
        # ----------------------------------------------------

        spreadsheet = (
            connect_google_sheet()
        )


        # ----------------------------------------------------
        # Sheet1
        # ----------------------------------------------------

        source_worksheet = (
            spreadsheet.sheet1
        )


        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        summary_worksheet = (
            get_summary_sheet(
                spreadsheet
            )
        )


        # ----------------------------------------------------
        # Read
        # ----------------------------------------------------

        fuel_data = (
            get_fuel_data(
                source_worksheet
            )
        )


        # ----------------------------------------------------
        # Group
        # ----------------------------------------------------

        weekly_data = (
            group_weekly(
                fuel_data
            )
        )


        # ----------------------------------------------------
        # Create rows
        # ----------------------------------------------------

        weekly_rows = (
            create_weekly_rows(
                fuel_data,
                weekly_data
            )
        )


        # ----------------------------------------------------
        # Write
        # ----------------------------------------------------

        build_summary_sheet(
            summary_worksheet,
            weekly_rows
        )


        # ----------------------------------------------------
        # Format
        # ----------------------------------------------------

        format_summary_sheet(
            summary_worksheet
        )


        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        print(
            "----------------------------------------"
        )


        print(
            f"Weekly Summary: "
            f"{len(weekly_rows)} rows"
        )


        print(
            "อัปเดต Summary สำเร็จ"
        )


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except gspread.exceptions.SpreadsheetNotFound:

        print(
            "[ERROR] "
            "ไม่พบ Spreadsheet"
        )


    except gspread.exceptions.APIError as e:

        print(
            "[ERROR] "
            "Google Sheets API Error:"
        )

        print(e)


    except FileNotFoundError:

        print(
            "[ERROR] "
            "ไม่พบ credentials.json"
        )


    except PermissionError:

        print(
            "[ERROR] "
            "ไม่มีสิทธิ์เข้าถึงไฟล์"
        )


    except Exception as e:

        print(
            "[ERROR] "
            f"{type(e).__name__}: {e}"
        )


    print(
        "========================================"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    update_summary()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()