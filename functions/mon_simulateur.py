"""Votre simulateur de cascade : c'est le fichier que votre équipe complète.

Écrivez les deux fonctions ci-dessous, puis vérifiez-les depuis le dossier du dépôt :

    python aides/verifier_simulateur.py mon_simulateur.py

Le vérificateur lance les 9 tests du sujet et explique chaque échec.
Ne changez pas le nom des fonctions ni leurs arguments : les aides les appellent ainsi.
"""

import os
import sys

import networkx as nx

# Rend le dossier aides/ importable, que ce fichier soit lancé ou importé depuis un notebook.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "aides"))
from functions.aides_contagion import depasse_capital  # noqa: E402


def construire_graphe(banques_r, expositions_r):

    # Initialiser un graphe orienté vide
    graphe = nx.DiGraph()

    # Ajouter les banques comme nœuds avec leur capital
    for _, row in banques_r.iterrows():
        graphe.add_node(row['banque_id'], capital=row['capital'])

    # Ajouter les expositions comme arêtes avec leur montant
    for _, row in expositions_r.iterrows():
        graphe.add_edge(row['debiteur_id'], row['creancier_id'], montant=row['montant'])

    return graphe





def simuler(G, origine, lam):
    """Simule la cascade à seuil du sujet (section 3) à partir de la banque d'origine.
    ...
    """
    defauts = {origine}
    nouveaux_par_etape = []

    while True:
        # Pour chaque banque encore active, on cumule les pertes venant
        # de TOUTES les banques déjà en défaut (recalcul complet, pas incrémental).
        pertes = {}
        for i in defauts:
            for j in G.successors(i):  # i doit à j (arête i -> j)
                if j in defauts:
                    continue
                pertes[j] = pertes.get(j, 0.0) + lam * G[i][j]['montant']

        # Nouveaux défauts : perte strictement supérieure au capital
        nouveaux = {
            j for j, perte in pertes.items()
            if depasse_capital(perte, G.nodes[j]['capital'])
        }

        if not nouveaux:
            break

        defauts |= nouveaux
        nouveaux_par_etape.append(len(nouveaux))

    return defauts, nouveaux_par_etape






