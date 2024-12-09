from openai import OpenAI
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

current_directory = os.path.dirname(os.path.abspath(__file__))

load_dotenv(dotenv_path=current_directory+"/../episodeManager/.env")

apikey = os.getenv("apikey")

client = OpenAI(api_key=apikey)

