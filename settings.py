import json
import os
import sys

def load_user_settings(file_path):

    with open(file_path) as json_file:
        userInfo = json.load(json_file)
    return userInfo

if __name__=="__main__":
    print(load_user_settings())
