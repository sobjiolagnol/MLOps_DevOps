# Utilisez une image de base avec Python
FROM python:3.12.0

# Copiez les fichiers nécessaires dans le conteneur
COPY . /App

# Définir le répertoire de travail
WORKDIR /App



# Installer les dépendances
RUN pip install fastapi uvicorn joblib statsmodels loguru pytest
# Installer les dépendances à partir du fichier requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# Exposer le port 8000 pour accéder à l'API
EXPOSE 8000

# Lancer l'application FastAPI avec Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
#RUN uvicorn main:app --reload