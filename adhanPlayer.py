import requests
import time
from datetime import datetime, date, timedelta
import subprocess

MASJID_GUID = "85966a2e-4c6d-48fa-9aa8-c29d1052e51c"
SOUNDBAR_MAC = "34:E6:E6:76:EC:8A"

ADHAN_FILES = {
    "Fajr": "fajradhan.mp3",
    "Dhuhr": "adhan.mp3",
    "Asr": "adhan.mp3",
    "Maghrib": "adhan.mp3",
    "Isha": "adhan.mp3",
}


def get_current_time():
    return datetime.now().strftime("%H:%M")


def add_one_hour(time_string):
    time_object = datetime.strptime(time_string, "%H:%M")
    updated_time = time_object + timedelta(hours=1)
    return updated_time.strftime("%H:%M")


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


def connect_bluetooth():
    subprocess.run(["bluetoothctl", "connect", SOUNDBAR_MAC])


def disconnect_bluetooth():
    subprocess.run(["bluetoothctl", "disconnect", SOUNDBAR_MAC])


def play_adhan(prayer):
    adhan_file = ADHAN_FILES[prayer]

    print(f"Playing {adhan_file} for {prayer}")

    connect_bluetooth()
    time.sleep(5)

    subprocess.run(["mpg123", adhan_file])

    disconnect_bluetooth()


prayer_times = get_prayer_times()
last_updated = date.today()

print("Loaded prayer times:", prayer_times)

while True:
    if date.today() != last_updated:
        prayer_times = get_prayer_times()
        last_updated = date.today()
        print("Updated prayer times:", prayer_times)

    current_time = get_current_time()

    for prayer, prayer_time in prayer_times.items():
        if current_time == prayer_time:
            print(f"It's time for {prayer}")
            play_adhan(prayer)

            while get_current_time() == prayer_time:
                time.sleep(1)

    time.sleep(30)

