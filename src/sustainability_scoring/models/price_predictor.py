"""Price prediction models using sustainability features."""

from typing import Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class PricePredictor:
    """
    Machine learning model for predicting fashion product prices
    based on sustainability characteristics.

    Supports Decision Tree, Random Forest, and Gradient Boosting models.

    Attributes
    ----------
    model : sklearn estimator
        The trained model.
    model_type : str
        Type of model ('decision_tree', 'random_forest', 'gradient_boosting').
    feature_names : list
        Names of features used for training.
    metrics : dict
        Performance metrics from the last evaluation.
    """

    SUPPORTED_MODELS = {
        "decision_tree": DecisionTreeRegressor,
        "random_forest": RandomForestRegressor,
        "gradient_boosting": GradientBoostingRegressor,
    }

    DEFAULT_PARAMS = {
        "decision_tree": {
            "max_depth": 6,
            "min_samples_leaf": 10,
            "random_state": 42,
        },
        "random_forest": {
            "n_estimators": 500,
            "max_depth": None,
            "min_samples_leaf": 5,
            "random_state": 42,
            "n_jobs": -1,
        },
        "gradient_boosting": {
            "n_estimators": 500,
            "learning_rate": 0.05,
            "max_depth": 3,
            "subsample": 0.8,
            "random_state": 42,
        },
    }

    def __init__(self, model_type: str = "random_forest"):
        """
        Initialize the price predictor.

        Parameters
        ----------
        model_type : str
            Type of model to use. One of 'decision_tree', 'random_forest',
            or 'gradient_boosting'.
        """
        if model_type not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unknown model type: {model_type}. "
                f"Supported: {list(self.SUPPORTED_MODELS.keys())}"
            )

        self.model_type = model_type
        self.model = None
        self.feature_names = None
        self.metrics = None

    def prepare_features(self, df_scored: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for ML from scored dataset.

        Drops composite scores to avoid leakage, converts price to numeric,
        and one-hot encodes categorical variables.

        Parameters
        ----------
        df_scored : pd.DataFrame
            Scored dataframe from calculate_sustainability_score().

        Returns
        -------
        pd.DataFrame
            ML-ready dataframe with encoded features.
        """
        df_ml = df_scored.copy()

        # Convert price to numeric (handle both object and StringDtype in pandas 3.0+)
        if not pd.api.types.is_numeric_dtype(df_ml["Price"]):
            df_ml["Price"] = (
                df_ml["Price"].astype(str)
                .str.replace("€", "", regex=False)
                .str.strip()
            )
            df_ml["Price"] = pd.to_numeric(df_ml["Price"], errors="coerce")

        # Drop columns that would cause leakage or aren't useful
        cols_to_drop = [
            "Id",
            "Product_Name",
            "Score_100",
            "S_final",
            "S_env",
            "Score_env_burden",
        ]
        df_ml = df_ml.drop(columns=[c for c in cols_to_drop if c in df_ml.columns])

        # One-hot encode categorical columns
        categorical_cols = ["Brand", "Category", "Subcategory"]
        categorical_cols = [c for c in categorical_cols if c in df_ml.columns]

        if categorical_cols:
            df_ml = pd.get_dummies(df_ml, columns=categorical_cols, drop_first=True)

        return df_ml

    def train(
        self,
        df_ml: pd.DataFrame,
        target_col: str = "Price",
        test_size: float = 0.2,
        tune_hyperparameters: bool = False,
        **model_params,
    ) -> dict:
        """
        Train the price prediction model.

        Parameters
        ----------
        df_ml : pd.DataFrame
            ML-ready dataframe from prepare_features().
        target_col : str
            Name of the target column.
        test_size : float
            Proportion of data to use for testing.
        tune_hyperparameters : bool
            Whether to perform hyperparameter tuning (Random Forest only).
        **model_params
            Additional parameters to pass to the model.

        Returns
        -------
        dict
            Dictionary with metrics: R2, MAE, RMSE.
        """
        y = df_ml[target_col]
        X = df_ml.drop(columns=[target_col])

        self.feature_names = list(X.columns)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        # Get default params and update with any provided
        params = self.DEFAULT_PARAMS[self.model_type].copy()
        params.update(model_params)

        if tune_hyperparameters and self.model_type == "random_forest":
            self.model = self._tune_random_forest(X_train, y_train)
        else:
            model_class = self.SUPPORTED_MODELS[self.model_type]
            self.model = model_class(**params)
            self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)

        self.metrics = {
            "R2": r2_score(y_test, y_pred),
            "MAE": mean_absolute_error(y_test, y_pred),
            "RMSE": np.sqrt(mean_squared_error(y_test, y_pred)),
        }

        return self.metrics

    def _tune_random_forest(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Tune Random Forest hyperparameters using RandomizedSearchCV."""
        param_dist = {
            "n_estimators": [300, 500, 800],
            "max_depth": [None, 10, 20, 30],
            "min_samples_leaf": [1, 3, 5],
            "max_features": ["sqrt", "log2", 0.7],
            "bootstrap": [True],
        }

        rf_base = RandomForestRegressor(random_state=42, n_jobs=-1)

        search = RandomizedSearchCV(
            estimator=rf_base,
            param_distributions=param_dist,
            n_iter=20,
            cv=5,
            scoring="r2",
            n_jobs=-1,
            random_state=42,
        )

        search.fit(X_train, y_train)
        return search.best_estimator_

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict prices for new data.

        Parameters
        ----------
        X : pd.DataFrame
            Feature dataframe (must have same columns as training data).

        Returns
        -------
        np.ndarray
            Predicted prices.
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        return self.model.predict(X)

    def get_feature_importance(self, top_n: int = 12) -> pd.Series:
        """
        Get feature importance scores.

        Parameters
        ----------
        top_n : int
            Number of top features to return.

        Returns
        -------
        pd.Series
            Feature importance scores, sorted descending.
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        importance = pd.Series(
            self.model.feature_importances_,
            index=self.feature_names,
        ).sort_values(ascending=False)

        return importance.head(top_n)
