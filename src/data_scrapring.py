import pandas as pd
import requests
from bs4 import BeautifulSoup


# Fonction de scraping: Récupère l'URL de la page taux de references de bons et rend un dataframe
def scarp(url):
    df = {}
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    if soup.find_all('table'):
        table = soup.find_all('table')[0]
        df = pd.read_html(str(table))[0]
        df = df.drop(df.index[-1])
    return df


def to_date(x):
    return pd.to_datetime(x, format='%d/%m/%Y')


# Fonction de chargement de données: Elle récupère les infos et les formattent pour être utiliser après pour les calculs
def load_data(dd, mm, yyyy):
    url = "https://www.bkam.ma/Marches/Principaux-indicateurs/Marche-obligataire/Marche-des-bons-de-tresor/Marche" \
          f"-secondaire/Taux-de-reference-des-bons-du-tresor?date={dd}%2F{mm}%2F{yyyy}"
    df = scarp(url)
    if type(df) is not dict:
        df["Taux moyen pondéré"] = df["Taux moyen pondéré"].str.replace(',', '.').str.rstrip("%").astype(float)
        df['Maturite'] = (to_date(df["Date d'échéance"]) - to_date(df['Date de la valeur'])).dt.days + 1
        columns = ["Date d'échéance", 'Transaction', 'Taux moyen pondéré',
                   'Date de la valeur', 'Maturité (en jours)']
        values = df.to_numpy()
        return columns, values, df
    print('didnt return')
    return
