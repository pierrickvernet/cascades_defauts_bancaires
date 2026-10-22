"""
Module de visualisation et d'analyse dynamique pour la cascade de défauts.

Ce fichier contient les fonctions permettant :
1. De générer une animation étape par étape de la propagation des faillites.
2. D'analyser textuellement (tour par tour) le déroulement de la contagion.
3. De tracer la courbe de cascade (nombre cumulé de banques en défaut, tour par tour).
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
import networkx as nx
from IPython.display import display

# Import des fonctions métier depuis ton simulateur
from functions.mon_simulateur import depasse_capital, simuler


def simuler_avec_historique(G, origine, lam):
    """
    Simule la cascade de défauts et enregistre l'historique détaillé.
    
    Contrairement à la fonction classique qui ne renvoie que le nombre de défauts,
    celle-ci sauvegarde les identifiants (ID) des banques à chaque étape pour 
    permettre l'animation visuelle.
    
    Paramètres :
    - G (nx.DiGraph) : Le graphe orienté du réseau bancaire.
    - origine (str/int) : L'ID de la banque qui fait défaut initialement.
    - lam (float) : Le paramètre lambda (taux de perte en cas de défaut).
    
    Retourne :
    - defauts (set) : L'ensemble final des banques en faillite.
    - frames (list) : Une liste de tuples (banques_en_defaut, nouveaux_defauts) 
                      pour chaque étape de la simulation.
    """
    defauts = {origine}
    # Initialisation des images : t=0 (réseau sain), t=1 (choc initial)
    frames = [(set(), set()), ({origine}, {origine})]  
    
    while True:
        pertes = {}
        
        # 1. Calcul des pertes propagées par les banques déjà en défaut
        for i in defauts:
            for j in G.successors(i):
                if j not in defauts:
                    pertes[j] = pertes.get(j, 0.0) + lam * G[i][j]['montant']
                    
        # 2. Identification des nouvelles banques en faillite (perte > capital)
        nouveaux = {
            j for j, p in pertes.items() 
            if depasse_capital(p, G.nodes[j]['capital'])
        }
        
        # 3. Condition d'arrêt : fin de la cascade si aucun nouveau défaut
        if not nouveaux:
            break
            
        # 4. Mise à jour des statuts et sauvegarde pour l'animation
        defauts |= nouveaux
        frames.append((set(defauts), set(nouveaux)))
        
    return defauts, frames


def animer_scenario(G, origine, lam, reseau_id="", titre_extra="", seed=42):
    """
    Génère une animation (FuncAnimation) de la cascade de faillites.
    
    Paramètres :
    - G (nx.DiGraph) : Le graphe du réseau bancaire.
    - origine (str/int) : L'ID de la banque source du premier défaut.
    - lam (float) : Le taux de contagion.
    - reseau_id (str) : L'identifiant du réseau (pour l'affichage du titre).
    - titre_extra (str) : Informations supplémentaires à ajouter au titre.
    - seed (int) : Graine aléatoire pour figer la position des nœuds.
    
    Retourne :
    - anim (FuncAnimation) : L'objet d'animation prêt à être affiché ou sauvegardé.
    """
    # Récupération de l'historique complet de la cascade
    _, frames = simuler_avec_historique(G, origine, lam)
    
    # Définition de la disposition spatiale des nœuds (figée par la variable 'seed')
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=seed)
    nodes = list(G.nodes())
    edges = list(G.edges())
    
    # Création de la zone de dessin
    fig, ax = plt.subplots(figsize=(14, 9))
    
    def update(i):
        """Fonction appelée à chaque image (frame) de l'animation."""
        ax.clear()
        en_defaut, nouveaux = frames[i]

        # --- Définition des couleurs des nœuds ---
        node_colors = []
        for n in nodes:
            if n == origine and n in en_defaut:
                node_colors.append('yellow')    # Origine du choc
            elif n in nouveaux:
                node_colors.append('red')       # Tombe en défaut à ce tour
            elif n in en_defaut:
                node_colors.append('darkred')   # Déjà en défaut aux tours précédents
            else:
                node_colors.append('skyblue')   # Banque saine (survivante)
        
        # --- Définition du style des arêtes (liens) ---
        edge_colors = []
        edge_widths = []
        for u, v in edges:
            if u in en_defaut and v in en_defaut:
                edge_colors.append('red')       # Pertes entre deux banques en défaut
                edge_widths.append(2.0)
            elif u in en_defaut:
                edge_colors.append('orange')    # Contagion vers une banque encore saine
                edge_widths.append(1.2)
            else:
                edge_colors.append('gray')      # Lien inactif / sain
                edge_widths.append(0.5)

        # --- Tracé du réseau avec NetworkX ---
        nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=node_colors, 
                               node_size=550, edgecolors='black', ax=ax)
        nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=edge_colors, 
                               width=edge_widths, arrowstyle='->', arrowsize=15, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', ax=ax)

        # --- Gestion des textes (Titres et Légendes) ---
        if i == 0:
            sous_titre = "État initial"
        elif i == 1:
            sous_titre = f"Choc initial : défaut de {origine}"
        else:
            sous_titre = f"Tour {i-1} : {len(nouveaux)} nouveau(x) défaut(s)"
            
        titre_principal = f"Réseau {reseau_id} · Origine : {origine} · λ={lam} {titre_extra}"
        ax.set_title(f"{titre_principal}\n{sous_titre} | Total défaillances : {len(en_defaut)}", fontsize=13)
        
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow', markeredgecolor='black', markersize=10, label='Origine'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markeredgecolor='black', markersize=10, label='Défaut du tour'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='darkred', markeredgecolor='black', markersize=10, label='Défaut antérieur'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='skyblue', markeredgecolor='black', markersize=10, label='Saine')
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
        ax.axis('off')

    # Génération de l'animation
    anim = FuncAnimation(fig, update, frames=len(frames), interval=1500, repeat=True)
    
    # Fermeture de la figure pour éviter un affichage statique parasite dans le notebook
    plt.close(fig) 
    
    return anim


