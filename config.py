from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN=os.getenv("BOT_TOKEN")
ADMIN_IDS=os.getenv("ADMIN_IDS")
BD_URL_POSTGRES=os.getenv("BD_URL_POSTGRES")
YK_TEST_TOKEN=os.getenv("YK_TEST_TOKEN")

def is_admin(user_id: str | int):
    if str(user_id) in ADMIN_IDS:
        return True
    return False