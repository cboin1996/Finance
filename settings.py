import json
import os
import sys

def load_user_settings():
    dotenv_file_path = os.path.join(os.path.dirname(__file__), 'secret.json')
    dotenv.load_dotenv(dotenv_path=dotenv_file_path)

    userInfo = {}
    userInfo['sid'] = os.getenv('acct_sid')
    userInfo['auth_token'] = os.getenv('auth_token')
    return userInfo

if __name__=="__main__":
    load_user_settings()
