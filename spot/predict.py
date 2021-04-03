"""Song Suggestions model"""
import pandas as pd
import numpy as np
import pickle
import re


def load_clean_data():
    """
    Loads data and performs basic cleaning / feature engineering.
    Returns one raw DataFrame, and one cleaned DataFrame.
    
    Example
    -------
    > raw, clean = load_clean_data()
    > type(raw), raw.shape, type(clean), df.clean
      (pandas.core.frame.DataFrame,
      (130326, 17),
      pandas.core.frame.DataFrame,
      (130326, 15))
    """
    def clean_text(doc):
        multi_ws = '[ ]{2,}'
        non_alpha = '[^a-zA-Z]'
        empty_start = '^ '
        empty_end = ' $'

        doc = re.sub(non_alpha, ' ', doc)
        doc = re.sub(multi_ws, ' ', doc)
        doc = re.sub(empty_start, '', doc)
        doc = re.sub(empty_end, '', doc)

        return doc
    
    def is_live(n):
        return (1 if n > 0.75 else 0)

    def round_10(n):
        a = (n // 10) * 10
        b = a + 10

        return (b if n - a > b - n else a)

    data = pd.read_csv("spot/Data/spotify2021.csv")
    data['artists'] = data['artists'].apply(clean_text)
    data['name'] = data['name'].apply(clean_text)

    df = data.drop(columns=['artists', 'name', 'year',
                            'release_date','duration_ms', 
                            'popularity'])

    df = df[~df.id.duplicated(keep='first')]

    to_bins = ['acousticness', 'danceability', 'energy', 
               'instrumentalness', 'valence']

    for col in to_bins:
        df[col] = round(df[col] * 4)

    df['tempo'] = df['tempo'].apply(round_10)
    df['liveness'] = df['liveness'].apply(is_live)
    df['speechiness'] = round(df['speechiness'] * 10 / 3)
    df['loudness'] = round(df['loudness'])

    return data, df

def suggest(song_id=None, n_suggestions=1, output_format='records'):
    """
    Suggests Spotify song(s) given one song id.
    
    Parameters
    ----------
    song_id: str
        Song id from which to base suggestions
    
    n_suggestions: int {1, 3, 5, 10, 15, 20}, default 1
        Number of songs to suggest

    output_format: str, default 'records'
        Output format of the JSON string:
            ‘split’ : dict like {‘index’ -> [index], ‘columns’ -> [columns], ‘data’ -> [values]}
            ‘records’ : list like [{column -> value}, … , {column -> value}]
            ‘index’ : dict like {index -> {column -> value}}
            ‘columns’ : dict like {column -> {index -> value}}
            ‘values’ : just the values array
            ‘table’ : dict like {‘schema’: {schema}, ‘data’: {data}}
        Note: Directly passed to pandas.DataFrame.to_json(orient=output_format) 
    
    Example
    -------
    > example = df[df.track_id == '6Wosx2euFPMT14UXiWudMy']
    > example.artists
      R3HAB
    > example.name
      Radio Silence
    > suggestion = suggest('3ajZwXiT7qpanVm5DcvcQF', 3)
    > suggestion
             artists	      id                        name
       9117	 Joni Mitchell	  00xemFYjQNRpOlPhVaLAHa	Urge For Going Live...
      42142	 Carmen Miranda	  2heQBczLrbtAgOtkDk831k	Samba Rasgado
      47980	 Amalia Mendoza	  4QJsxMItrRbvn05gGuf0CZ	chame a M la Culpa

    """
    data, df = load_clean_data()
    song = df[df.id == song_id].drop(columns='id').values

    filename = f'spot/model/model_{n_suggestions}_suggestions.sav'
    loaded_model = pickle.load(open(filename, 'rb'))

    output = data.iloc[loaded_model.kneighbors(song)[1][0][1:]]

    drop_cols = ['acousticness', 'danceability', 'duration_ms', 'energy',
                 'explicit', 'instrumentalness', 'key', 'liveness', 'loudness',
                 'mode', 'popularity', 'release_date', 'speechiness', 'tempo',
                 'valence', 'year']
    
    suggestion = output.drop(columns = drop_cols)

    return suggestion