def analyser_scenario(G, origine, lam, reseau_id="Réseau", top_creanciers=8):
    """
    Rejoue un scénario et explique textuellement la cascade tour par tour.
    Affiche un tableau des premiers impactés et détaille les pertes.
    
    Paramètres :
    - G (nx.DiGraph) : Le graphe orienté du réseau bancaire.
    - origine (str/int) : L'ID de la banque qui fait défaut initialement.
    - lam (float) : Le paramètre lambda (taux de perte en cas de défaut).
    - reseau_id (str) : L'identifiant du réseau (pour l'affichage).
    - top_creanciers (int) : Nombre de créanciers directs à afficher dans le tableau.
    """
    # 1) Lancement de la simulation globale (utilise la fonction officielle du simulateur)
    defauts_finaux, nouveaux_par_etape = simuler(G, origine, lam)
    y_sim = (len(defauts_finaux) - 1) / (G.number_of_nodes() - 1)
    
    print(f"=== {reseau_id} | Origine {origine} | λ={lam} ===")
    print(f"Défauts finaux : {len(defauts_finaux)} banques -> y = {y_sim:.3f}")
    print(f"Nouveaux défauts par tour : {nouveaux_par_etape}\n")

    # 2) Créanciers directs de l'origine : qui reçoit le premier choc ?
    print(f"Créanciers directs de {origine} (dette e_ij, perte = λ·e_ij, capital c_j) :")
    lignes = []
    for j in G.successors(origine):
        e = G[origine][j]['montant']
        c = G.nodes[j]['capital']
        lignes.append({
            'Créancier': j, 
            'Dette (e_ij)': e, 
            'Perte (λ·e_ij)': lam * e,
            'Capital': c, 
            'Perte/Capital': lam * e / c,
            'Tombe au T1 ?': "OUI" if depasse_capital(lam * e, c) else "NON"
        })
        
    if lignes:
        df_choc = pd.DataFrame(lignes).sort_values('Perte/Capital', ascending=False)
        # Formatage en pourcentages pour plus de clarté
        df_choc['Perte/Capital'] = df_choc['Perte/Capital'].apply(lambda x: f"{x:.1%}")
        display(df_choc.head(top_creanciers).reset_index(drop=True))
    else:
        print("  Aucun (l'origine n'a pas de créancier : la cascade ne démarre pas)\n")

    # 3) Rejeu tour par tour pour l'analyse textuelle
    defauts = {origine}
    t = 0
    while True:
        pertes = {}
        for i in defauts:
            for j in G.successors(i):
                if j not in defauts:
                    pertes[j] = pertes.get(j, 0.0) + lam * G[i][j]['montant']
                    
        nouveaux = {j for j, p in pertes.items() if depasse_capital(p, G.nodes[j]['capital'])}
        
        if not nouveaux:
            # Fin de la cascade : affichage des "survivants de justesse"
            proches = sorted(pertes.items(), key=lambda kv: kv[1] / G.nodes[kv[0]]['capital'], reverse=True)[:3]
            print(f"\n--- Arrêt après le tour {t} ---")
            print("Survivantes les plus proches de la faillite :")
            for j, p in proches:
                ratio = p / G.nodes[j]['capital']
                print(f"  {j} : perte {p:.2f} / capital {G.nodes[j]['capital']:.2f} ({ratio:.1%} du capital consommé)")
            break
            
        t += 1
        print(f"\n--- Tour {t} : {len(nouveaux)} nouveau(x) défaut(s) ---")
        for j in sorted(nouveaux, key=lambda j: -pertes[j]): # Tri par montant de perte décroissant
            print(f"  {j} tombe : perte {pertes[j]:.2f} > capital {G.nodes[j]['capital']:.2f}")
            
        defauts |= nouveaux


