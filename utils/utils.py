

import os



def file_exists_check(func):
    
    def wrapper(file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' does not exist.")

    return wrapper