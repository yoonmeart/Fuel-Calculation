# ============================================================
# FUEL CALCULATIONS
# ============================================================


# ============================================================
# FUEL PRICE
# ============================================================

def calculate_fuel_price(
    total_price: float,
    liters: float
) -> float:
    """
    คำนวณราคาน้ำมันต่อลิตร

    สูตร:

        Total Price / Liters

    ตัวอย่าง:

        200 / 6.09
        = 32.84 บาท/L
    """

    if liters <= 0:
        return 0.0

    return total_price / liters


# ============================================================
# DISTANCE
# ============================================================

def calculate_distance(
    current_odometer: int,
    previous_odometer: int
) -> int:


    return current_odometer - previous_odometer

def calculate_fuel_efficiency(distance:float, fuel_liters:float) -> float:  #Km/L
    return distance / fuel_liters 