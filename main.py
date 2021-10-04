import discord
import os
import sys
from dotenv import load_dotenv

# Modules
import modules.rquiz as rquiz
import modules.mquiz as mquiz


sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

client = discord.Client()

data = {}


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

        # Reading quiz
        if data[data_key].get_type() == "rquiz":
            finished = await data[data_key].resume(message)
            if finished:
                data.pop(data_key)

        # Meaning quiz
        if data[data_key].get_type() == "mquiz":
            finished = await data[data_key].resume(message)
            if finished:
                data.pop(data_key)
    else:
        if message.content.lower().startswith("0pri ") or message.content.lower().startswith("0p "):
            message_list = message.content.split(" ")
            second_message = message_list[1].lower()

            # Reading quiz
            if second_message == "rq" or second_message == "rquiz":
                try:
                    index = int(message_list[2] if len(
                        message_list) > 2 else "0")
                    length = int(message_list[3] if len(
                        message_list) > 3 else "10")
                    max_try = int(message_list[4] if len(
                        message_list) > 4 else "3")
                    await rquiz.start(message, data, data_key, index, length, max_try)
                except ValueError as e:
                    print(str(e))
                    return

            # Meaning quiz
            if second_message == "mq" or second_message == "mquiz":
                try:
                    index = int(message_list[2] if len(
                        message_list) > 2 else "0")
                    length = int(message_list[3] if len(
                        message_list) > 3 else "10")
                    max_try = int(message_list[4] if len(
                        message_list) > 4 else "3")
                    await mquiz.start(message, data, data_key, index, length, max_try)
                except ValueError as e:
                    print(str(e))
                    return

        elif message.content.lower() == "0pri" or message.content.lower() == "0p":
            await message.channel.send(get_help())

client.run(os.getenv("TOKEN"))
