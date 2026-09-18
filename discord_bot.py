import asyncio
import discord

from main import (
    record_fuel,
    get_previous_odometer,
    default_data
)


# ============================================================
# CONFIG
# ============================================================

TOKEN = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

ALLOWED_CHANNEL_ID = 1542247032108875979

# เวลาที่ให้ User ตอบแต่ละคำถาม
INPUT_TIMEOUT = 60


# ============================================================
# DISCORD CLIENT
# ============================================================

intents = discord.Intents.default()
intents.message_content = True


class Client(discord.Client):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ป้องกัน User คนเดิมเปิด !fuel ซ้อนกัน
        self.active_fuel_users: set[int] = set()


    # ========================================================
    # ON READY
    # ========================================================

    async def on_ready(self):

        print("========================================")
        print("        DISCORD FUEL BOT")
        print("========================================")

        print(f"Logged in as: {self.user}")
        print(f"Allowed Channel ID: {ALLOWED_CHANNEL_ID}")

        print("========================================")


    # ========================================================
    # ON MESSAGE
    # ========================================================

    async def on_message(self, message):

        # ----------------------------------------------------
        # Ignore Bot
        # ----------------------------------------------------

        if message.author.bot:
            return


        # ----------------------------------------------------
        # Allowed Channel
        # ----------------------------------------------------

        if message.channel.id != ALLOWED_CHANNEL_ID:
            return


        # ----------------------------------------------------
        # Normalize Command
        # ----------------------------------------------------

        command = message.content.strip().lower()


        # ====================================================
        # !HELP
        # ====================================================

        if command == "!help":

            await self.help_command(message)

            return


        # ====================================================
        # !FUEL
        # ====================================================

        if command == "!fuel":

            await self.fuel_command(message)

            return


    # ========================================================
    # HELP
    # ========================================================

    async def help_command(self, message):

        await message.channel.send(
            f"{message.author.mention}\n"
            "```text\n"
            "Fuel Bot Commands\n"
            "\n"
            "!fuel\n"
            "บันทึกข้อมูลการเติมน้ำมัน\n"
            "\n"
            "!help\n"
            "แสดงรายการคำสั่ง\n"
            "\n"
            f"เวลาตอบแต่ละขั้นตอน: {INPUT_TIMEOUT} วินาที\n"
            "```"
        )


    # ========================================================
    # FUEL COMMAND
    # ========================================================

    async def fuel_command(self, message):

        user = message.author
        user_id = user.id


        # ----------------------------------------------------
        # Prevent Duplicate Session
        # ----------------------------------------------------

        if user_id in self.active_fuel_users:

            await message.channel.send(
                f"{user.mention}\n"
                "คุณกำลังบันทึกข้อมูลเติมน้ำมันอยู่แล้ว\n"
                "กรุณาทำรายการปัจจุบันให้เสร็จก่อน"
            )

            return


        self.active_fuel_users.add(user_id)


        try:

            # =================================================
            # GET PREVIOUS ODOMETER
            # =================================================

            try:

                previous_odometer = get_previous_odometer()

            except Exception as e:

                print(
                    "[ERROR] Cannot get previous odometer:"
                )
                print(e)

                await message.channel.send(
                    f"{user.mention}\n"
                    "❌ ไม่สามารถอ่านเลขไมล์จาก Google Sheets ได้\n"
                    "กรุณาลองใหม่อีกครั้ง"
                )

                return


            # -------------------------------------------------
            # No Previous Data
            # -------------------------------------------------

            if previous_odometer is None:

                await message.channel.send(
                    f"{user.mention}\n"
                    "❌ ไม่พบข้อมูลเลขไมล์ครั้งก่อนใน Google Sheets\n"
                    "กรุณาเพิ่มข้อมูลเริ่มต้นใน Google Sheets ก่อน"
                )

                return


            # =================================================
            # CURRENT ODOMETER
            # =================================================

            response = await self.ask_user(
                message,
                "กรุณาใส่เลขไมล์ปัจจุบัน (km):"
            )

            if response is None:
                return


            try:

                current_odometer = int(response)

            except ValueError:

                await self.send_invalid_number(message)

                return


            # -------------------------------------------------
            # Validate Current Odometer
            # -------------------------------------------------

            if current_odometer < 0:

                await message.channel.send(
                    f"{user.mention}\n"
                    "❌ เลขไมล์ต้องไม่น้อยกว่า 0\n"
                    "ยกเลิกการบันทึก"
                )

                return


            if current_odometer < previous_odometer:

                await message.channel.send(
                    f"{user.mention}\n"
                    "❌ เลขไมล์ปัจจุบันน้อยกว่าเลขไมล์ครั้งก่อน\n\n"
                    f"เลขไมล์ครั้งก่อน: "
                    f"{previous_odometer:,} km\n"
                    f"เลขไมล์ปัจจุบัน: "
                    f"{current_odometer:,} km\n\n"
                    "ยกเลิกการบันทึก"
                )

                return


            # =================================================
            # LITERS
            # =================================================

            response = await self.ask_user(
                message,
                "กรุณาใส่จำนวนลิตรที่เติม (L):"
            )

            if response is None:
                return


            try:

                liters = float(response)

            except ValueError:

                await self.send_invalid_number(message)

                return


            # -------------------------------------------------
            # Validate Liters
            # -------------------------------------------------

            if liters <= 0:

                await message.channel.send(
                    f"{user.mention}\n"
                    "❌ จำนวนลิตรต้องมากกว่า 0\n"
                    "ยกเลิกการบันทึก"
                )

                return


            # =================================================
            # TOTAL PRICE
            # =================================================

            response = await self.ask_user(
                message,
                "กรุณาใส่ราคาน้ำมันรวม (บาท):"
            )

            if response is None:
                return


            try:

                total_price = float(response)

            except ValueError:

                await self.send_invalid_number(message)

                return


            # -------------------------------------------------
            # Validate Price
            # -------------------------------------------------

            if total_price <= 0:

                await message.channel.send(
                    f"{user.mention}\n"
                    "❌ ราคาน้ำมันต้องมากกว่า 0\n"
                    "ยกเลิกการบันทึก"
                )

                return


            # =================================================
            # SEND TO MAIN.PY
            # =================================================

            await message.channel.send(
                f"{user.mention}\n"
                "⏳ กำลังบันทึกข้อมูลลง Google Sheets..."
            )


            try:

                fuel_data = record_fuel(
                    current_odometer,
                    liters,
                    total_price
                )

            except Exception as e:

                print(
                    "[ERROR] record_fuel():"
                )
                print(e)

                await message.channel.send(
                    f"{user.mention}\n"
                    "❌ ไม่สามารถบันทึกข้อมูลได้\n"
                    "กรุณาตรวจสอบ Terminal"
                )

                return


            # =================================================
            # SUCCESS
            # =================================================

            await message.channel.send(
                f"{user.mention}\n"
                "✅ **บันทึกข้อมูลเรียบร้อยแล้ว**\n"
                "\n"
                f"เชื้อเพลิง: "
                f"{default_data['FUEL_TYPE']}\n"
                f"รถ: "
                f"{default_data['CAR_MODEL']}\n"
                "\n"
                f"เลขไมล์ปัจจุบัน: "
                f"{fuel_data['CurrentOdometer']:,} km\n"
                f"เลขไมล์ครั้งก่อน: "
                f"{fuel_data['PreviousOdometer']:,} km\n"
                f"ระยะทาง: "
                f"{fuel_data['Distance']:,} km\n"
                "\n"
                f"เติมน้ำมัน: "
                f"{fuel_data['Liters']:.2f} L\n"
                f"ราคาต่อลิตร: "
                f"{fuel_data['ActualPrice']:.2f} บาท/L\n"
                f"ราคารวม: "
                f"{fuel_data['TotalPrice']:.2f} บาท\n"
                "\n"
                f"อัตราสิ้นเปลือง: "
                f"{fuel_data['FuelEffiency']:.2f} km/L"
            )


        finally:

            # -------------------------------------------------
            # Always Clear Session
            # -------------------------------------------------

            self.active_fuel_users.discard(user_id)


    # ========================================================
    # ASK USER
    # ========================================================

    async def ask_user(self, original_message, question):

        user = original_message.author
        channel = original_message.channel


        await channel.send(
            f"{user.mention}\n"
            f"{question}"
        )


        def check(response):

            return (
                response.author.id == user.id
                and response.channel.id == channel.id
                and not response.author.bot
            )


        try:

            response = await self.wait_for(
                "message",
                timeout=INPUT_TIMEOUT,
                check=check
            )

            return response.content.strip()


        except asyncio.TimeoutError:

            await channel.send(
                f"{user.mention}\n"
                "⏰ **หมดเวลาในการกรอกข้อมูล**\n\n"
                f"คุณไม่ได้ตอบภายใน {INPUT_TIMEOUT} วินาที\n"
                "รายการเติมน้ำมันนี้ถูกยกเลิก\n\n"
                "พิมพ์ `!fuel` เพื่อเริ่มใหม่"
            )

            return None


    # ========================================================
    # INVALID NUMBER
    # ========================================================

    async def send_invalid_number(self, message):

        await message.channel.send(
            f"{message.author.mention}\n"
            "❌ กรุณาใส่ตัวเลขเท่านั้น\n"
            "รายการเติมน้ำมันนี้ถูกยกเลิก"
        )


# ============================================================
# CREATE CLIENT
# ============================================================

client = Client(
    intents=intents
)


# ============================================================
# RUN
# ============================================================

client.run(TOKEN)

