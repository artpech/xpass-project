import os

PROJECT_HOME = os.environ.get("PROJECT_HOME")

STATSBOMB_DATA = os.environ.get("STATSBOMB_DATA")
THREE_SIXTY = os.path.join(STATSBOMB_DATA, "three-sixty")
MATCHES = os.path.join(STATSBOMB_DATA, "matches")
EVENTS = os.path.join(STATSBOMB_DATA, "events")

GENDER = os.environ.get("GENDER")

SIZE = os.environ.get("SIZE")
SIZE_MAP = {
    "S" : int(os.environ.get("SIZE_S")),
    "M" : int(os.environ.get("SIZE_M"))
}

if __name__ == "__main__":
    print(GENDER)
