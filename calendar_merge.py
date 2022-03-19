from pydoc import locate
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import csv
import urllib.request
import recurring_ical_events
import os

#Set date markers
start_date=input("What is the scheduler starting date? (in DD/MM/YYYY) ")  
start_date=datetime.strptime(start_date,"%d/%m/%Y").date()
start_date=datetime.combine(start_date,datetime.min.time()) 
end_date=input("What is the scheduler ending date? (in DD/MM/YYYY) ")  
end_date=datetime.strptime(end_date,"%d/%m/%Y").date() 
end_date=datetime.combine(end_date,datetime.max.time())

#Initializing master calendar
cal = Calendar()
cwd = os.getcwd()
location = cwd + "Experiments//"

#Canvas file
target_url = ""
canvas_file = urllib.request.urlopen(target_url)
calendar = Calendar.from_ical(canvas_file.read())
with open(location+"schedule.csv", 'w', newline='') as csvfile:
    schedulewriter = csv.writer(csvfile, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
    schedulewriter.writerow(["Summary", "Type", "Start", "End", "Duration"])
    events = recurring_ical_events.of(calendar).between(start_date, end_date)
    for event in events:
        if ('assignment' in event['uid']):
            cal.add_component(event)
            schedulewriter.writerow([event["SUMMARY"].replace (",",""), "To-do", (event["DTSTART"].dt-timedelta (hours=4)).replace(tzinfo=None), (event["DTEND"].dt-timedelta (hours=4)).replace(tzinfo=None)])
canvas_file.close()

#Scheduler file
scheduler_file = open (location+"scheduler.ics",'rb')
calendar = Calendar.from_ical(scheduler_file.read())
with open(location+"schedule.csv", 'a', newline='') as csvfile:
    schedulewriter = csv.writer(csvfile, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
    events = recurring_ical_events.of(calendar).between(start_date, end_date)
    for event in events:
        cal.add_component(event)
        schedulewriter.writerow([event["SUMMARY"].replace (",",""), "Class", event["DTSTART"].dt, event["DTEND"].dt, event["DTEND"].dt - event["DTSTART"].dt])
scheduler_file.close()

f = open(location+'optistudy_calendar.ics', 'wb')
f.write(cal.to_ical())
f.close()