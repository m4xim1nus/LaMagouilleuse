import numpy as np
import pandas as pd

from src.data_manager import read_csv

def prepare_plne_input(config):
    preferences_df = read_csv(config["allocations"]["preferences_path"])
    
    try:
        students_df = read_csv(config["allocations"]["students_path"])
        num_students = students_df.shape[0]  # Nombre d'élèves
    except FileNotFoundError:
        num_students = preferences_df.shape[1]  # Nombre d'élèves

    num_preferences = preferences_df.shape[0]  # Nombre de préférences pour chaque élève

    # Conversion de df en 3D-array
    preferences_matrix = convert_to_matrix(preferences_df, num_students, config["allocations"]["num_topics"], num_preferences)

    group_sizes = compute_group_sizes(num_students, config["allocations"]["group_size"])
    
    # Lecture du CSV contenant les paires d'élèves à ne pas mettre ensemble
    try:
        excluded_df = pd.read_csv(config["allocations"]["excluded_path"], sep=";")
        excluded_pairs_raw = list(excluded_df.itertuples(index=False, name=None))
        excluded_pairs = [(int(a)-1, int(b)-1) for a, b in excluded_pairs_raw if not (pd.isna(a) or pd.isna(b))]
    except FileNotFoundError:
        excluded_pairs = []
    
    plne_input = {
        'num_students': num_students,
        'num_topics': config["allocations"]["num_topics"],
        'num_preferences': num_preferences,
        'group_sizes': group_sizes if 'group_sizes' in locals() else None, # Sera traité dans le modèle PLNE avec topic_df
        'def_preference': config["allocations"]["def_preference"],
        'preferences_matrix': preferences_matrix,
        'excluded_pairs': excluded_pairs,
        'students_df': students_df if 'students_df' in locals() else None,
        'gender_ratio': config["allocations"]["gender_ratio"],
        'same_class_ratio': config["allocations"]["same_class_ratio"]
    }
    
    return plne_input

def convert_to_matrix(df, num_students, num_topics, num_preferences):
    # Initialiser la matrice z avec des def_preference
    preference_matrix = np.zeros((num_students, num_topics, num_preferences), dtype=int)

    df.columns = df.columns.astype(int)
    df = df.astype(int)  # convertir tout le DataFrame en entiers
    
    for student in range(num_students):
        for preference_rank in range(num_preferences):
            topic = df.iloc[preference_rank, student] - 1  # Sujets sont indexés à partir de 1
            preference_matrix[student][topic][preference_rank] = 1
    
    return preference_matrix

def compute_group_sizes(num_students, group_size):
    group_sizes = [0, group_size]
    if num_students % group_size != 0:
        group_sizes.append(group_size + 1)
    return group_sizes

