import os
from pathlib import Path
from typing import TypedDict
from dotenv import load_dotenv



class EnvSettings(TypedDict):
    DATABASE_URL: str



class EnvClass:
    def __init__(self):
        self.env: EnvSettings = {
            "DATABASE_URL": "sqlite:///./database.db"
            }

        if (Path().parent / '.env').exists():
            load_dotenv(Path().parent / '.env')

        current_env = dict(os.environ.items())
        for key in self.env.keys():
            if key in current_env.keys():
                try:
                    self.env[key] = int(current_env[key])
                except:
                    self.env[key] = current_env[key]
            else:
                print(f'{key} didn\'t find in environment. Use default value - {self.env[key]}')