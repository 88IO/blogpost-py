import discord
import re
import os
import tweepy
from discord.ext import tasks
from config import CK, CS, AT, AS, BOT_TOKEN, TWITTER_URL, REQUEST_LIMIT
from regional_indicator import Letter


class Bot(discord.Client):
    def __init__(self):
        super().__init__()

        self.counter = 0

        auth = tweepy.OAuthHandler(CK, CS)
        auth.set_access_token(AT, AS)
        self.api = tweepy.API(auth)

        self.reset_counter.start()

    @tasks.loop(hours=3)
    async def reset_counter(self):
        self.counter = 0

    async def on_message(self, message):
        # 自身の場合は無視
        if message.author == self.user:
            return
        # 時間当たりのアクセス回数が多い場合は弾く
        if self.counter > REQUEST_LIMIT:
            await message.reply("API利用制限により処理できません")
            return
        # 自分へのメンション, また単独の場合（everyone避け）
        if self.user.mentioned_in(message) and len(message.raw_mentions) == 1:
            # メッセージが返信であれば、返信元を対象に変更
            if (reply_ref := message.reference):
                message = await message.channel.fetch_message(reply_ref.message_id)

            # メンション部分を削除
            content = re.sub("<@!.*>", "", message.content).lstrip(" 　\n")
            print(content)

            # 本文がブログのツイートURLの場合、該当ツイートを削除
            status_url = os.path.join(TWITTER_URL, "status", "")
            if re.fullmatch(os.path.join(status_url, "[0-9]+"), content):
                print("destroy_status")
                status_id = content.lstrip(status_url)
                self.api.destroy_status(status_id)
                for emoji in [Letter.D, Letter.E, Letter.S, Letter.T, Letter.R, Letter.O, Letter.Y]:
                    await message.add_reaction(emoji)
            # URLでない場合、本文をツイート
            else:
                print("update_status")
                status = self.api.update_status(content)
                for emoji in [Letter.U, Letter.P, Letter.D, Letter.A, Letter.T, Letter.E]:
                    await message.add_reaction(emoji)
                await message.reply(os.path.join(status_url, status.id_str))

            self.counter += 1

    async def on_ready(self):
        print("ready...")

if __name__ == "__main__":
    bot = Bot()
    bot.run(BOT_TOKEN)
