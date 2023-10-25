import yaml

def read_config(filename):
    with open(filename, 'r') as f:
        config = yaml.safe_load(f)
    return config