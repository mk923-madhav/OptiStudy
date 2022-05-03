from asyncio import events
from re import S
from flask import Flask, render_template, send_from_directory
from calendar_merge import *
import os
import shutil

app = Flask(__name__, template_folder="templates")

@app.route("/", methods=['GET'])
def main():
    return render_template('index.html')

@app.route("/preferences", methods=['GET', 'POST'])
def check_preferences():
    folder_name = request.args.get('id', None)
    return render_template('preferences.html', folder_name=folder_name)

@app.route("/basic_calendar", methods=['GET', 'POST'])
def show_calendar():
    canvasURL = str(request.form['canvasURL'])
    folder_name = canvasURL[canvasURL.rfind('/')+1:-4]
    cwd = os.getcwd()
    location = os.path.join(cwd, "Experiments/", folder_name)
    if os.path.exists(location):
        shutil.rmtree (location)
    os.mkdir (location)
    file = request.files['file']
    file.save(os.path.join(location, 'scheduler.ics'))
    events = create_calendar(location)
    return render_template ("basic_calendar.html", events=events, folder_name=folder_name)

@app.route("/calendar", methods=['GET', 'POST'])
def show_advanced_calendar():
    cwd = os.getcwd()
    folder_name = request.args.get('id', None)
    print (folder_name)
    location = os.path.join(cwd, "Experiments/", folder_name)
    events = make_recommendations (location)
    print (events)
    return render_template ("advanced_calendar.html", events=events)

@app.route("/download", methods=['GET'])
def download_file():
    return send_from_directory(app.config["UPLOAD_FOLDER"], 'optistudy_calendar.ics', )

if __name__ == "__main__":
	# setDefaultEncoding ()
	app.run(host= '0.0.0.0', port = 5001, debug = True)

