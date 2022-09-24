import time
from datetime import datetime, timedelta

import requests

URL = "http://127.0.0.1:8080/api/v0/events"

DAYS_ON_DUTY = 2

TEAM_RED = ["d.kozlov", "r.leontev"]
TEAM_BLUE = ["d.gerasimov", "a.albertov"]
START_DATE = datetime.strptime("19 09 2022 10:00", "%d %m %Y %H:%M")

data = {"team": "", "start": "", "end": "", "role": "", "user": ""}
i = 0

while i <= 60:
    data["team"] = "BlueTeam"
    data["start"] = START_DATE + timedelta(days=i)
    data["start"] = time.mktime(data["start"].timetuple())
    data["end"] = START_DATE + timedelta(days=i) + timedelta(days=DAYS_ON_DUTY)
    data["end"] = time.mktime(data["end"].timetuple())
    data["user"] = TEAM_BLUE[0]
    data["role"] = "primary"
    requests.post(URL, json=data)

    data["user"] = TEAM_BLUE[1]
    data["role"] = "secondary"
    requests.post(URL, json=data)
    t = TEAM_BLUE[0]

    TEAM_BLUE[0] = TEAM_BLUE[1]
    TEAM_BLUE[1] = t

    data["team"] = "RedTeam"
    data["start"] = START_DATE + timedelta(days=i)
    data["start"] = time.mktime(data["start"].timetuple())
    data["end"] = START_DATE + timedelta(days=i) + timedelta(days=DAYS_ON_DUTY)
    data["end"] = time.mktime(data["end"].timetuple())
    data["user"] = TEAM_RED[0]
    data["role"] = "primary"
    requests.post(URL, json=data)

    data["user"] = TEAM_RED[1]
    data["role"] = "secondary"
    requests.post(URL, json=data)
    t = TEAM_RED[0]
    TEAM_RED[0] = TEAM_RED[1]
    TEAM_RED[1] = t

    i += DAYS_ON_DUTY
