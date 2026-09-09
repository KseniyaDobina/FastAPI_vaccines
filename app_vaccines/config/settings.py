from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
    KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
    KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
    PATH_TO_DB = os.getenv("PATH_TO_DB")
