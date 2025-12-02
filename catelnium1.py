import asyncio
import logging
import json
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from docx import Document

# --- SOZLAMALAR ---
BOT_TOKEN = "8217853009:AAH7JUesU_iZsv1R55iBaQAcJ-1WI0qBmMw"  # Tokenni qo'ying
ADMIN_ID = 5341602920  # O'zingizning ID raqamingizni qo'ying
DB_FILE = "baza.json"

# --- O'ZBEKISTONNING BARCHA VILOYAT VA TUMANLARI ---
REGIONS = {
    "Toshkent shahri": ["Bektemir", "Chilonzor", "Mirobod", "Mirzo Ulug'bek", "Olmazor", "Sergeli", "Shayxontohur",
                        "Uchtepa", "Yakkasaroy", "Yangihayot", "Yashnobod", "Yunusobod"],
    "Toshkent viloyati": ["Angren sh", "Bekobod sh", "Chirchiq sh", "Nurafshon sh", "Olmaliq sh", "Ohangaron sh",
                          "Yangiyo'l sh", "Bekobod", "Bo'ka", "Bo'stonliq", "Chinoz", "Qibray", "Ohangaron",
                          "Oqqo'rg'on", "Parkent", "Piskent", "Quyi Chirchiq", "O'rta Chirchiq", "Yangiyo'l",
                          "Yuqori Chirchiq", "Zangiota", "Toshkent tumani"],
    "Andijon viloyati": ["Andijon sh", "Xonobod sh", "Andijon", "Asaka", "Baliqchi", "Bo'z", "Buloqboshi", "Izboskan",
                         "Jalaquduq", "Marhamat", "Oltinko'l", "Paxtaobod", "Shahrixon", "Ulug'nor", "Xo'jaobod",
                         "Qo'rg'ontepa"],
    "Buxoro viloyati": ["Buxoro sh", "Kogon sh", "Buxoro", "G'ijduvon", "Jondor", "Kogon", "Olot", "Peshku", "Qorako'l",
                        "Qorovulbozor", "Romitan", "Shofirkon", "Vobkent"],
    "Farg'ona viloyati": ["Farg'ona sh", "Marg'ilon sh", "Qo'qon sh", "Quvasoy sh", "Beshariq", "Bog'dod", "Buvayda",
                          "Dang'ara", "Farg'ona", "Furqat", "Oltiariq", "Qo'shtepa", "Quva", "Rishton", "So'x",
                          "Toshloq", "Uchko'priq", "Yozyovon", "O'zbekiston"],
    "Jizzax viloyati": ["Jizzax sh", "Arnasoy", "Baxmal", "Do'stlik", "Forish", "G'allaorol", "Sharof Rashidov",
                        "Mirzacho'l", "Paxtakor", "Yangiobod", "Zafarobod", "Zarbdor", "Zomin"],
    "Xorazm viloyati": ["Urganch sh", "Xiva sh", "Bog'ot", "Gurlan", "Qo'shko'pir", "Shovot", "Urganch", "Xiva",
                        "Xonqa", "Hazorasp", "Yangibozor", "Yangiariq"],
    "Namangan viloyati": ["Namangan sh", "Chortoq", "Chust", "Kosonsoy", "Mingbuloq", "Namangan", "Norin", "Pop",
                          "To'raqo'rg'on", "Uchqo'rg'on", "Uychi", "Yangiqo'rg'on"],
    "Navoiy viloyati": ["Navoiy sh", "Zarafshon sh", "Karmana", "Konimex", "Navbahor", "Nurota", "Qiziltepa", "Tomdi",
                        "Uchquduq", "Xatirchi"],
    "Qashqadaryo viloyati": ["Qarshi sh", "Shahrisabz sh", "Chiroqchi", "Dehqonobod", "G'uzor", "Kasbi", "Kitob",
                             "Koson", "Mirishkor", "Muborak", "Nishon", "Qamashi", "Qarshi", "Shahrisabz", "Yakkabog'"],
    "Qoraqalpog'iston Respublikasi": ["Nukus sh", "Amudaryo", "Beruniy", "Chimboy", "Ellikqal'a", "Kegeyli", "Mo'ynoq",
                                      "Nukus", "Qanliko'l", "Qo'ng'irot", "Qorao'zak", "Shumanay", "Taxtako'pir",
                                      "To'rtko'l", "Xo'jayli", "Taxiatosh"],
    "Samarqand viloyati": ["Samarqand sh", "Kattaqo'rg'on sh", "Bulung'ur", "Ishtixon", "Jomboy", "Kattaqo'rg'on",
                           "Narpay", "Nurobod", "Oqdaryo", "Pastdarg'om", "Paxtachi", "Payariq", "Qo'shrabot",
                           "Samarqand", "Toyloq", "Urgut"],
    "Sirdaryo viloyati": ["Guliston sh", "Yangiyer sh", "Shirin sh", "Boyovut", "Guliston", "Mirzaobod", "Oqoltin",
                          "Sardoba", "Sayxunobod", "Sirdaryo", "Xovos"],
    "Surxondaryo viloyati": ["Termiz sh", "Angor", "Bandixon", "Boysun", "Denov", "Jarqo'rg'on", "Muzrabot", "Oltinsoy",
                             "Qiziriq", "Qumqo'rg'on", "Sariosiyo", "Sherobod", "Sho'rchi", "Termiz", "Uzun"]
}


