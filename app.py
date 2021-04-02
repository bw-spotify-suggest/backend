from flask import Flask, render_template, request, Response
import pandas as pd
from predictor import suggest, load_clean_data
import json
import base64
from io import BytesIO
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# from flask_sqlalchemy import SQLAlchemy
APP = Flask(__name__)



APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'


# DB = SQLAlchemy(APP)


@APP.route("/")
def root():
    return render_template("base.html")


@APP.route("/get_song", methods=["POST"])
def get_song():
    data = pd.read_csv("Data/spotify2021.csv")
    song_name = request.values['song_request']
    found_song = data[(data["name"] == song_name)]
    array = []
    max_yr_song = found_song[found_song['year'] == found_song['year'].max()]

    track_id = max_yr_song['id'].iloc[0]
    suggest_list, graph_data = suggest(track_id, 5)
    suggest_list = json.loads(suggest_list)
    for x in suggest_list:
        array.append((x['artists'], x['id'], x['name'].split('feat')[0],data['year'][x['id'] == data['id']].values[0]))
    names, energy, speech, dance = vis(graph_data)
    our_json = json.dumps(graph_data.to_dict())
    return render_template("get_song.html", song_request=song_name, names_list=names, energy_list=energy, speech_list=speech, dance_list=dance, table_contents=array, our_json=our_json)


def vis(graph_data):

    # data for the plot
    names_list = []
    speechiness_list = []
    danceability_list = []
    energy_list = []
    for i, x in graph_data.iterrows():
        names_list.append(x['name'].split('feat')[0])
        energy_list.append(x['energy'])
        speechiness_list.append(x['speechiness'])
        danceability_list.append(x['danceability'])
    return names_list, energy_list, speechiness_list, danceability_list


# print(suggest("6Wosx2euFPMT14UXiWudMy",3))
if __name__ == '__main__':
    APP.run()
