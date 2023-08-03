import os

STATSBOMB_DATA = os.environ.get("STATSBOMB_DATA")
THREE_SIXTY = os.path.join(STATSBOMB_DATA, "three-sixty")
MATCHES = os.path.join(STATSBOMB_DATA, "matches")
EVENTS = os.path.join(STATSBOMB_DATA, "events")

GENDER = os.environ.get("GENDER")

if __name__ == "__main__":
    print(GENDER)
