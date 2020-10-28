import os

from utils.encoder import json_load_byteified

config = {}

"""
A simple configuration loader
"""
project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
with open(os.path.join(project_root, './config.json')) as f:
    config = json_load_byteified(f)

