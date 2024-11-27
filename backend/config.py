import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')
    MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1"

