from flask import Flask, render_template, request
import requests as requests
import pandas as pd
from bs4 import BeautifulSoup

app = Flask(__name__)


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


def load_data(dd, mm, yyyy):
    # Code to load data from the internet
    url = "https://www.bkam.ma/Marches/Principaux-indicateurs/Marche-obligataire/Marche-des-bons-de-tresor/Marche" \
          f"-secondaire/Taux-de-reference-des-bons-du-tresor?date={dd}%2F{mm}%2F{yyyy}"
    df = scarp(url)
    if type(df) is not dict:
        df["Taux moyen pondéré"] = df["Taux moyen pondéré"].str.replace(',', '.').str.rstrip("%").astype(float)
        df['Maturite'] = (to_date(df["Date d'échéance"]) - to_date(df['Date de la valeur'])).dt.days + 1
        columns = df.columns
        values = df.to_numpy()
        return columns, values, df
    print('didnt return')
    return

def taux_actuariel(maturites, taux_moyens_pond):
    taux_actuariels = []
    for i in range(len(maturites)):
        if maturites[i] < 1:
            taux_actuariels.append(((1 + (taux_moyens_pond[i] * maturites[i])) ** (1 / maturites[i])) - 1)
        else:
            taux_actuariels.append(taux_moyens_pond[i])
    return taux_actuariels


def zc(maturities, rates):
    if len(rates) != len(maturities):
        raise ValueError("Les listes de taux actuariels et de maturités doivent avoir la même longueur.")
    n = len(maturities)
    taux_zero = []
    for i in range(n):
        if maturities[i] <= 1:
            taux_zero.append(rates[i])
        else:
            taux_zero.append(
                ((1 / ((1 / (1 + rates[i])) - (1 / (1 + taux_zero[-1])) + (1 / ((1 + rates[i]) ** 2)))) ** (1 / 2)) - 1)

    return taux_zero


def inter(t: float, t2: float, ech: float, ech1: float, ech2: float) -> float:
    return ((t2 - t) * (ech1 - ech) / (ech2 - ech)) + t


def generate_maturity_list(maturity):
    mlist = []
    n = 1
    year = 365 * n
    for m in maturity:
        if m <= year:
            mlist.append(m)
        elif m > year:
            while m > year:
                mlist.append(year)
                n = n + 1
                year = 365 * n
            mlist.append(m)
    return mlist


def get_first_non_na(li, i):
    for j, entry in enumerate(li):
        if entry != 'NA':
            return j + i


def fill_na(tmp_list, maturity_list):
    for i, entry in enumerate(tmp_list):
        if entry == 'NA':
            j = get_first_non_na(tmp_list[i:], i)
            tmp_list[i] = inter(
                tmp_list[i - 1],
                tmp_list[j],
                maturity_list[i - 1],
                maturity_list[i],
                maturity_list[j]
            )
    return tmp_list


def calculate_data(df):
    maturity_list = generate_maturity_list(df['Maturite'])
    tmp_list = []
    for i, entry in enumerate(maturity_list):
        if entry in df['Maturite'].values:
            tmp_list.append(df.loc[df['Maturite'] == entry, 'Taux moyen pondéré'].values[0])
        else:
            tmp_list.append('NA')
    maturities = [m / 365 for m in maturity_list]
    tmp_list = fill_na(tmp_list, maturities)
    tmp = [m / 100 for m in tmp_list]
    ta_list = taux_actuariel(maturities, tmp)
    tzc_list = zc(maturities, ta_list)
    return maturity_list, maturities, tmp, ta_list, tzc_list


def construct_graph_data(years, tzc):
    years_graph = []
    tzc_graph = []
    for i, year in enumerate(years):
        if year.is_integer():
            years_graph.append(year)
            tzc_graph.append((tzc[i] * 100))
    return years_graph, tzc_graph


@app.route('/', methods=['GET', 'POST'])
def main():  # put application's code here
    if request.method == 'POST':
        # Process data from the form
        date = request.form.get('data')
        print(date)
        yyyy, mm, dd = date.split('-')
        data = load_data(dd, mm, yyyy)
        if data:
            c_data = calculate_data(data[2])
            graph_data = construct_graph_data(c_data[1], c_data[4])
            print(c_data[0])
            return render_template('index.html', columns=data[0], data=data[1], date=date,
                                   maturity=c_data[0], tmp=c_data[2], ta=c_data[3], tzc=c_data[4], graph_data=graph_data)
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
