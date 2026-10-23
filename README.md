# Réseaux bancaires et contagion : simuler, prédire, protéger

Hackathon Data Science & Risque, Université de Bordeaux (25 septembre – 23 octobre 2026).

Des banques se prêtent de l'argent. Quand l'une d'elles ne rembourse plus, ses créanciers perdent une partie de leur argent et certains peuvent tomber à leur tour : c'est une **cascade de défauts**. Ce projet étudie 12 réseaux fictifs de 60 banques et répond à la question suivante :

> À partir de la structure d'un réseau et des caractéristiques des banques, peut-on prévoir l'ampleur d'une cascade de défauts et proposer une intervention qui en réduit les conséquences ?

Les réseaux sont fictifs et le simulateur est un modèle pédagogique simplifié (cascade à seuil) : les résultats ne constituent pas des prévisions sur de vraies banques.

## Auteurs

- Vernet Pierrick
- Ricci Louis

## Contenu du dépôt

```
.
├── reseaux_bancaires_vernet_ricci.ipynb   # notebook principal (à exécuter du début à la fin)
├── data/
│   ├── banques.csv                        # 720 lignes : reseau_id, banque_id, capital (séparateur « ; »)
│   ├── expositions.csv                    # dettes : reseau_id, debiteur_id, creancier_id, montant
│   ├── repartition.csv                    # usage de chaque réseau : apprentissage / validation / test
│   ├── tirages_aleatoires.csv             # 10 tirages officiels de 5 banques par réseau
│   └── dictionnaire_variables.md
└── functions/
    ├── mon_simulateur.py                  # construire_graphe et simuler (notre simulateur)
    ├── fonctions.py                       # animation, analyse tour par tour, courbes de cascade
    └── aides_contagion.py                 # aides fournies par l'encadrant
```

## Lancer le code

1. Installer Python (3.10 ou plus ; le notebook a été exécuté avec Python 3.13) et les dépendances :

   ```bash
   pip install numpy pandas networkx matplotlib seaborn plotly statsmodels scikit-learn jupyter
   ```

2. Se placer à la **racine du dépôt** (les chemins `data/` et `functions/` sont relatifs), puis lancer :

   ```bash
   jupyter notebook reseaux_bancaires_vernet_ricci.ipynb
   ```

3. Exécuter toutes les cellules (*Run All*). Le temps de calcul est de quelques minutes : la génération des 2 160 scénarios, puis les recherches d'hyperparamètres et les simulations d'intervention sont les étapes les plus longues.

Vérification du simulateur : le vérificateur fourni (`verifier_simulateur.py`) fait passer 9 tests à `construire_graphe` et `simuler`. Lancez-le depuis le dossier qui contient ce fichier, avec le chemin de `mon_simulateur.py` en argument.

### Bibliothèques utilisées

