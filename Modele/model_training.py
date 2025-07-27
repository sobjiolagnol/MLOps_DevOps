from statsmodels.tsa.arima.model import ARIMA
import joblib
import os
from connectiondatabase import Connexion
from preprocessing import process_data

def train_model(data):
    # Initialiser le modèle ARIMA
    order = (1, 1, 1)  # Assurez-vous de choisir les paramètres corrects en fonction de l'analyse des données
    model = ARIMA(data, order=order)
    model_fit = model.fit()
    return model_fit

file_path = 'Modele'

def save_model(model, folder_path, file_name):
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Chemin complet du fichier de sauvegarde
    file_path = os.path.join(folder_path, file_name)

    # Sauvegarde du modèle
    joblib.dump(model, file_path)

    return file_path

# Charger les données
donnees = Connexion()
data1 = process_data(donnees)

# Entraîner le modèle ARIMA
Model_ARIMA = train_model(data1)

# Sauvegarder le modèle
save_model(Model_ARIMA, file_path, 'model_arima')
