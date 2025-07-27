import sqlite3
import csv

# Connexion à la base de données
conn = sqlite3.connect('temperature_Dakar.db')
cursor = conn.cursor()

# Création de la table temperature si elle n'existe pas déjà
cursor.execute('''CREATE TABLE IF NOT EXISTS temperature (
                    date TEXT,
                    temperature_2m REAL
                )''')

# Fonction pour insérer les données du CSV dans la table temperature
def enregistrer_temperature(data):
    cursor.executemany('''INSERT INTO temperature (date, temperature_2m) VALUES (?, ?)''', data)
    conn.commit()

# Lecture du fichier CSV et insertion des données dans la table temperature
tampon_donnees = []
with open('hourly_data.csv', 'r') as fichier_csv:
    lecteur_csv = csv.DictReader(fichier_csv)
    for ligne in lecteur_csv:
        date = ligne['date']
        temperature_2m = float(ligne['temperature_2m'])
        tampon_donnees.append((date, temperature_2m))

# Insérer toutes les données du tampon dans la base de données en une seule transaction
if tampon_donnees:
    enregistrer_temperature(tampon_donnees)

print("Données de la table temperature enregistrées avec succès.")

# Fonction pour afficher les données de la table temperature
def afficher_temperature():
    cursor.execute('''SELECT * FROM temperature''')
    lignes = cursor.fetchall()
    for ligne in lignes:
        print(ligne)  # Afficher chaque ligne de résultat

# Appel de la fonction pour afficher les données de la table temperature
afficher_temperature()

# Fermeture de la connexion à la base de données
conn.close()
