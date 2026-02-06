import asyncio
import logging
import datetime
import requests
from aiogram import Bot
from config import CHANNEL_ID
from storage import get_schedule, save_schedule


async def get_lviv_text_schedule():
    """Парсер JSON для Львова: перетворює yes/no у квадратики"""
    url = "https://raw.githubusercontent.com/yaroslav2901/OE_OUTAGE_DATA/main/data/Lvivoblenerho.json"
    try:
        logging.info("🌐 Отримання даних з GitHub...")
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            today_ts = str(data.get('today', ''))
            day_data = data.get('data', {}).get(today_ts, {})

            if not day_data:
                logging.warning("⚠️ Даних на сьогодні у файлі немає")
                return None

            text = f"📝 <b>ГРАФІК ЛЬВІВ</b>\n📅 {datetime.date.today().strftime('%d.%m.%Y')}\n\n"
            for group, hours in day_data.items():
                line = ""
                for h in range(1, 25):
                    status = str(hours.get(str(h), '')).lower()
                    line += "⬛" if status == 'no' else "⬜"
                text += f"<b>Гр {group}:</b>\n<code>{line}</code>\n"

            text += f"\n⬜-є світло | ⬛-немає\n🔗 <a href='https://poweron.loe.lviv.ua/'>Сайт</a>"
            return text
        else:
            logging.error(f"❌ Помилка сервера GitHub: {res.status_code}")
    except Exception as e:
        logging.error(f"❌ Помилка парсингу: {e}")
    return None


async def check_updates(bot: Bot):
    logging.info("🚀 Планувальник перевірки графіків запущено")
    while True:
        try:
            today = datetime.date.today().isoformat()

            # Тимчасово прибираємо перевірку бази, щоб графік скинувся зараз
            logging.info("🔍 Перевірка оновлень для Львова...")
            text = await get_lviv_text_schedule()

            if text:
                logging.info(f"📤 Надсилання графіка в канал {CHANNEL_ID}")
                await bot.send_message(CHANNEL_ID, text)
                logging.info("✅ Графік успішно опубліковано!")
                # save_schedule("lviv", today, "TEXT", "v1")
            else:
                logging.info("😴 Нових графіків поки немає")

        except Exception as e:
            logging.error(f"❌ Критична помилка у циклі: {e}")

        await asyncio.sleep(600)  # Перевірка кожні 10 хв


def setup_scheduler(bot: Bot):
    asyncio.create_task(check_updates(bot))