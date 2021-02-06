from datetime import datetime, date, timedelta
import config as c
import caldav
from caldav.elements import dav, cdav
import uuid
import requests
from requests.auth import HTTPBasicAuth

def save_to_calendar(_, task):
    event_summary = ""
    for _ in task:
        if c._remove_due:
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
PRODID:In Acryl We Trust
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

def get_todos():
    if c._local:
        fs = open(c._local_path,'r')
        content = fs.read()
        print(content)
        fs.close()
        return content
    else:
        r = requests.request(
            method='get',
            url=c._remote_path,
            auth=(c._calendar_user, c._calendar_pass)
        )
        return r.text


url = c._calendar_protocol+c._calendar_user+":"+c._calendar_pass+"@"+c._calendar_url
client = caldav.DAVClient(url)
principal = client.principal()
calendars = principal.calendars()

for cal in calendars:
    namedict = cal.get_properties([dav.DisplayName()])
    if namedict["{DAV:}displayname"] == c._calendar_name:
        # Deleting ALL old entries
        if c._delete_old == True:
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
