from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Optional, List
import joblib
import uvicorn
from loguru import logger

# Définition de la classe pour le corps de la requête
class DonneesEntree(BaseModel):
    step: int
    start_date: str  # Date de début de l'intervalle au format YYYY-MM-DD HH:MM:SS
    end_date: str    # Date de fin de l'intervalle au format YYYY-MM-DD HH:MM:SS

# Charger le modèle ARIMA (s'il est utilisé)
modele = joblib.load('Modele/model_arima')

# Créer une instance de l'application FastAPI
app = FastAPI()

chemin_fichier_log = "./Data_db/logs.log"
logger.add(chemin_fichier_log, rotation="500 MB", retention="10 days", level="INFO")

# Fonction pour enregistrer les prédictions dans un DataFrame
def enregistrer_prediction_dataframe(dates, predictions):
    df = pd.DataFrame({'date': dates, 'predictions': predictions})
    return df

# Fonction pour enregistrer les prédictions dans la base de données SQLite
def enregistrer_prediction_sqlite(df, chemin='data'):

    try:
        conn = sqlite3.connect(chemin)
        df.to_sql('predictions', conn, if_exists='append', index=False)
        conn.close()
        print("Prédictions enregistrées avec succès dans la base de données.")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement des prédictions : {str(e)}")


@app.get("/")
def root():
    logger.info("Endpoint racine appelé")
    return {"message": "Bienvenue"}

# Définir le point de terminaison pour les prédictions
@app.post("/predict")
async def predict(data: DonneesEntree):
    try:
        logger.info(f"Prédictions demandées pour les dates {data.start_date} à {data.end_date}")
        # Convertir les dates en format datetime
        start_date = datetime.strptime(data.start_date, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(data.end_date, "%Y-%m-%d %H:%M:%S")

        # Liste pour stocker les dates et les prédictions
        dates = []
        predictions = []

        # Boucle pour calculer les prédictions pour chaque intervalle de 3 heures
        current_date = start_date
        while current_date <= end_date:
            # Faire la prédiction pour l'intervalle actuel
            prediction = modele.predict(start=current_date, end=current_date, dynamic=False)  # Sans prédiction dynamique

            # Ajouter la date et la prédiction aux listes
            dates.append(current_date)
            predictions.append(prediction[0])  # Prendre le premier élément de la prédiction

            # Passer à l'intervalle de 3 heures suivant
            current_date += pd.Timedelta(hours=3)  # Utiliser Pandas Timedelta pour ajouter 3 heures
        logger.info("Prédictions effectuées avec succès")
        # Enregistrer les prédictions dans un DataFrame
        df_predictions = enregistrer_prediction_dataframe(dates, predictions)
        chemin_base_de_donnees = 'data/predictions.db'
        # Enregistrer les prédictions dans la base de données SQLite
        enregistrer_prediction_sqlite(df_predictions, chemin_base_de_donnees)

        return {"predictions": df_predictions.to_dict(orient='records')}  # Convertir le DataFrame en format JSON

    except Exception as e:
        logger.error(f"Erreur lors des prédictions : {str(e)}")
        return {"error": str(e)}

@app.get("/predictions")
async def get_predictions(start_date: Optional[str] = Query(None, description="Date de début au format YYYY-MM-DD"),
                          end_date: Optional[str] = Query(None, description="Date de fin au format YYYY-MM-DD")):
    try:
        logger.info("Début de la récupération des prédictions depuis la base de données")

        # Construction de la requête SQL en fonction des paramètres
        conn = sqlite3.connect('data/predictions.db')
        if start_date and end_date:
            query = f"SELECT * FROM predictions WHERE date BETWEEN '{start_date}' AND '{end_date}'"
        elif start_date:
            query = f"SELECT * FROM predictions WHERE date >= '{start_date}'"
        elif end_date:
            query = f"SELECT * FROM predictions WHERE date <= '{end_date}'"
        else:
            query = "SELECT * FROM predictions"

        # Exécution de la requête SQL
        df_predictions = pd.read_sql_query(query, conn)
        conn.close()

        predictions_list = df_predictions.to_dict(orient='records')
        logger.info("Prédictions récupérées avec succès depuis la base de données")
        return {"predictions": predictions_list}

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des prédictions : {str(e)}")
        return {"error": "Erreur lors de la récupération des prédictions"}

# Fonction pour récupérer les données de la base de données SQLite
def get_data_from_database(start_date: str, end_date: str) -> List[str]:
    try:
        # Construction de la requête SQL en fonction des paramètres
        conn = sqlite3.connect('data/predictions.db')
        query = f"SELECT DISTINCT date FROM predictions WHERE date BETWEEN '{start_date}' AND '{end_date}'"

        # Exécution de la requête SQL
        df_predictions = pd.read_sql_query(query, conn)
        conn.close()

        return df_predictions['date'].tolist()

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données depuis la base de données : {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des données depuis la base de données")

@app.post("/get_dates_in_range", response_model=List[str])
async def get_dates_in_range(data: DonneesEntree):
    try:
        logger.info(f"Demande de récupération de dates pour l'intervalle {data.start_date} à {data.end_date}")

        # Appeler la fonction pour récupérer les données depuis la base de données
        dates = get_data_from_database(data.start_date, data.end_date)

        logger.info(f"Dates récupérées avec succès pour l'intervalle {data.start_date} à {data.end_date}")
        return dates

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des dates pour l'intervalle {data.start_date} à {data.end_date} : {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des dates")

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
