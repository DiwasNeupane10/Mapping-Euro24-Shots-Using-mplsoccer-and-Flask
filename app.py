from flask import Flask,render_template,request,jsonify
import pandas as pd
import json
import matplotlib
from datetime import datetime
import os
import glob
matplotlib.use('Agg')
from mplsoccer import VerticalPitch

app=Flask(__name__)

@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        team=request.form.get('country')
        player=request.form.get('player')
        data=load()
        data['location']=data['location'].apply(json.loads)#convert the location data from string to list
        df=filter_df(data,team,player)
        pitch=VerticalPitch(pitch_type='statsbomb',half=True ,pitch_color='grass', line_color='white', stripe=True)
        fig,ax=pitch.draw(figsize=(10,10))
        timestamp=datetime.now().strftime('%Y%m%d%H%M%S')
        filename=f'plot_{timestamp}.png'
        path=os.path.join('./static/images',filename)
        for file in glob.glob(os.path.join('./static/images', 'plot_*.png')):
            os.remove(file)
        create_pitch(df,ax,pitch,path)
        return jsonify({'path': path})
    if request.method=='GET':
        data=load()
        countries=data['team'].sort_values().unique()
        return render_template('index.html',countries=countries)
    
@app.route('/get_players', methods=['GET'])
def get_players():
    selected_team = request.args.get('team')
    if selected_team:
        data=load()
        players = data[data['team'] == selected_team]['player'].sort_values().unique().tolist()
        return jsonify(players)
    else:
        # If accessed directly without a team parameter, return a meaningful message
        return jsonify({"error": "Please select a team first"}), 400



def filter_df(df,team,player):
    if team:
        df=df[df['team']==team]
    if player:
        df=df[df['player']==player]
    return df

def load():
    data = pd.read_csv('./euros_2024_shot_map.csv')
    data = data[data['type'] == 'Shot'].reset_index(drop=True)
    return data


def create_pitch(df,ax,pitch,path):
    for x in df.to_dict(orient='records'):
        pitch.scatter(
            x=float(x['location'][0]),
            y=float(x['location'][1]),
            ax=ax,
            s=1000*x['shot_statsbomb_xg'],
            color='green' if x['shot_outcome']=='Goal' else 'white',
            edgecolor='black',
            alpha=1 if x['type']=='goal' else 0.5,
            zorder=2 if x['type']=='goal' else 1
        )
    if path:
        fig = ax.figure  # Retrieve the figure from the axes object
        fig.savefig(path, dpi=300, bbox_inches='tight')

if __name__=='__main__':
    app.run(debug=True)