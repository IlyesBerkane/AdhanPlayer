import requests
from datetime import datetime, date, timedelta


def get_current_time():
    return datetime.now().strftime("%H:%M")


def add_one_hour(time_string):
    time_object = datetime.strptime(time_string, "%H:%M")
    updated_time = time_object + timedelta(hours=1)
    return updated_time.strftime("%H:%M")


MASJID_GUID = "85966a2e-4c6d-48fa-9aa8-c29d1052e51c"


def get_prayer_times():
    today = date.today()

    response = requests.get(
        "https://time.my-masjid.com/api/TimingsInfoScreen/OneWeekMultiSalahTimings",
        params={
            "Day": today.day,
            "Month": today.month,
            "GuidId": MASJID_GUID,
        },
    )

    response.raise_for_status()

    data = response.json()
    timings = data["model"]["salahTimings"]

    today_timing = None

    for day in timings:
        if day["day"] == today.day and day["month"] == today.month:
            today_timing = day
            break

    if today_timing is None:
        raise Exception("Could not find today's prayer timings")

    return {
        "Fajr": add_one_hour(today_timing["fajr"][0]["salahTime"]),
        "Dhuhr": add_one_hour(today_timing["zuhr"][0]["salahTime"]),
        "Asr": add_one_hour(today_timing["asr"][0]["salahTime"]),
        "Maghrib": add_one_hour(today_timing["maghrib"][0]["salahTime"]),
        "Isha": add_one_hour(today_timing["isha"][0]["salahTime"]),
    }


print(get_prayer_times())