import os
import yaml

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            last_folder = config.get('last_folder', '')
            dark_mode = config.get('dark_mode', False)
            return last_folder, dark_mode
    else:
        return '', False

def save_config(last_folder, dark_mode, csv_path=None):
    config = {
        'last_folder': last_folder,
        'dark_mode': dark_mode,
        'csv_path': csv_path
    }
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
