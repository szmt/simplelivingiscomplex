from datetime import datetime, date, timedelta
import caldav
from caldav.elements import dav, cdav
import uuid
import requests
from requests.auth import HTTPBasicAuth
import configparser
import pathlib


# Writing to calendar
def save_to_calendar(_, task):
    event_summary = ""
    for _ in task:
        # Removing due date
        if config['behaviour']['remove_due']== "1":
            if not _.startswith("due:"):
                event_summary += _ + " "
        else:
            event_summary += _ + " "

    event_summary = event_summary[:-1]

    todo_date = datetime.strptime(_[4:], "%Y-%m-%d")
    today = date.today().strftime("%Y%m%d")
    uid = uuid.uuid4()
    event_date = todo_date.strftime("%Y%m%d")
    event_end = (todo_date + timedelta(days=1)).strftime("%Y%m%d")
    event = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:SimpleLivingIsComplex
BEGIN:VEVENT
UID:{uid}@acrylnimbus.de
DTSTAMP:{today}T060000Z
DTSTART;VALUE=DATE:{event_date}
DTEND;VALUE=DATE:{event_end}
SUMMARY:{event_summary}
END:VEVENT
END:VCALENDAR
"""
    print("created: " + event_summary)
    cal.save_event(event)


# Reading todos
def get_todos():
    # From local file
    if config['source']['local']== "1":
        local_path = config['source']['local_path']
        fs = open(local_path)
        content = fs.read()
        fs.close()
        return content
    # From webdav file
    else:
        remote_path = config['source']['remote_path']
        remote_user = config['source']['remote_user']
        remote_pass = config['source']['remote_pass']
        r = requests.request(
            method='get',
            url=remote_path,
            auth=(remote_user, remote_pass)
        )
        return r.text

# Read Configuration
config = configparser.ConfigParser()
config.read(str(pathlib.Path(__file__).parent.absolute())+"/config.ini")

# Setting up the calendar connection
calendar_protocol = config['calendar']['calendar_protocol']
calendar_user = config['calendar']['calendar_user']
calendar_pass = config['calendar']['calendar_pass']
calendar_url = config['calendar']['calendar_url']
calendar_name = config['calendar']['calendar_name']

url = calendar_protocol + calendar_user + ":" + calendar_pass + "@" + calendar_url
client = caldav.DAVClient(url)
principal = client.principal()
calendars = principal.calendars()

print("__ simple living is complex __")

for cal in calendars:
    namedict = cal.get_properties([dav.DisplayName()])
    if namedict["{DAV:}displayname"] == calendar_name:
        # Deleting ALL old entries
        if config['behaviour']['delete_old'] == "1":
            for ev in cal.events():
                ev.load()
                e = ev.instance.vevent
                print("deleted: " + str(e.summary.value))
                ev.delete()

        data = get_todos()
        tasks = data.split("\n")
        duetasks = [task.replace("\r","") for task in tasks if "due:" in task]
        for task in duetasks:
            current_task = task.split(" ")
            for _ in current_task:
                # Saving all entries with a due date
                if _.startswith("due:"):
                    save_to_calendar(_, current_task)
