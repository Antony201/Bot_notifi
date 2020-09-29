import logging

from aiogram.utils.exceptions import BotBlocked
from aiogram import Bot, Dispatcher, executor, types
import asyncio

import requests
from bs4 import BeautifulSoup

from config import API_TOKEN, url, headers
import  dbworker


logging.basicConfig(level=logging.INFO)


loop = asyncio.get_event_loop()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, loop=loop)



async def add_to_db(msg):
    dbworker.init_db()
    dbworker.add_user(user_id=msg.from_user.id)

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await add_to_db(message)
    await message.reply("Вы добавлены для розсылки")


async def send_everyone(liga, detail_match):
    users = dbworker.get_users()
    print("Helo")
    print(users)
    for user in users:
        user_id = user[0]
        try:
            await bot.send_message(user_id, f"""
                                                Лига - {liga}
Детали - {detail_match}
                                                """)

        except BotBlocked:
            print("Bot blocked by User")
            dbworker.delete_user(user_id=user_id)


async def sheduled(wait_for):
    dbworker.init_db()
    while True:
        await asyncio.sleep(wait_for)
        s = requests.Session()
        r = s.get(url, headers=headers)

        soup = BeautifulSoup(r.content, "lxml")

        divs = soup.find_all("div", attrs={"class": "tournaments-item"})

        print("check")

        for div in divs:
            match = div.find("h3").text.strip()
            times = div.find_all("div", attrs={"class": "tournaments-match"})

            if len(times) == 1 and ("Мир" not in match and "Другие" not in match):
                status = times[0].find("span", attrs={"class": "status"}).text.strip()
                hour = times[0].find("span", attrs={"class": "data"}).text.strip()
                time = times[0].find("div", attrs={"class": "teams"})
                teams = time.find_all("div", attrs={"class": "team"})
                points = time.find_all("span", attrs={"class": "point"})

                try:
                    team_1 = teams[0].text.strip()
                    team_2 = teams[1].text.strip()
                    point_1 = points[0].text.strip()
                    point_2 = points[1].text.strip()
                    detail = (hour, team_1, point_1, point_2, team_2)

                except Exception as e:
                    print(e)

                if ((int(point_1) == 1 and int(point_2) == 1) or (int(point_1) == 2 and int(point_2) == 0)) \
                        and status != "Завершен" and detail not in dbworker.get_last_footballs() :
                    print(match)

                    print(detail[0], detail[1], detail[2], ":", detail[3], detail[4])
                    top_match = {
                        "liga": match,
                        "game_detail": f"{detail[0]} {detail[1]} {detail[2]} : {detail[3]} {detail[4]}"
                    }

                    await send_everyone(top_match["liga"], top_match["game_detail"])
                    print(top_match)
                    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

                    dbworker.insert_foot_game(detail=detail)


if __name__ == '__main__':
    dp.loop.create_task(sheduled(1))
    executor.start_polling(dp, skip_updates=True)

