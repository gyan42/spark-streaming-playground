import os
import shutil

def check_n_mk_dirs(path, is_remove=False):
    if os.path.exists(path):
        if is_remove:
            shutil.rmtree(path)
    else:
        os.makedirs(path)