import pandas as pd
import data
import pandas as pd


def process_data(data_path):
    # Charger les données à partir du fichier CSV
    temperature_df = pd.read_csv(data_path, index_col=None)

    # Convertir la colonne de dates en type datetime
    temperature_df['date'] = pd.to_datetime(temperature_df['date'])

    # Supprimer la partie "+00:00" du format de date
    temperature_df['date'] = temperature_df['date'].dt.strftime('%Y-%m-%d %H:%M')

    # Convertir à nouveau la colonne de dates en type datetime
    temperature_df['date'] = pd.to_datetime(temperature_df['date'])

    # Définir la colonne 'date' comme index
    temperature_df.set_index('date', inplace=True)

    # Calculer la moyenne des valeurs à chaque intervalle de 3 heures
    temperature_new_df = temperature_df.resample('3h').mean()

    # Définir le nom de l'index de la nouvelle série de données
    temperature_new_df.index.names = ['Timestamp']
    # Renommer la colonne "Unnamed: 0" en "humidity"
    temperature_new_df.rename(columns={'Unnamed: 0': 'humidity'}, inplace=True)

    print(temperature_new_df)

    return temperature_new_df


# Appel de la fonction avec le chemin vers le fichier CSV
result = process_data('hourly_data.csv')


