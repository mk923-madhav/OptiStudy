from asyncio import events
from flask import Flask, render_template, send_from_directory, current_app
from calendar_merge import *
from datetime import datetime
import os

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_COOKIE_NAME'] = "my_session"

@app.route("/", methods=['GET'])
def main():
    return render_template('index.html')

@app.route("/preferences", methods=['GET', 'POST'])
def check_preferences():
    return render_template('preferences.html')

@app.route("/basic_calendar", methods=['GET', 'POST'])
def show_calendar():
    cwd = os.getcwd()
    location = os.path.join(cwd, "Experiments/", datetime.now().strftime("%m.%d.%Y,%H.%M.%S"))
    os.mkdir (location)
    session['folderLocation'] = location
    file = request.files['file']
    file.save(os.path.join(session['folderLocation'], 'scheduler.ics'))
    events = create_calendar(location)
    return render_template ("basic_calendar.html", events=events)

@app.route("/calendar", methods=['GET', 'POST'])
def show_advanced_calendar():
    events = populate_events(session['folderLocation'])
    return render_template ("advanced_calendar.html", events=events)

@app.route("/download", methods=['GET'])
def download_file():
    return send_from_directory(app.config["UPLOAD_FOLDER"], 'optistudy_calendar.ics', )

if __name__ == "__main__":
	# setDefaultEncoding ()
	app.run(host= '0.0.0.0', port = 5001, debug = True)

