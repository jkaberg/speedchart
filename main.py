 # -*- coding: utf-8 -*-

from pygal import Line as pygal_line
from csv import reader as csv_reader
from os import environ
from gevent.pywsgi import WSGIServer
from flask import Flask, render_template

app = Flask(__name__)

def readCsv(f_path):
    speedstats = []  
    with open(f_path, 'rt', encoding='utf-8') as csvfile:
        speedreader = csv_reader(csvfile)
        for row in speedreader:
            speedstats.append(dict(server=row[1], 
                                   location=row[2], 
                                   timestamp=row[3], 
                                   distance=row[4], 
                                   ping=row[5], 
                                   downspeed=float(row[6])/1000000, 
                                   upspeed=float(row[7])/1000000))
        return speedstats

def createChart(stats):
    chart = pygal_line(y_title='Mbps', x_title='Time', legend_at_bottom=True, dots_size=1)
    
    time = []
    speeds = {}
    avg_down = float()
    avg_up = float()

    for s in stats:
        avg_down += s['downspeed']
        avg_up += s['upspeed']
#        time.append(s['timestamp'])

        if s['server'] in speeds.keys():
            speeds[s['server']]['down'].append(s['downspeed'])
            speeds[s['server']]['up'].append(s['upspeed'])                    
        else:
            speeds[s['server']] = {'up': [s['upspeed']], 'down': [s['downspeed']]}

    # Add servers and plot speeds
    for server, speed in speeds.items():
        chart.add('{} (Download)'.format(server), speed['down'])
        chart.add('{} (Upload)'.format(server), speed['up'], secondary=True)
    
    # Add avarage speeds
    avg_down = avg_down / len(stats)
    avg_up = avg_up / len(stats)
    chart.add('Avarage (Download)', [avg_down])
    chart.add('Avarage (Upload)', [avg_up], secondary=True)
#    chart.x_labels = time

    # Render
    return chart.render_data_uri()

@app.route('/')
def index():
    chart = createChart(readCsv(environ['CSV_PATH']))
    return render_template('chart.html', chart=chart)

if __name__ == '__main__':
    http = WSGIServer(('0.0.0.0', 8080), app.wsgi_app)
    http.serve_forever()

    #createChart(readCsv(environ['CSV_PATH']))
