import pandas as pd
import re
import requests, json
import urllib.parse
import ast

# Local
from util import get_data, split_and_format_text

base_url = "http://127.0.0.1:8000/"

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


def initialize(userId):
    url = base_url + "initialize"

    dic = {
		"userId" : userId,
	}
    r = requests.post(base_url, data=json.dumps(dic))
    return r.json()

def chat(userId, query, isTest, checkContext):
    url = base_url + "chat"
    dic = {
		"userId" : userId,
        "query" : query,
        "isTest" : isTest,
        "checkContext" : checkContext
	}


if __name__ == "__main__":

