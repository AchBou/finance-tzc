# Fonction de constrution du graphes qui récupère les années et valeurs des taux zéro-coupons
def construct_graph_data(years, tzc):
    years_graph = []
    tzc_graph = []
    for i, year in enumerate(years):
        if year.is_integer():
            years_graph.append(year)
            tzc_graph.append((tzc[i] * 100))
    return years_graph, tzc_graph
