from datetime import datetime
import config as c
from caldav.elements import dav, cdav

with open(c._path, 'r') as file:
    data = file.read()
    tasks = data.split("\n")
    duetasks = [task for task in tasks if "due:" in task]
    for task in duetasks:
        current_task = task.split(" ")
        for _ in current_task:
            if _.startswith("due:"):
                date = datetime.strptime(_[4:], "%Y-%m-%d")
                print(str(date))
