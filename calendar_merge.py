from collections import Counter
from pydoc import locate
from icalendar import Calendar, Event
from datetime import datetime, timedelta, timezone
import csv
import urllib.request
import recurring_ical_events
from flask import Flask, render_template, request, json, session, redirect, url_for
import os

def create_calendar(location, start_date, end_date):
    #Initializing master calendar
    cal = Calendar()
    location = location + "/"
    display_events = []
    
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
                display_event = {
                    'todo' : event["SUMMARY"],
                    'start' :(event["DTSTART"].dt-timedelta (hours=4)).replace(tzinfo=None),
                    'end' : (event["DTEND"].dt-timedelta (hours=4)).replace(tzinfo=None)
                }
                display_events.append (display_event)
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
<<<<<<< HEAD
            display_event = {
                'todo' : event["SUMMARY"],
                'start' :event["DTSTART"].dt,
                'end' : event["DTEND"].dt
            }
            display_events.append (display_event)
            schedulewriter.writerow([event["SUMMARY"].replace (",",""), "Class", event["DTSTART"].dt, event["DTEND"].dt, event["DTEND"].dt - event["DTSTART"].dt])
=======
            schedulewriter.writerow([event["SUMMARY"].replace (",",""), "Class", event["DTSTART"].dt, (event["DTEND"].dt-timedelta (hours=4)).replace(tzinfo=None), event["DTEND"].dt - event["DTSTART"].dt])
>>>>>>> 44f6bcff438cafdf51be3670a7d825b8092517d1
    scheduler_file.close()

    f = open(location+'optistudy_calendar.ics', 'wb')
    f.write(cal.to_ical())
    f.close()

<<<<<<< HEAD
    return display_events
=======
def fetch_data(location, start_date, end_date):
    location = location + "/"
    scheduler_file = open (location+"optistudy_calendar.ics",'rb')
    calendar = Calendar.from_ical(scheduler_file.read())
    events = recurring_ical_events.of(calendar).between(start_date, end_date)
    counter=1
    events_list=[]
    for event in events:
        dict = {}
        dict['id'] = counter
        counter=counter+1
        dict['title'] = event["SUMMARY"]
        dict['url'] = ""
        if ('assignment' in event['uid']):
            dict['class'] = 'assignment'
        else:
            dict['class'] = 'lecture'
        if ('assignment' in event['uid']):
            dict['start'] = event["DTSTART"].dt.replace(tzinfo=timezone.utc).timestamp()*1000
            dict['end'] = (event["DTEND"].dt.replace(tzinfo=timezone.utc)+timedelta (minutes=30)).timestamp()*1000
        else:
            dict['start'] = (event["DTSTART"].dt.replace(tzinfo=timezone.utc)+timedelta (hours=4)).timestamp()*1000
            dict['end'] = (event["DTEND"].dt.replace(tzinfo=timezone.utc)+timedelta (hours=4)).timestamp()*1000
        events_list.append (dict)
    print (events_list)
    return events_list
>>>>>>> 44f6bcff438cafdf51be3670a7d825b8092517d1
