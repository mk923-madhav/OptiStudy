from pydoc import locate
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import csv
import urllib.request
import recurring_ical_events
from flask import Flask, render_template, request, json, session, redirect, url_for
import os

def create_calendar():
    #Set date markers
    start_date=str(request.form['startDate'])
    start_date=datetime.strptime(start_date,"%d/%m/%Y").date()
    start_date=datetime.combine(start_date,datetime.min.time()) 
    end_date=str(request.form['endDate']) 
    end_date=datetime.strptime(end_date,"%d/%m/%Y").date() 
    end_date=datetime.combine(end_date,datetime.max.time())

    #Initializing master calendar
    cal = Calendar()
    cwd = os.getcwd()
    location = os.path.join(cwd, "Experiments/", datetime.now().strftime("%m.%d.%Y,%H.%M.%S"))
    os.mkdir (location)
    location = location + "/"
    
    #Canvas file
    target_url = str(request.form['canvasURL'])
    print (target_url)
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