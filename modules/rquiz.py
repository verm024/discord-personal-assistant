import os
import pandas as pd
import cutlet
from dotenv import load_dotenv

load_dotenv()
katsu = cutlet.Cutlet()


class RQuiz:
    def __init__(self, data, length, max_try):
        self.type = "rquiz"
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
            await message.channel.send("Correct answer: {}".format(current_row["Hiragana"]))
            await self.send_question(message)
            return
        if message.content == current_row["Hiragana"] or message.content.lower() == katsu.romaji(current_row["Hiragana"]).lower():
            self.increment_current()
            self.increment_true()
            self.reset_current_try()
            await message.channel.send("Correct!")
            finished = await self.check_finished(message)
            if finished:
                return True
        else:
            if self.check_max_try():
                self.increment_current()
                self.reset_current_try()
                await message.channel.send("You have reached the max try, this question will be skipped.")
                await message.channel.send("Correct answer: {}".format(current_row["Hiragana"]))
                finished = await self.check_finished(message)
                if finished:
                    return True
            else:
                await message.channel.send("Try again!")

    async def send_question(self, message):
        current_row = self.get_data().iloc[self.get_current()]
        await message.channel.send("{number}. {kanji}".format(number=self.get_current() + 1, kanji=current_row["Kanji"]))

    async def check_finished(self, message):
        if self.check_total():
            await message.channel.send("Quiz finished with total true {true} of {total} questions".format(true=self.get_true(), total=self.get_total()))
            return True
        else:
            await self.send_question(message)


async def start(message, data, data_key, index=0, length=10, max_try=3):
    await message.channel.send("Starting Japanese reading quiz...")
    URL = os.getenv("URL_MAIN")
    df = pd.read_csv(URL, encoding='utf-8')
    data[data_key] = RQuiz(df.sample(
        n=10 if length == 0 else length).reset_index(drop=True), length, max_try)
    await message.channel.send("Japanese reading quiz started!")
    await data[data_key].send_question(message)
