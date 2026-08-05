from dotenv import load_dotenv
from pathlib import Path
import os


load_dotenv()
PATH_TO_DB = os.getenv("PATH_TO_DB")
print(PATH_TO_DB, 67)
