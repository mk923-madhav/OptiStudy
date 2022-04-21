from asyncio import events
from flask import Flask, render_template, send_from_directory
from calendar_merge import *
from datetime import datetime

app = Flask(__name__, template_folder="templates")

@app.route("/", methods=['GET'])
def main():
    return render_template('index.html')

@app.route("/calendar", methods=['GET', 'POST'])
def show_calendar():
    cwd = os.getcwd()
    location = os.path.join(cwd, "Experiments/", datetime.now().strftime("%m.%d.%Y,%H.%M.%S"))
    os.mkdir (location)
    app.config['UPLOAD_FOLDER'] = location
    file = request.files['file']
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'scheduler.ics'))
    events = create_calendar(location)
    return render_template ("calendar1.html", events=events)

@app.route("/download", methods=['GET'])
def download_file():
    return send_from_directory(app.config["UPLOAD_FOLDER"], 'optistudy_calendar.ics', )

# @app.route("/calendar", methods=['GET', 'POST'])
# def calendar():

#     return render_template('calendar1.html', events=events)

if __name__ == "__main__":
	# setDefaultEncoding ()
	app.run(host= '0.0.0.0', port = 5001, debug = True)

