# Magouilleuse v1

## Description

Un outil pour aider les professeurs à répartir les élèves entre différents sujets en fonction de leurs préférences.

## Installation

1. **Clonez le dépôt** :
`git clone [https://github.com/m4xim1nus/LaMagouilleuse]`

2. **Mettez en place un environnement virtuel** (recommandé) :
`python -m venv venv`


3. **Activez l'environnement virtuel** :

- Sur Windows :
  
  ```
  .\venv\Scripts\activate
  ```

- Sur MacOS/Linux :
  
  ```
  source venv/bin/activate
  ```

4. **Installez les dépendances** :

`pip install -r requirements.txt`


## Configuration

1. Assurez-vous d'avoir les fichiers CSV d'input dans le dossier `data/`: la liste des élèves, les préférences des élèves, les paires d'élèves exclues.

2. Configurez `config.yaml` selon vos besoins. Ce fichier contient les paramètres pour le processus de répartition.

## Utilisation

1. **Exécutez le script principal** :
`python main.py config.yaml`


2. **Vérifiez l'output** :

Les résultats seront sauvegardés dans le fichier spécifié dans `config.yaml` (par défaut : `./data/test_allocations.csv`).