def courbe_cascade(G, origine, lam, proportion=False):
    """
    Calcule la courbe de cascade : nombre cumulé de banques en défaut à chaque tour.

    Le tour 0 correspond au choc initial (l'origine seule est en défaut).
    Utilise la fonction officielle `simuler`, donc la même règle que le reste du projet.

    Paramètres :
    - G (nx.DiGraph) : Le graphe orienté du réseau bancaire.
    - origine (str/int) : L'ID de la banque qui fait défaut initialement.
    - lam (float) : Le paramètre lambda (taux de perte en cas de défaut).
    - proportion (bool) : si True, renvoie la proportion de défauts secondaires
                          (même définition que y : (défauts - 1) / (N - 1)).

    Retourne :
    - courbe (list) : valeur au tour 0, 1, 2, ... jusqu'à la fin de la cascade.
    """
    _, nouveaux_par_etape = simuler(G, origine, lam)

    cumul = 1                       # tour 0 : l'origine seule
    courbe = [cumul]
    for nouveaux in nouveaux_par_etape:
        cumul += nouveaux
        courbe.append(cumul)

    if proportion:
        n = G.number_of_nodes()
        return [(c - 1) / (n - 1) for c in courbe]
    return courbe


def tracer_courbes_cascade(G, origine, lam, lams_comparaison=(0.3, 0.6, 0.9),
                           reseau_id="", proportion=False):
    """
    Trace deux courbes de cascade côte à côte, pour le scénario (origine, lam) :
    (a) même origine : la courbe du scénario (trait épais) et, pour comparer,
        celles des autres valeurs de lambda de `lams_comparaison` ;
    (b) même lambda que le scénario : une courbe par origine possible
        (toutes les banques du réseau).

    Paramètres :
    - G (nx.DiGraph) : Le graphe orienté du réseau bancaire.
    - origine (str/int) : L'origine du scénario.
    - lam (float) : Le lambda du scénario (celui utilisé partout ailleurs dans le notebook).
    - lams_comparaison (tuple) : Valeurs de lambda ajoutées pour comparaison dans (a).
                                 Passer () pour ne tracer que le scénario.
    - reseau_id (str) : L'identifiant du réseau (pour l'affichage des titres).
    - proportion (bool) : si True, l'axe vertical est la proportion de défauts secondaires.

    Affiche la figure avec plt.show() et ne renvoie rien (évite un double affichage
    dans un notebook quand l'appel est la dernière ligne de la cellule).
    """
    n = G.number_of_nodes()
    ylabel = ("Proportion de défauts secondaires" if proportion
              else "Banques en défaut (cumul)")
    ylim = (0, 1.02) if proportion else (0, n)

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

    # (a) Même origine : le scénario en trait épais, les autres lambda pour comparer
    for lam_i in sorted(set(lams_comparaison) | {lam}):
        c = courbe_cascade(G, origine, lam_i, proportion)
        est_scenario = (lam_i == lam)
        axes[0].plot(range(len(c)), c, marker='o',
                     lw=3 if est_scenario else 1.5,
                     alpha=1.0 if est_scenario else 0.7,
                     label=f"λ = {lam_i}" + (" (scénario)" if est_scenario else ""))
    axes[0].set(title=f"Cascade depuis {origine} (réseau {reseau_id})",
                xlabel="Tour", ylabel=ylabel, ylim=ylim)
    axes[0].legend()

    # (b) Lambda du scénario, toutes les origines
    for o in G.nodes():
        c = courbe_cascade(G, o, lam, proportion)
        axes[1].plot(range(len(c)), c, color='steelblue', alpha=0.25)
    axes[1].set(title=f"Cascade de chaque origine (λ = {lam})",
                xlabel="Tour", ylabel=ylabel, ylim=ylim)

    plt.tight_layout()
    plt.show()