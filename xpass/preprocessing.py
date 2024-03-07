import os
import json
import pandas as pd

from xpass.params import STATSBOMB_DATA, THREE_SIXTY, MATCHES, EVENTS, GENDER
from xpass.utils import get_reception_shape_features

# from sklearn.preprocessing import FunctionTransformer

from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer, make_column_selector
from sklearn.base import TransformerMixin, BaseEstimator


class ReceptionTransformer(TransformerMixin, BaseEstimator):
    # BaseEstimator generates the get_params() and set_params() methods that all Pipelines require
    # TransformerMixin creates the fit_transform() method from fit() and transform()

    def __init__(self, corr_width: float = 2, alpha: float = 10, length: float = 50):
        self.corr_width = corr_width
        self.alpha = alpha
        self.length = length


    def fit(self, X, y = None):
        # Here you store what needs to be stored/learned during .fit(X_train) as instance attributes
        # Return "self" to allow chaining .fit().transform()
        return self

    def transform(self, X, y = None):
        # Return the result as a DataFrame for an integration into the ColumnTransformer

        X[["n_teammates", "n_opponents"]] = X.apply(
            lambda x: get_reception_shape_features(
                x, corr_width = self.corr_width, alpha = self.alpha, length = self.length),
            axis = 1, result_type = "expand"
        )

        X_transformed = X.drop(columns = "freeze_frame")

        return X_transformed


num_col = make_column_selector(dtype_include=["float64", "int64"])
num_tranformer = make_pipeline(
    SimpleImputer(strategy = "mean"),
    MinMaxScaler()
)

cat_col = make_column_selector(dtype_include=["object"])
cat_transformer = make_pipeline(
    SimpleImputer(strategy = "most_frequent"),
    OneHotEncoder(handle_unknown = "ignore")
)

preprocessing = make_column_transformer(
    (num_tranformer, num_col),
    (cat_transformer, cat_col)
)

pipeline = make_pipeline(
    ReceptionTransformer(),
    preprocessing
)
