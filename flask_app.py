from flask import Flask, render_template
from calendar_merge import *

app = Flask(__name__)

@app.route("/", methods=['GET'])
def main():
    return render_template('index.html')

@app.route("/submit", methods=['GET', 'POST'])
def show_calendar():
    create_calendar()
    return render_template ("calendar.html")

if __name__ == "__main__":
	# setDefaultEncoding ()
	app.run(host= '0.0.0.0', port = 5001, debug = True)