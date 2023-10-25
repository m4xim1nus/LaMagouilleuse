import numpy as np
import pandas as pd

def allocs_to_df(best_allocs, original_preferences):    
    final_df = pd.DataFrame(list(best_allocs.items()), columns=['Student', 'Topic'])
    final_df['Student'] += 1
    final_df['Topic'] += 1
    
    # Ajouter la colonne 'Preference_Rank'
    final_df['Preference_Rank'] = final_df.apply(lambda row: original_preferences[row['Student'] - 1].index(row['Topic']) + 1 if row['Topic'] in original_preferences[row['Student'] - 1] else 'NaN', axis=1)

    return final_df

def create_original_preferences_from_z(z):
    original_preferences = {}
    
    for student in range(z.shape[0]):
        original_preferences[student] = []
        for rank in range(z.shape[2]):
            topic = np.argmax(z[student, :, rank])
            original_preferences[student].append(topic + 1)  # +1 pour correspondre à l'indexation originale
    
    return original_preferences