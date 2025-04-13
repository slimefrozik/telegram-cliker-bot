from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import sqlite3, os
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
conn = sqlite3.connect('game.db')
cursor = conn.cursor()

# Создаём БД
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    coins DECIMAL(10,2) DEFAULT 0,
    click_power INTEGER DEFAULT 1,
    auto_income INTEGER DEFAULT 0
)''')
conn.commit()

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    
    web_app = types.WebAppInfo(url="https://your-site.com/game.html")
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton("🎮 Открыть игру", web_app=web_app)],
        [types.KeyboardButton("🏆 Лидеры"), types.KeyboardButton("💸 Передать монеты")]
    ], resize_keyboard=True)
    
    await message.answer("Добро пожаловать в кликер!", reply_markup=keyboard)

@dp.message(F.text == "🏆 Лидеры")
async def show_leaders(message: types.Message):
    cursor.execute("SELECT user_id, coins FROM users ORDER BY coins DESC LIMIT 10")
    leaders = cursor.fetchall()
    
    text = "Топ-10 игроков:\n"
    for i, (user_id, coins) in enumerate(leaders, 1):
        text += f"{i}. ID{user_id}: {coins} монет\n"
    
    await message.answer(text)

@dp.message(F.text == "💸 Передать монеты")
async def start_transfer(message: types.Message, state: FSMContext):
    await message.answer("Введите ID получателя и сумму (например: 123456 50)")
    await state.set_state("wait_transfer")

@dp.message(F.text.regexp(r'^\d+\s+\d+$'), F.state == "wait_transfer")
async def process_transfer(message: types.Message, state: FSMContext):
    sender_id = message.from_user.id
    receiver_id, amount = map(int, message.text.split())
    
    cursor.execute("SELECT coins FROM users WHERE user_id=?", (sender_id,))
    sender_coins = cursor.fetchone()[0]
    
    if sender_coins >= amount:
        commission = int(amount * 0.09)  # Комиссия 9%
        received = amount - commission
        
        cursor.execute("UPDATE users SET coins=coins-? WHERE user_id=?", (amount, sender_id))
        cursor.execute("UPDATE users SET coins=coins+? WHERE user_id=?", (received, receiver_id))
        conn.commit()
        
        await message.answer(
            f"✅ Передано {received} монет (комиссия {commission})\n"
            f"Новый баланс: {sender_coins - amount}"
        )
    else:
        await message.answer("❌ Недостаточно монет")
    
    await state.clear()

@dp.message()
async def handle_web_app_data(message: types.Message):
    if message.web_app_data:
        data = json.loads(message.web_app_data.data)
        user_id = message.from_user.id
        
        # Обновляем данные в БД
        cursor.execute('''UPDATE users SET 
                      coins=coins+?, 
                      click_power=click_power+?,
                      auto_income=auto_income+?
                      WHERE user_id=?''',
                   (data['coins'], data['click_power'], data['auto_income'], user_id))
        conn.commit()
        
        await message.answer(f"Прогресс сохранён! Монет: {data['coins']}")

if __name__ == "__main__":
    dp.run_polling(bot)