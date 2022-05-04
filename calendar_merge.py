from collections import Counter
from pydoc import locate
from icalendar import Calendar, Event
import datetime as dt
from datetime import datetime, timedelta, timezone
import csv
import urllib.request
import recurring_ical_events
import pandas as pd
from flask import Flask, render_template, request, json, session, redirect, url_for
import os
import re
import math
import random

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

    display_events = populate_events(location+"/schedule.csv")
    return display_events

def to_dt(date_string):
    return datetime.fromisoformat(date_string)

def to_day(date_string):
    return datetime.fromisoformat(date_string).isoweekday()

def to_time(date_string):
    return datetime.fromisoformat(date_string).isoweekday()

def make_recommendations (location):
    location = location+"/schedule.csv"
    df = pd.read_csv(location)
    assignments = df[df.Type == 'To-do']
    classes = df[df.Type == 'Class']  
    classes['hours'] = classes['Duration'].str.split(':', expand = True)[0].astype(int)
    classes['mins'] = classes['Duration'].str.split(':', expand = True)[1].astype(int)
    classes['Duration_Mins'] = classes['hours'] * 60 + classes['mins']
    classes = classes.drop(columns = ['Duration', 'hours', 'mins'])  
    print('Total time in class (mins)', classes.Duration_Mins.sum())
    class_assign = assignments.Summary.str.split('[', expand = True)
    class_assign = class_assign.rename(columns = {0: 'Assignment', 1: 'Class'})
    class_assign = class_assign.groupby('Class').count()
    class_assign_dict = class_assign.to_dict()['Assignment']
    # Time spent studying per week 
    time_per_week = 40
    # Number of tests
    test_per_class = {i : 1 for i in list(classes.Summary.unique())}
    # Class difficulty
    class_diff = {i : 1 for i in list(classes.Summary.unique())}
    class_dur_ass = classes.groupby('Summary').sum('Duration_Mins')
    class_dur_ass['Number_Tests'] = pd.Series(test_per_class)
    class_dur_ass['Class_Diff'] = pd.Series(class_diff)
    formatted_class_assign_dict = {x:0 for x in list(class_dur_ass.index)}
    for i in class_assign_dict.keys():
        if i == 'TECH5910]':
            formatted_class_assign_dict['TECH 5910 Studio'] = class_assign_dict[i]
        else:
            j = i.replace(']', '')
            res = re.sub("[A-Za-z]+", lambda ele: " " + ele[0] + " ", j)[1:]
            formatted_class_assign_dict[res + ' Lecture'] = class_assign_dict[i]
    class_dur_ass['Number_Assignments'] = pd.Series(formatted_class_assign_dict)
    class_dur_ass['Numerator'] = class_dur_ass.Class_Diff * (class_dur_ass.Number_Assignments + class_dur_ass.Number_Tests)
    class_dur_ass['Fraction'] = class_dur_ass['Numerator']/class_dur_ass['Numerator'].sum()
    class_dur_ass['Time Per Week'] = round((time_per_week - sum(class_dur_ass.Duration_Mins)/60) * class_dur_ass['Fraction'])

    classes['Day of Week'] = classes['Start'].map(to_day)
    classes['Start'] = classes['Start'].map(to_dt)
    classes['End'] = classes['End'].map(to_dt)
    classes.sort_values(by = ['Day of Week', 'Start'])
    free_time_per_week = class_dur_ass['Time Per Week']
    
    def shift_calculator(dayofweek):
  
        if dayofweek not in list(classes['Day of Week'].unique()):
            shift_dict = {}
  
        temp = classes[classes['Day of Week'] == dayofweek]

        iter = len(temp)*3

        # Sort by the start 
        temp = temp.sort_values(by = 'Start').reset_index(drop = True)

        # Check if there is a class at 8 AM, if not then start the schedule then
        if temp.Start[0] != dt.datetime.combine(temp.End.iloc[0], dt.time(8, 00)):
            morning = dt.datetime.combine(temp.End.iloc[0], dt.time(8, 00))
            temp = temp.append({'Summary': '0', 'Type': '0', 'Start': morning, 'End': morning, 'Duration_Mins': 0, 'Day of Week': dayofweek}, ignore_index = True)

        # Adding a schedule end time
        evening = dt.datetime.combine(temp.End.iloc[0], dt.time(22, 00))

        # Adding in start and end times 
        temp = temp.append({'Summary': '0', 'Type': '0', 'Start': evening, 'End': evening, 'Duration_Mins': 0, 'Day of Week': dayofweek}, ignore_index = True)

        # Sorting 
        temp = temp.sort_values(by = 'Start').reset_index(drop = True)

        # Computing the open shifts throughout the day
        shift_dict = {}
        for i in range(0,iter):
            a = temp[temp.index == i].End.reset_index(drop = True)
            b = temp[temp.index == i + 1].Start.reset_index(drop = True)
            #print(a, b)
            delta = list(b - a)
            for j in delta:
                mins = round(j.total_seconds()/60)
            if mins >= 45:
                for l in range(math.floor(mins/55)):
                    shift_dict['shift' + str(i + l)] = {'Start': (a + timedelta(minutes = (55*l))).values[0], 'End': (a + timedelta(minutes = 45 + (55*l))).values[0]}
                    # Updating the temp df
                    temp = temp.append({'Summary': '0', 'Type': '0', 'Start': (a + timedelta(minutes = 5 + (55*l))).values[0], 'End': (a + timedelta(minutes = 50 + (55*l))).values[0], 'Duration_Mins': 0, 'Day of Week': dayofweek}, ignore_index = True)
                    # Sorting 
                    temp = temp.sort_values(by = 'Start').reset_index(drop = True)

        return shift_dict

    #Putting into a dictionary for all days of week
    master_shifts = {}
    for i in list(classes['Day of Week'].unique()):
        master_shifts[str(i)] = shift_calculator(i)

    for c in list(free_time_per_week.index):
        for h in range(int(free_time_per_week[c])):
            # Stop assinging when there are no empty shifts left
            if master_shifts == {}:
                break
            else:
                # Pick a random day
                day = random.choice(list(master_shifts.keys()))

                # Picking random shift on that day
                shift = random.choice(list(master_shifts[day].keys()))

                # Getting the time in that block
                block = master_shifts[day][shift]
                
                # Delete that shift from the dictionary so it can't be picked again
                master_shifts[day].pop(shift)

                if master_shifts[day] == {}:
                    master_shifts.pop(day)

                # Appending to the classes df
                classes = classes.append({'Summary': 'Study for ' + c, 'Type': 'Block', 'Start': block['Start'], 'End': block['End'], 'Duration_Mins': 45, 'Day of Week': day}, ignore_index = True)

    results = classes.sort_values(by = 'Start').reset_index(drop = True)

    blocks = results[results.Type == 'Block']
    blocks = blocks.reset_index()

    rows = []
    with open(location, 'r') as readFile:
        reader = csv.reader(readFile)
        for row in reader:
            if row[1] != "Block":
                rows.append(row)
    with open(location, 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(rows)

    with open(location, 'a', newline='') as csvfile:
        schedulewriter = csv.writer(csvfile, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
        for index, row in blocks.iterrows():
            schedulewriter.writerow([row['Summary'], row ['Type'], row['Start'], row['End'], row ['Duration_Mins']])
        
    
    display_events = populate_events(location)
    return display_events

def populate_events (location):
    events = []

    with open(location, newline='') as csvfile:
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
            elif (row[1]) == "Block" :
                event = {
                    'todo' : row[0],
                    'start' : row[2],
                    'end' : row[3],
                    'color' : '#69d667',
                    'editable' : 'false'
                }
                events.append (event)
    return events