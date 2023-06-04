# Fonctions utilitaires pour les calculs mathématiques
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
