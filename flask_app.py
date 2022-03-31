from flask import Flask, render_template, send_from_directory, jsonify, current_app
from calendar_merge import *
from datetime import datetime

app = Flask(__name__, template_folder="templates")

@app.route("/", methods=['GET'])
def main():
    return render_template('index.html')

@app.route("/submit", methods=['GET', 'POST'])
def show_calendar():
    cwd = os.getcwd()
    location = os.path.join(cwd, "Experiments/", datetime.now().strftime("%m.%d.%Y,%H.%M.%S"))
    os.mkdir (location)
    app.config['UPLOAD_FOLDER'] = location
    file = request.files['file']
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'scheduler.ics'))
    start_date, end_date = get_dates()
    app.config['START_DATE'] = start_date
    app.config['END_DATE'] = end_date
    create_calendar(location, current_app.config["START_DATE"], current_app.config["END_DATE"])
    return render_template ("calendar.html")

@app.route("/view", methods=['GET'])
def calendar_load():
    return render_template('calendar_events.html')

@app.route('/calendar-events', methods=['GET'])
def calendar_events():
    # cwd = os.getcwd()
    # location = os.path.join(cwd, "Experiments/", datetime.now().strftime("%m.%d.%Y,%H.%M.%S"))
    rows = fetch_data(current_app.config["UPLOAD_FOLDER"], current_app.config["START_DATE"], current_app.config["END_DATE"])
    resp = jsonify({'success' : 1, 'result' : rows})
    resp.status_code = 200
    print (resp)
    return resp

@app.route("/download", methods=['GET'])
def download_file():
    return send_from_directory(app.config["UPLOAD_FOLDER"], 'optistudy_calendar.ics', )

def get_dates ():
    #Set date markers
    start_date=str(request.form['startDate'])
    start_date=datetime.strptime(start_date,"%d/%m/%Y").date()
    start_date=datetime.combine(start_date,datetime.min.time()) 
    end_date=str(request.form['endDate']) 
    end_date=datetime.strptime(end_date,"%d/%m/%Y").date() 
    end_date=datetime.combine(end_date,datetime.max.time())
    return start_date, end_date

if __name__ == "__main__":
	# setDefaultEncoding ()
	app.run(host= '0.0.0.0', port = 5001, debug = True)