| Usage | Bibliothèques |
|---|---|
| Données et calcul | `pandas`, `numpy` |
| Graphes | `networkx` |
| Visualisation | `matplotlib`, `seaborn`, `plotly` |
| Statistiques | `statsmodels` (VIF) |
| Machine learning | `scikit-learn` (arbre, forêt, gradient boosting, régression linéaire, modèles de référence, grille d'hyperparamètres, importance par permutation) |
| Bibliothèque standard | `sys`, `random`, `itertools` |

Pour figer les versions exactes utilisées : `pip freeze > requirements.txt`.

## Graines aléatoires

- **Toutes les graines du code valent 42** : disposition du graphe (`nx.spring_layout`), échantillon des graphiques, arbre, forêt aléatoire, gradient boosting et importance par permutation (`random_state=42`).
- **Intervention aléatoire** : les 10 tirages de 5 banques par réseau proviennent du fichier officiel `tirages_aleatoires.csv` (graines 0 à 9), identique pour toutes les équipes.

## Démarche (plan du notebook)

| Partie | Contenu |
|---|---|
| 1 | Chargement des données, contrôles de qualité (manquants, doublons, capitaux et montants positifs, auto-dettes, banques inconnues) et statistiques descriptives |
| 2 | Import et vérification de `construire_graphe` et `simuler` |
| 3 | Exploration du réseau R01 : degrés, poids, hypothèses, visualisation statique et animée de la cascade, courbes de cascade |
| 4 | Simulation des 2 160 scénarios (12 réseaux × 60 origines × λ ∈ {0,3 ; 0,6 ; 0,9}) |
| 5 | Variables explicatives, découpage par réseau (8 / 2 / 2) et analyse exploratoire |
| 6 | Modèles : références par la médiane, arbre, forêt aléatoire, gradient boosting, OLS ; analyse des erreurs importantes |
| 7 | Intervention avec un budget de 10 % des capitaux sur 5 banques : sans intervention, aléatoire, règle ciblée |

### Règle de propagation

La banque d'origine fait défaut d'office. À chaque tour, une banque *j* subit la perte `L_j = λ × Σ e_ij` sur ses créances envers les banques déjà tombées, et fait défaut si **`L_j` dépasse strictement son capital**. Tous les défauts d'un même tour sont ajoutés simultanément, jusqu'à stabilisation. La mesure principale est `y = (|D_final| − 1) / (N − 1)`, la proportion de défauts secondaires.

### Variables explicatives

λ, capital de l'origine, degrés et poids entrants et sortants de l'origine (socle du sujet), plus deux variables calculées sur le réseau initial uniquement :

- `max_ratio` : plus grand rapport entre la dette de l'origine envers un créancier et le capital de ce créancier ;
- `frag_moy_creanciers` : fragilité moyenne des créanciers directs de l'origine, la fragilité d'une banque étant `Σ créances reçues / capital`.

Aucun résultat de la cascade n'est utilisé comme variable.

### Protocole d'évaluation

- Découpage **par réseau**, jamais ligne par ligne : 8 réseaux pour l'apprentissage, 2 pour la validation, 2 pour le test (`repartition.csv`).
- Hyperparamètres choisis sur la validation (`GridSearchCV` avec `PredefinedSplit`), modèles réentraînés sur apprentissage + validation, test utilisé une seule fois.
- Références « paresseuses » : médiane globale et médiane par λ.
- Intervention : règle choisie sur les réseaux d'apprentissage et de validation, figée, puis évaluée une seule fois sur les 2 réseaux de test, avec les mêmes 60 origines et les mêmes 3 valeurs de λ pour toutes les stratégies.

## Hypothèses

1. **Vulnérabilité** : moins une banque a de débiteurs différents, plus elle est fragile (pas de diversification de ses créances).
2. **Contagion** : une banque ayant de nombreux créanciers propage plus largement les défauts.

## Principaux résultats

**Prédiction de l'ampleur de la cascade (test).** La forêt aléatoire est le meilleur modèle : MAE ≈ 0,074 (erreur moyenne d'environ 7 points de pourcentage) et R² ≈ 0,77, bien au-dessus des deux références par la médiane. La régression linéaire (OLS) est nettement moins bonne.

**Intervention (test, réseaux R02 et R09).**

| Stratégie | y moyen | Gain vs « sans » |
|---|---|---|
| Sans intervention | 19,99 % | — |
| 5 banques au hasard (moyenne de 10 tirages, écart-type 0,58 point) | 18,51 % | 1,48 point |
| 5 banques ciblées (règle **fragilité × poids sortant**) | 16,57 % | 3,42 points |

La règle ciblée fait mieux que chacun des 10 tirages aléatoires et son avantage est maximal pour λ = 0,6. Elle a été choisie sur les réseaux d'apprentissage et de validation (gain de 6,25 points sur ces réseaux), parmi quatre règles comparées. La plus grande cascade observée (0,78 sur le test) n'est pas réduite par l'intervention.

## Limites

- Les résultats reposent sur 12 réseaux issus d'un générateur, dont seulement 2 pour le test : l'évaluation finale est limitée et bruitée.
- Le simulateur est une cascade à seuil : ni paiements partiels, ni ventes d'actifs, ni réaction des marchés.
- La moyenne de `y` sur les scénarios est un indicateur de comparaison, pas une probabilité de crise réelle.
- Le gain de la règle ciblée est plus faible sur le test que sur les réseaux de sélection, ce qui rappelle que la règle a été choisie sur ces derniers.
- Les variables du modèle décrivent l'origine et son voisinage direct : elles ne capturent pas toute la dynamique du réseau, ce que montre l'analyse des erreurs importantes.

## Aides et ressources externes

- Kit de départ du hackathon : sujet, cours, jeux de données, `aides_contagion.py` (fonctions `depasse_capital`, `generer_scenarios`, `comparer_interventions`, `resumer_interventions`, `charger_tirages`, etc.) et vérificateur du simulateur.
- Documentation de NetworkX, pandas, scikit-learn, seaborn et statsmodels.
- Assistant d'IA générative (Claude, Anthropic) : aide à la rédaction et à la mise en forme du code (visualisations, comparaison des modèles, comparaison des stratégies d'intervention) et relecture de textes. *À ajuster selon l'usage réel de l'équipe.*
