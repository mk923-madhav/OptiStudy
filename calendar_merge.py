from collections import Counter
from pydoc import locate
from icalendar import Calendar, Event
from datetime import datetime, timedelta, timezone
import csv
import urllib.request
import recurring_ical_events
from flask import Flask, render_template, request, json, session, redirect, url_for
import os

def create_calendar(location):
     #Set date markers
    start_date=str(request.form['startDate'])
    start_date=datetime.strptime(start_date,"%Y-%m-%d").date()
    start_date=datetime.combine(start_date,datetime.min.time()) 
    end_date=str(request.form['endDate']) 
    end_date=datetime.strptime(end_date,"%Y-%m-%d").date() 
    end_date=datetime.combine(end_date,datetime.max.time())

    #Initializing master calendar
    cal = Calendar()
    display_events = []

    #Canvas file
    target_url = str(request.form['canvasURL'])
    print (target_url)
    canvas_file = urllib.request.urlopen(target_url)
    calendar = Calendar.from_ical(canvas_file.read())
    with open(location+"/schedule.csv", 'w', newline='') as csvfile:
        schedulewriter = csv.writer(csvfile, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
        schedulewriter.writerow(["Summary", "Type", "Start", "End", "Duration"])
        events = recurring_ical_events.of(calendar).between(start_date, end_date)
        for event in events:
            if ('assignment' in event['uid']):
                cal.add_component(event)
                schedulewriter.writerow([event["SUMMARY"].replace (",",""), "To-do", (event["DTSTART"].dt-timedelta (hours=4)).replace(tzinfo=None), (event["DTEND"].dt-timedelta (hours=4)).replace(tzinfo=None)])
    canvas_file.close()

    #Scheduler file
    scheduler_file = open (location+"/scheduler.ics",'rb')
    calendar = Calendar.from_ical(scheduler_file.read())
    with open(location+"/schedule.csv", 'a', newline='') as csvfile:
        schedulewriter = csv.writer(csvfile, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
        events = recurring_ical_events.of(calendar).between(start_date, end_date)
        for event in events:
            cal.add_component(event)
            schedulewriter.writerow([event["SUMMARY"].replace (",",""), "Class", event["DTSTART"].dt, event["DTEND"].dt, event["DTEND"].dt - event["DTSTART"].dt])
    scheduler_file.close()

    f = open(location+'/optistudy_calendar.ics', 'wb')
    f.write(cal.to_ical())
    f.close()

    display_events = populate_events(location)
    return display_events

def populate_events (location):
    events = []
    with open(location+"/schedule.csv", newline='') as csvfile:
        schedule_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in schedule_reader:
            if (row[1]) == "To-do" :
                event = {
                    'todo' : row[0],
                    'start' : row[2],
                    'end' : row[3],
                    'color' : '#F8E9E8',
                    'editable' : 'false'
                }
                events.append (event)
            elif (row[1]) == "Class" :
                event = {
                    'todo' : row[0],
                    'start' : row[2],
                    'end' : row[3],
                    'color' : '#E9F6FC',
                    'editable' : 'false'
                }
                events.append (event)
            
    return events