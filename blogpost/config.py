from dotenv import load_dotenv
import os


load_dotenv()

BOT_TOKEN = os.environ.get("DISCORD_TOKEN")
CK = os.environ.get("CK")
CS = os.environ.get("CS")
AT = os.environ.get("AT")
AS = os.environ.get("AS")
TWITTER_URL = os.environ.get("TWITTER_URL")
REQUEST_LIMIT = 300
