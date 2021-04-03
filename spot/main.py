"""Main routing for Spotify App"""
from io import BytesIO
from predict import load_clean_data, suggest
from flask import Flask, render_template, request, Response, redirect, url_for
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
import base64
import json

@APP.route("/")
def root():
    return render_template("base.html")


@APP.route("/get_song", methods=["POST"])
def get_song():
    array = []
    data = pd.read_csv("spot/Data/spotify2021.csv")
    song_id = request.values['song_request']

    suggest_list, graph_data = suggest(song_id, 5)
    suggest_list = json.loads(suggest_list)

    for x in suggest_list:
        array.append((x['artists'], x['id'], x['name'].split('feat')[0],data['year'][x['id'] == data['id']].values[0]))

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

    names, energy, speech, dance = vis(graph_data)
    our_json = json.dumps(graph_data.to_dict())

    return render_template("get_song.html", song_request=song_id,
                                            names_list=names, energy_list=energy, speech_list=speech, dance_list=dance, table_contents=array, our_json=our_json)
