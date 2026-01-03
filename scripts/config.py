import os

def load_config():
    return {
        'background_image': os.environ.get('BACKGROUND_IMAGE', 'static/background.jpg'),
        'history_file': os.environ.get('HISTORY_FILE', 'history.json'),
        'shorts_dir': os.environ.get('SHORTS_DIR', 'shorts'),
        'compilation_dir': os.environ.get('COMPILATION_DIR', 'compilations'),
        'max_retries': int(os.environ.get('MAX_RETRIES', 3)),
        'timeout_seconds': int(os.environ.get('TIMEOUT_SECONDS', 300))
    }
