from pathlib import Path
import pandas as pd
import yaml
import argparse

from src.config_manager import read_config
from src.plne_model import build_plne_model, solve_plne
from src.data_preparation import prepare_plne_input
from src.data_postprocessing import allocs_to_df, create_original_preferences_from_z
from src.generate_dummy_data import generate_dummy_data

if __name__ == "__main__":  
    parser = argparse.ArgumentParser(description="Gestionnaire du projet Magouilleuse")
    parser.add_argument('filename')
    parser.add_argument('--generate-dummy-data', action='store_true', help="Générer des données fictives avant de lancer le programme")
    args = parser.parse_args()

    # Utilisation de la nouvelle fonction pour lire la config
    config = read_config(args.filename)

    if args.generate_dummy_data or config["allocations"]["use_dummy_data"]:
        generate_dummy_data(
            num_students=config["tests"]["num_students"], 
            num_topics=config["allocations"]["num_topics"],
            num_preferences=config["tests"]["num_preferences"], 
            num_excluded_pairs=config["tests"]["num_excluded_pairs"],
            num_classes=config["tests"]["num_classes"],
            output_path=config["tests"]["output_path"],
            seed=config["tests"]["seed"]
        )
        # Mise à jour des chemins vers les fichiers CSV pour pointer vers les données fictives
        config["allocations"]["preferences_path"] = './data/test_preferences.csv'
        config["allocations"]["students_path"] = './data/test_students.csv'
        config["allocations"]["topics_path"] = './data/test_topics.csv'
        config["allocations"]["excluded_path"] = './data/test_excluded.csv'
    
    config = read_config("config.yaml")  # Assurez-vous que vous avez cette fonction

    plne_input = prepare_plne_input(config)
    plne_model = build_plne_model(plne_input)
    best_allocs_list = []  # Liste pour stocker les meilleures allocations
    final_dfs = []  # Liste pour stocker les DataFrames des meilleures solutions

    # Trouver les top solutions
    for i in range(config["allocations"]["num_top"]):    
        best_allocs, group_sizes = solve_plne(plne_model, best_allocs_list)
        best_allocs_list.append(best_allocs)
        original_preferences = create_original_preferences_from_z(plne_input['preferences_matrix'])
        
        final_df = allocs_to_df(best_allocs, original_preferences)
        final_df['Rank'] = i + 1  # Ajoute une colonne pour le classement de cette solution
        final_dfs.append(final_df)

    # Concaténez tous les DataFrames dans final_dfs
    final_dfs_concat = pd.concat(final_dfs, keys=[f"Rank_{i+1}" for i in range(len(final_dfs))])

    # Sauvegarde le DataFrame concaténé
    final_dfs_concat.to_csv(config["allocations"]["output_path"], sep=";")