# --- YORDAMCHI FUNKSIYALAR ---
def load_data():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_data(new_record):
    data = load_data()
    data.append(new_record)
    with open(DB_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def clear_data():
    with open(DB_FILE, 'w', encoding='utf-8') as file:
        json.dump([], file)


def generate_word_file(data):
    doc = Document()
    doc.add_heading("Muassasalar bo'yicha hisobot", 0)

    table = doc.add_table(rows=1, cols=9)
    table.style = 'Table Grid'

    hdr_cells = table.rows[0].cells
    headers = ["Viloyat", "Tuman", "Turi", "Nomi", "Xonalar", "Direktor", "Tel", "Lokatsiya", "Link"]
    for i, text in enumerate(headers):
        hdr_cells[i].text = text

    for item in data:
        row_cells = table.add_row().cells
        row_cells[0].text = item.get('region', '')
        row_cells[1].text = item.get('district', '')
        row_cells[2].text = item.get('type', '')
        row_cells[3].text = item.get('name', '')
        row_cells[4].text = str(item.get('rooms', ''))
        row_cells[5].text = item.get('director', '')
        row_cells[6].text = item.get('phone', '')
        row_cells[7].text = f"{item.get('latitude')}, {item.get('longitude')}"
        row_cells[8].text = item.get('map_link', '')

    filename = "hisobot.docx"
    doc.save(filename)
    return filename


# --- STATES ---
class Form(StatesGroup):
    region = State()
    district = State()
    inst_type = State()
    inst_name = State()
    room_count = State()
    director = State()
    phone = State()
    location = State()


# --- BOT ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ---------------- O'ZGARISH KIRITILGAN START QISMI ----------------
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # ID ni konsolga chiqarish (Siz shu yerdan ko'rib olasiz)
    print(f"\n\n!!! SIZNING ID RAQAMINGIZ: {user_id} !!!\n\n")

    # ADMIN UCHUN ALOHIDA MENYU
    if user_id == ADMIN_ID:
        admin_buttons = [
            [KeyboardButton(text="📥 WORD Hisobotni olish")],
            [KeyboardButton(text="📝 Ma'lumot qo'shish (Anketa)")]  # Yangi tugma
        ]
        admin_kb = ReplyKeyboardMarkup(keyboard=admin_buttons, resize_keyboard=True)

        await message.answer("Xush kelibsiz, Admin! Nima qilamiz?", reply_markup=admin_kb)
        return  # <--- BU MUHIM: Kod shu yerda to'xtaydi, pastga o'tib ketmaydi

    # ODDIY FOYDALANUVCHI UCHUN MENYU
    await show_region_keyboard(message, state)


# --- ADMIN "MA'LUMOT QO'SHISH" BOSGANDA ---
@dp.message(F.text == "📝 Ma'lumot qo'shish (Anketa)")
async def admin_start_survey(message: Message, state: FSMContext):
    await show_region_keyboard(message, state)


# --- VILOYATLARNI CHIQARUVCHI YORDAMCHI FUNKSIYA ---
async def show_region_keyboard(message: Message, state: FSMContext):
    region_names = list(REGIONS.keys())
    buttons = []
    row = []
    for name in region_names:
        row.append(KeyboardButton(text=name))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Assalomu alaykum! Iltimos, Viloyatni tanlang:", reply_markup=kb)
    await state.set_state(Form.region)


# ------------------------------------------------------------------

# 2. Viloyat -> Tuman
@dp.message(Form.region)
async def process_region(message: Message, state: FSMContext):
    region = message.text
    if region not in REGIONS:
        await message.answer("Iltimos, tugmalardan birini tanlang.")
        return

    await state.update_data(region=region)
    districts = REGIONS[region]
    buttons = []
    row = []
    for dist in districts:
        row.append(KeyboardButton(text=dist))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer(f"Tanlandi: {region}. Endi Tumanni tanlang:", reply_markup=kb)
    await state.set_state(Form.district)


# 3. Tuman -> Turi
@dp.message(Form.district)
async def process_district(message: Message, state: FSMContext):
    await state.update_data(district=message.text)
    buttons = [
        [KeyboardButton(text="Maktab"), KeyboardButton(text="MTT")],
        [KeyboardButton(text="Oilaviy poliklinika")]
    ]
    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Muassasa turini tanlang:", reply_markup=kb)
    await state.set_state(Form.inst_type)


# 4. Turi -> Nomi
@dp.message(Form.inst_type)
async def process_type(message: Message, state: FSMContext):
    if message.text not in ["Maktab", "MTT", "Oilaviy poliklinika"]:
        await message.answer("Tugmalardan birini tanlang.")
        return
    await state.update_data(type=message.text)
    await message.answer("Muassasa raqami yoki nomini yozing (Masalan: 14-maktab):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.inst_name)


# 5. Nomi -> Xonalar
@dp.message(Form.inst_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("O'quv xonalar sonini kiriting (faqat raqam):")
    await state.set_state(Form.room_count)


# 6. Xonalar -> Direktor
@dp.message(Form.room_count)
async def process_rooms(message: Message, state: FSMContext):
    await state.update_data(rooms=message.text)
    await message.answer("Direktorning F.I.O.sini to'liq yozing:")
    await state.set_state(Form.director)


# 7. Direktor -> Tel
@dp.message(Form.director)
async def process_director(message: Message, state: FSMContext):
    await state.update_data(director=message.text)
    await message.answer("Telefon raqamni kiriting (Masalan: +998901234567):")
    await state.set_state(Form.phone)


# 8. Tel -> Lokatsiya
@dp.message(Form.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Lokatsiyani yuborish 📍", request_location=True)]],
                             resize_keyboard=True)
    await message.answer("Muassasa lokatsiyasini yuboring:", reply_markup=kb)
    await state.set_state(Form.location)


# 9. Lokatsiya -> SAQLASH
@dp.message(Form.location, F.location)
async def process_location(message: Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    link = f"https://www.google.com/maps?q={lat},{lon}"

    data = await state.get_data()
    data['latitude'] = lat
    data['longitude'] = lon
    data['map_link'] = link

    save_data(data)

    # --- ADMIN QAYTA START BOSMASLIGI UCHUN ---
    # Agar bu odam Admin bo'lsa, unga yana Admin panelni ko'rsatamiz
    if message.from_user.id == ADMIN_ID:
        admin_buttons = [
            [KeyboardButton(text="📥 WORD Hisobotni olish")],
            [KeyboardButton(text="📝 Ma'lumot qo'shish (Anketa)")]
        ]
        admin_kb = ReplyKeyboardMarkup(keyboard=admin_buttons, resize_keyboard=True)
        await message.answer("✅ Ma'lumotlar saqlandi! Yana nima qilamiz?", reply_markup=admin_kb)
    else:
        # Oddiy odamga shunchaki rahmat deymiz
        await message.answer("✅ Ma'lumotlar qabul qilindi! Rahmat.", reply_markup=ReplyKeyboardRemove())

    await state.clear()


# --- ADMIN PANEL ---
@dp.message(F.text == "📥 WORD Hisobotni olish")
async def admin_get_report(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    data = load_data()
    if not data:
        await message.answer("Hozircha ma'lumotlar yo'q.")
        return

    await message.answer("Hisobot tayyorlanmoqda... ⏳")

    filename = generate_word_file(data)
    file = FSInputFile(filename)
    await message.answer_document(file, caption="Mana siz so'ragan hisobot 📄")

    clear_data()
    await message.answer("🗑 Bazadagi eski ma'lumotlar tozalandi.")

    if os.path.exists(filename):
        os.remove(filename)


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi")