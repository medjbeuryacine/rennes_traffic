import plotly.express as px
import numpy as np
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()
logger = logging.getLogger(__name__)

def send_alert(message):
    try:
        msg = MIMEMultipart()
        msg['From'] = os.getenv('MAIL_FROM')
        msg['To'] = os.getenv('MAIL_TO')
        msg['Subject'] = 'ALERTE - Erreur application trafic Rennes'
        msg.attach(MIMEText(message, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587, timeout=5) as server:  # timeout=5s
            server.starttls()
            server.login(os.getenv('MAIL_FROM'), os.getenv('MAIL_PASSWORD'))
            server.sendmail(os.getenv('MAIL_FROM'), os.getenv('MAIL_TO'), msg.as_string())

    except Exception as e:
        logger.error(f"Erreur envoi alerte email : {e}")

def create_figure(data):
    try :
        fig_map = px.scatter_mapbox(
                data,
                title="Traffic en temps réel",
                color="traffic",
                lat="lat",
                lon="lon",
                color_discrete_map={'freeFlow':'green', 'heavy':'orange', 'congested':'red'},
                zoom=10,
                height=500,
                mapbox_style="carto-positron"
        )

        return fig_map
    except Exception as e:
        logger.error(f"Erreur create_figure : {e}")
        raise
    
def prediction_from_model(model, hour_to_predict):
    try:
        input_pred = np.array([0]*24)
        input_pred[int(hour_to_predict)] = 1

        cat_predict = np.argmax(model.predict(np.array([input_pred])))

        return cat_predict
    except Exception as e:
        logger.error(f"Erreur prediction_from_model : {e}")
        raise

