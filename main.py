import discord
import os
import pandas as pd
import cutlet
import sys
from dotenv import load_dotenv


sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

katsu = cutlet.Cutlet()

client = discord.Client()

data = {}


async def start_rquiz(message, data_key, index=0, length=10, max_try=3):
    global data
    await message.channel.send("Starting Japanese reading quiz...")
    URL = os.getenv("URL_MAIN")
    df = pd.read_csv(URL, encoding='utf-8')
    data[data_key] = {
        "type": "rquiz",
        "data": df.sample(n=10 if length == 0 else length).reset_index(drop=True),
        "current": 0,
        "total": 10 if length == 0 else length,
        "true": 0,
        "current_try": 0,
        "max_try": 3 if max_try == 0 else max_try,
    }
    await message.channel.send("Japanese reading quiz started!")
    await send_rquiz_question(message, data_key)


async def continue_rquiz(message, data_key):
    global data
    current_row = data[data_key]["data"].iloc[data[data_key]["current"]]
    data[data_key]["current_try"] += 1
    if message.content.lower() == "0skip" or message.content.lower() == "0s":
        data[data_key]["current"] += 1
        data[data_key]["current_try"] = 0
        await message.channel.send("Question skipped.")
        await message.channel.send("Correct answer: {}".format(current_row["Hiragana"]))
        await send_rquiz_question(message, data_key)
        return
    if message.content == current_row["Hiragana"] or message.content.lower() == katsu.romaji(current_row["Hiragana"]).lower():
        data[data_key]["current"] += 1
        data[data_key]["true"] += 1
        data[data_key]["current_try"] = 0
        await message.channel.send("Correct!")
        await check_rquiz_finished(message, data_key)
    else:
        if data[data_key]["current_try"] == data[data_key]["max_try"]:
            data[data_key]["current"] += 1
            data[data_key]["current_try"] = 0
            await message.channel.send("You have reached the max try, this question will be skipped.")
            await message.channel.send("Correct answer: {}".format(current_row["Hiragana"]))
            await check_rquiz_finished(message, data_key)
        else:
            await message.channel.send("Try again!")


async def send_rquiz_question(message, data_key):
    global data
    current_row = data[data_key]["data"].iloc[data[data_key]["current"]]
    await message.channel.send("{number}. {kanji}".format(number=data[data_key]["current"] + 1, kanji=current_row["Kanji"]))


async def check_rquiz_finished(message, data_key):
    global data
    if data[data_key]["current"] == data[data_key]["total"]:
        await message.channel.send("Quiz finished with total true {true} of {total} questions".format(true=data[data_key]["true"], total=data[data_key]["total"]))
        data.pop(data_key)
    else:
        await send_rquiz_question(message, data_key)


def get_help():
    return "Help: "


@client.event
async def on_ready():
    print("Logged in")


@client.event
async def on_message(message):
    global data
    data_key = str(message.guild.id) + "+_+_+" + str(message.channel.id)
    if message.author == client.user:
        return
    if data.get(data_key, None):
        if message.content.lower() == "0exit" or message.content.lower() == "0e":
            data.pop(data_key)
            await message.channel.send("Exited from current activity.")
            return
        if data[data_key]["type"] == "rquiz":
            await continue_rquiz(message, data_key)
    else:
        if message.content.lower().startswith("0pri ") or message.content.lower().startswith("0p "):
            message_list = message.content.split(" ")
            second_message = message_list[1].lower()

            # Reading quiz
            if second_message == "rq" or second_message == "rquiz":
                try:
                    index = int(message_list[2] if len(message_list) > 2 else "0")
                    length = int(message_list[3] if len(message_list) > 3 else "10")
                    max_try = int(message_list[4] if len(message_list) > 4 else "3")
                    await start_rquiz(message, data_key, index, length, max_try)
                except ValueError:
                    print(ValueError)
                    return
        elif message.content.lower() == "0pri" or message.content.lower() == "0p":
            await message.channel.send(get_help())

client.run(os.getenv("TOKEN"))
