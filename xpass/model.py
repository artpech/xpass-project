import os
import pickle

from xpass.params import SIZE, PROJECT_HOME

def load_model(
    path: str = os.path.join(PROJECT_HOME, "data", "models"),
    model_name: str = f"model_{SIZE}.pkl"
    ):
    model_path = os.path.join(path, model_name)
    model = pickle.load(open(model_path,"rb"))
    return model
