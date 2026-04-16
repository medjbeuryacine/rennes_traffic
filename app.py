from flask import Flask, render_template, request
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import flask_monitoringdashboard as dashboard
from keras.models import load_model
from src.get_data import GetData
from src.utils import create_figure, prediction_from_model, send_alert
import logging
from logging.handlers import SMTPHandler
from dotenv import load_dotenv
import os
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

app = Flask(__name__)

# Setup logging - uniquement les erreurs avec horodatage
logging.basicConfig(
    filename='logs/app.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Alerte
mail_handler = SMTPHandler(
    mailhost=('smtp.gmail.com', 587),
    fromaddr=os.getenv('MAIL_FROM'),
    toaddrs=[os.getenv('MAIL_TO')],
    subject='ALERTE - Erreur application trafic Rennes',
    credentials=(os.getenv('MAIL_FROM'), os.getenv('MAIL_PASSWORD')),
    secure=()
)
mail_handler.setLevel(logging.ERROR)
app.logger.addHandler(mail_handler)

data_retriever = GetData(url="https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/exports/json?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B&")
data = data_retriever()

model = load_model('model.h5') 

def update_data():
    global data
    try:
        data = data_retriever()
        logger.info("Données mises à jour")
    except Exception as e:
        logger.error(f"Erreur mise à jour données : {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(update_data, 'interval', minutes=30)
scheduler.start()

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':

            fig_map = create_figure(data) # récupèrer la data
            graph_json = fig_map.to_json() # mettre en json

            selected_hour = request.form['hour'] # récupèrer l'heur selection depuis index.html

            cat_predict = prediction_from_model(model, selected_hour) # prediction de model

            color_pred_map = {0:["Prédiction : Libre", "green"], 1:["Prédiction : Dense", "orange"], 2:["Prédiction : Bloqué", "red"]} # les labels

            return render_template('index.html', graph_json=graph_json, text_pred=color_pred_map[cat_predict][0], color_pred=color_pred_map[cat_predict][1]) # returne dans le site 

        else:

            fig_map = create_figure(data)
            graph_json = fig_map.to_json()

            return render_template('index.html', graph_json=graph_json)
    except Exception as e:
        logger.error(f"Erreur route / : {e}")
        send_alert(f"Erreur route / : {e}")
        return "Erreur interne", 500

dashboard.config.init_from(file='config.cfg')
dashboard.bind(app)

if __name__ == '__main__':    
    app.run(debug=True, use_reloader=False)
