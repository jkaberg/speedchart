import dateutil.parser
import datetime

from pygal import Bar as pygal_bar
from csv import reader as csv_reader
from os import environ
from gevent.pywsgi import WSGIServer
from flask import Flask, render_template

app = Flask(__name__)

def readCsv(f_path):
    speedstats = []  
    with open(f_path) as csvfile:
        speedreader = csv_reader(csvfile)
        for row in speedreader:
            server = row[1]
            location = row[2]
            timestamp = row[3]
            distance = row[4]
            ping = row[5]
            downspeed = float(row[6])/1000000
            upspeed = float(row[7])/1000000
     
            speedstats.append(dict(server=server, location=location, timestamp=timestamp, distance=distance, ping=ping, downspeed=downspeed, upspeed=upspeed))
        return speedstats

def createChart(speedstats):
    speedchart = pygal_bar(y_title='Mbps', truncate_legend=-1)
    speedchart.x_labels = 'Up', 'Down'
    
    # Add bars
    average_down = float()
    average_up = float()
    for s in speedstats:
      average_down = average_down + s['downspeed']
      average_up = average_up + s['upspeed']
      speedchart.add(s['server'] + ' (' + s['location'] + ')', [s['downspeed'], s['upspeed']])
     
    # Calculate and add average
    average_down = average_down / len(speedstats)
    average_up = average_up / len(speedstats)
    speedchart.add('Average', [average_down, average_up])
     
    # Convert UTC to more readble local time and set title
    utc = speedstats[0]['timestamp']
    utc = dateutil.parser.parse(utc)
    from_zone = dateutil.tz.tzutc()
    to_zone = dateutil.tz.tzlocal()
    utc = utc.replace(tzinfo=from_zone)
    localtime = utc.astimezone(to_zone)
    title = localtime.strftime("%Y-%m-%d %H:%M:%S %Z")
    speedchart.config(title=title)
     
    # Render and save to png
    return speedchart.render_data_uri()

@app.route('/')
def index():
    chart = createChart(readCsv(environ['CSV_PATH']))
    return render_template('chart.html', chart=chart)

if __name__ == '__main__':
    http = WSGIServer(('0.0.0.0', 8080), app.wsgi_app)
    http.serve_forever()
