from datetime import datetime, date, timedelta
import config as c
import caldav
from caldav.elements import dav, cdav
import uuid

def save_to_calendar(_, task):
    todo_date = datetime.strptime(_[4:], "%Y-%m-%d")
    today = date.today().strftime("%Y%m%d")
    uid = uuid.uuid4()
    event_date = todo_date.strftime("%Y%m%d")
    event_end = (todo_date + timedelta(days=1)).strftime("%Y%m%d")
    event_summary = task
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


url = c._calendar_protocol+c._calendar_user+":"+c._calendar_pass+"@"+c._calendar_url
client = caldav.DAVClient(url)
principal = client.principal()
calendars = principal.calendars()

for cal in calendars:
    namedict = cal.get_properties([dav.DisplayName()])
    if namedict["{DAV:}displayname"] == c._calendar_name:
        # Deleting ALL old entries
        for ev in cal.events():
            ev.load()
            e = ev.instance.vevent
            print("deleted: " + str(e.summary.value))
            ev.delete()

        # opening todo file
        with open(c._path, 'r') as file:
            data = file.read()
            tasks = data.split("\n")
            duetasks = [task for task in tasks if "due:" in task]
            for task in duetasks:
                current_task = task.split(" ")
                for _ in current_task:
                    # Saving all entries with a due date
                    if _.startswith("due:"):
                        save_to_calendar(_, task)
