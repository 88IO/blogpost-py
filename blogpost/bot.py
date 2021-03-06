import discord
import re
import os
import tweepy
from discord.ext import tasks
from . import symbol_letter as Letter
from .config import CK, CS, AT, AS, BOT_TOKEN, TWITTER_URL, REQUEST_LIMIT


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
        print("reset counter")
        self.counter = 0

    async def on_message(self, message):
        # 自身の場合は無視
        if message.author == self.user or len(message.raw_mentions) != 1 or message.mention_everyone:
            return
        # 時間当たりのアクセス回数が多い場合は弾く
        if self.counter > REQUEST_LIMIT:
            await message.reply("API利用制限により処理できません")
            return
        # 自分へのメンション, また単独の場合（everyone避け）
        if self.user.mentioned_in(message):
            # メッセージが返信であれば、返信元を対象に変更
            if reply_ref := message.reference:
                message = await message.channel.fetch_message(reply_ref.message_id)

            # メンション部分を削除
            _content = re.sub("<@!?\d+>", "", message.content)
            # 頭の空白と"<>"を削除
            content = re.sub("^\s*(?:<(.*)>$)?", r"\1", _content)
            print("content:", content)

            # 空なら通知して終了
            if re.fullmatch("\s*", content):
                print("message is empty")
                await message.reply("メッセージが空です")
                return

            # 本文がブログのツイートURLの場合、該当ツイートを削除
            status_url = os.path.join(TWITTER_URL, "status", "")
            if match := re.match(os.path.join(status_url, "(\d+)"), content):
                status_id = match.group(1)
                print("destroy_status")
                self.api.destroy_status(status_id)
                for emoji in [Letter.D, Letter.E, Letter.S, Letter.T, Letter.R, Letter.O, Letter.Y]:
                    await message.add_reaction(emoji)
            # URLでない場合、本文をツイート
            else:
                print("update_status")
                status = self.api.update_status(content)
                for emoji in [Letter.U, Letter.P, Letter.D, Letter.A, Letter.T, Letter.E]:
                    await message.add_reaction(emoji)
                await message.reply("<{}>".format(os.path.join(status_url, status.id_str)))

            self.counter += 1
            print("counter:", self.counter)

    async def on_reaction_add(self, reaction, _):
        # "\U0000274C" is ❌
        if reaction.message.author == self.user and reaction.emoji == "\U0000274C":
            print("x reaction added")
            await reaction.message.delete()

    async def on_ready(self):
        print("ready...")
        await self.change_presence(
                activity=discord.Activity(type=discord.ActivityType.playing, name="https://scienceboy.jp"))


def main():
    bot = Bot()
    bot.run(BOT_TOKEN)

if __name__ == "__main__":
    main()
