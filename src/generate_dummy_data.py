import pandas as pd
import numpy as np

def generate_dummy_data(num_students=100, num_topics=10, num_preferences=3, num_excluded_pairs=5, num_classes=7, output_path="data/", seed=None):
    rng = np.random.default_rng(seed=seed)

    # Génération de preferences.csv
    preferences_data = {}
    for student in range(num_students):
        preferences_data[student+1] = rng.choice(num_topics, size=num_preferences, replace=False) + 1

    preferences_df = pd.DataFrame(preferences_data)
    preferences_df.to_csv(output_path + "test_preferences.csv", index=False, sep=";")

    # # Génération de excluded.csv
    excluded_pairs = [rng.choice(num_students, 2, replace=False) for _ in range(num_excluded_pairs)]
    excluded_df = pd.DataFrame(excluded_pairs, columns=["Student_A", "Student_B"])
    excluded_df.to_csv(output_path + "test_excluded.csv", index=False, sep=";")

    # Génération de students.csv
    genders = ['M', 'F']

    # Distribution équilibrée des élèves entre les classes
    base_students_per_class = num_students // num_classes
    remaining_students = num_students % num_classes

    students_classes = [f"Class_{i}" for i in range(num_classes) for _ in range(base_students_per_class)]
    # Ajouter les élèves restants à certaines classes
    students_classes += [f"Class_{i}" for i in range(remaining_students)]
    rng.shuffle(students_classes)

    students_data = {
        'ID': [i+1 for i in range(num_students)],
        'Gender': rng.choice(genders, num_students),
        'Class': students_classes
    }
    students_df = pd.DataFrame(students_data)
    students_df.to_csv(output_path + "test_students.csv", index=False, sep=";")

    # # Génération de topics.csv
    min_sizes = 0 # rng.integers(4, 6, num_topics)
    max_sizes = 3 # min_sizes + rng.integers(1, 3, num_topics)
    topics_data = {
        'ID': [i+1 for i in range(num_topics)],
        'min_size': min_sizes,
        'max_size': max_sizes
    }
    topics_df = pd.DataFrame(topics_data)
    topics_df.to_csv(output_path + "test_topics.csv", index=False, sep=";")
