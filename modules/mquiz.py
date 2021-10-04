import os
import pandas as pd
from dotenv import load_dotenv

# Utils
import helper.utils as utils

load_dotenv()


class MQuiz:
    def __init__(self, data, length, max_try):
        self.type = "mquiz"
        self.data = data
        self.current = 0
        self.total = 10 if length == 0 else length
        self.true = 0
        self.current_try = 0
        self.max_try = 3 if max_try == 0 else max_try

    def get_type(self):
        return self.type

    def get_data(self):
        return self.data

    def get_current(self):
        return self.current

    def get_true(self):
        return self.true

    def get_total(self):
        return self.total

    def check_max_try(self):
        return self.current_try == self.max_try

    def check_total(self):
        return self.current == self.total

    def increment_current(self):
        self.current += 1

    def increment_current_try(self):
        self.current_try += 1

    def increment_true(self):
        self.true += 1

    def reset_current_try(self):
        self.current_try = 0

    async def resume(self, message):
        current_row = self.get_data().iloc[self.get_current()]
        self.increment_current_try()
        if message.content.lower() == "0skip" or message.content.lower() == "0s":
            self.increment_current()
            self.reset_current_try()
            await message.channel.send("Question skipped.")
            await message.channel.send("Correct answer: {}; Hiragana: {}".format(current_row["Meaning"], current_row["Hiragana"]))
            finished = await self.check_finished(message)
            if finished:
                return True
            return
        splitted_message = message.content.lower().split(", ")
        found = False
        for i in range(len(splitted_message)):
            if splitted_message[i] in current_row["Meaning"].lower().split(", "):
                found = True

        if found:
            self.increment_current()
            self.increment_true()
            self.reset_current_try()
            await message.channel.send("Correct!")
            await message.channel.send("Correct answer: {}; Hiragana: {}".format(current_row["Meaning"], current_row["Hiragana"]))
            finished = await self.check_finished(message)
            if finished:
                return True
        else:
            if self.check_max_try():
                self.increment_current()
                self.reset_current_try()
                await message.channel.send("You have reached the max try, this question will be skipped.")
                await message.channel.send("Correct answer: {}; Hiragana: {}".format(current_row["Meaning"], current_row["Hiragana"]))
                finished = await self.check_finished(message)
                if finished:
                    return True
            else:
                await message.channel.send("Try again!")

    async def send_question(self, message):
        current_row = self.get_data().iloc[self.get_current()]
        await utils.text_to_image(message, current_row["Kanji"], self.get_current() + 1)

    async def check_finished(self, message):
        if self.check_total():
            await message.channel.send("Quiz finished with total true {true} of {total} questions".format(true=self.get_true(), total=self.get_total()))
            return True
        else:
            await self.send_question(message)


async def start(message, data, data_key, index=0, length=10, max_try=3):
    await message.channel.send("Starting Japanese meaning quiz...")
    URL = os.getenv("URL_MAIN")
    df = pd.read_csv(URL, encoding='utf-8')
    data[data_key] = MQuiz(df.sample(
        n=10 if length == 0 else length).reset_index(drop=True), length, max_try)
    await message.channel.send("Japanese meaning quiz started!")
    await data[data_key].send_question(message)
