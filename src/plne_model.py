from pulp import LpProblem, LpVariable, lpSum, LpMinimize, PULP_CBC_CMD

def build_plne_model(plne_input):
    model = LpProblem(name="student-topic-allocation", sense=LpMinimize)
    num_students = plne_input['num_students']
    num_topics = plne_input['num_topics']
    preferences_matrix = plne_input['preferences_matrix']
    default_preference = plne_input['def_preference']
    group_sizes = plne_input['group_sizes']
    students_df = plne_input.get('students_df', None)
    gender_ratio = plne_input.get('gender_ratio', None)
    same_class_ratio = plne_input.get('same_class_ratio', None)

    # Variables
    y = create_y_variables(num_topics, group_sizes)
    x = create_x_variables(num_students, num_topics)

    # Objectif
    add_objective_function(model, x, num_students, num_topics, preferences_matrix, default_preference)
    # Contraintes de Unicité pour chaque élève
    add_unique_students_constraints(model, x, num_students, num_topics)
    # Contrainte d'unicité de taille de groupes pour chaque sujet j
    add_unique_topics_constraints(model, y, num_topics, group_sizes)
    # Contraintes sur la taille des groupes et conditions sur yjk
    add_topics_size_constraints(model, x, y, num_students, num_topics, group_sizes)
    # Contraintes sur le ratio de genre
    add_gender_constraints(model, x, num_topics, students_df, gender_ratio)
    # Contraintes sur le ratio de classe
    add_same_class_ratio_constraints(model, x, num_students, num_topics, students_df, same_class_ratio)

    return model

def solve_plne(plne_model, exclude_solutions=[]):
    for allocs in exclude_solutions:
        constraints = []
        for i, j in allocs.items():
            var_name = f"x_{i}_{j}"
            constraints.append(plne_model.variablesDict()[var_name])
        plne_model += lpSum(constraints) <= len(allocs) - 1

    # Solve the model
    plne_model.solve(PULP_CBC_CMD(msg=1))  # Mettre msg=1 pour voir les logs de résolution

    # Check if the optimization was successful
    if plne_model.status == 1:
        best_allocs = {}
        group_sizes = {}

        for v in plne_model.variables():
            if v.varValue == 1:
                prefix, i, j = v.name.split("_")
                i, j = int(i), int(j)
                if prefix == "x":
                    best_allocs[i] = j
                elif prefix == "y":
                    group_sizes[j] = i
                    
        return best_allocs, group_sizes
    else:
        return None  # Indique que la résolution a échoué

def create_y_variables(num_topics, group_sizes):
    y = {(j, k): LpVariable(name=f"y_{j}_{k}", cat='Binary') for j in range(num_topics) for k in group_sizes}
    return y


def create_x_variables(num_students, num_topics):
    return {(i, j): LpVariable(name=f"x_{i}_{j}", cat='Binary') for i in range(num_students) for j in range(num_topics)}


def add_objective_function(model, x, num_students, num_topics, preferences_matrix, def_preference):
    objective_terms = [
        ((k+1)**2 if preferences_matrix[i, j, k] else def_preference**2) * x[i, j] 
        for i in range(num_students) for j in range(num_topics) for k in range(preferences_matrix.shape[2])
    ]
    model += lpSum(objective_terms), "Objective"


def add_unique_students_constraints(model, x, num_students, num_topics):
    for i in range(num_students):
        model += lpSum(x[i, j] for j in range(num_topics)) == 1, f"UniqueStudent_{i}"

def add_unique_topics_constraints(model, y, num_topics, group_sizes):
    for j in range(num_topics):
        model += lpSum(y[j, k] for k in group_sizes) == 1, f"UniqueTopic_{j}"
    

def add_topics_size_constraints(model, x, y, num_students, num_topics, group_sizes):
    # Utilisation de group_sizes pour définir les contraintes de taille de groupe
        for j in range(num_topics):
            if len(group_sizes) == 2:
                model += lpSum(x[i, j] for i in range(num_students)) == group_sizes[1] * y[j, group_sizes[1]], f"GroupSize_{j}"
            elif len(group_sizes) == 3:
                model += lpSum(x[i, j] for i in range(num_students)) == group_sizes[1] * y[j, group_sizes[1]] + group_sizes[2] * y[j, group_sizes[2]], f"GroupSize_{j}"
            else:
                raise ValueError("group_sizes should have 2 or 3 elements")

        # Conditions sur yjk lorsque group_sizes est utilisé
        for j in range(num_topics):
            model += lpSum(y[j, k] for k in group_sizes) == 1, f"y_condition_1_{j}"

        # Contraintes basées sur le nombre de groupes de chaque taille
        group_sizes_number = compute_group_sizes_number(num_students, num_topics, group_sizes)
        for k in range(len(group_sizes)):
            model += lpSum(y[j, group_sizes[k]] for j in range(num_topics)) == group_sizes_number[k], f"y_condition_2_{k}"

def compute_group_sizes_number(num_students, num_topics, group_sizes):
    group_sizes_number = [0] * len(group_sizes)
    if len(group_sizes) == 2:
        group_sizes_number[1] = num_students // group_sizes[1]
        group_sizes_number[0] = num_topics - group_sizes_number[1]
    elif len(group_sizes) == 3:
        group_sizes_number[2] = num_students % group_sizes[1]
        group_sizes_number[1] = num_students // group_sizes[1] - group_sizes_number[2]
        group_sizes_number[0] = num_topics - group_sizes_number[1] - group_sizes_number[2]
    return group_sizes_number

def add_gender_constraints(model, x, num_topics, students_df, gender_ratio):
    if gender_ratio is not None:
        for j in range(num_topics):
            female_students_in_group = lpSum(x[i, j] for i in students_df.index[students_df['Gender'] == 'F'])
            male_students_in_group = lpSum(x[i, j] for i in students_df.index[students_df['Gender'] == 'M'])
            
            model += female_students_in_group >= gender_ratio * (female_students_in_group + male_students_in_group)
            model += male_students_in_group >= gender_ratio * (female_students_in_group + male_students_in_group)

def add_same_class_ratio_constraints(model, x, num_students, num_topics, students_df, same_class_ratio):
    if same_class_ratio is not None:
        classes = students_df['Class'].unique()
        for j in range(num_topics):
            for c in classes:
                students_in_class_in_group = lpSum(x[i, j] for i in students_df.index[students_df['Class'] == c])
                model += students_in_class_in_group <= same_class_ratio * lpSum(x[i, j] for i in range(num_students))

    return model