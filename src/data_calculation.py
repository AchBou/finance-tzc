from utils.functions import taux_actuariel, inter, zc

# Fonction de génération de la liste des maturités
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

#Fonction qui cherche la première valeur non-nul par calculer les valeurs nul avec la fonction fill_na
def get_first_non_na(li, i):
    for j, entry in enumerate(li):
        if entry != 'NA':
            return j + i

#Remplissage des valeurs NA
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

#Fonction principale de calcul des données des valeurs zéro-coupons: Elle retourne des listes de maturités, taux moyens pondérés, taux actuariels et zéro-coupons
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
