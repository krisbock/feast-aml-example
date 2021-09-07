from feast import Entity, Feature, FeatureView, ValueType
from feast import FeatureStore, RepoConfig
from feast.data_source import SqlServerSource
from feast.repo_config import SqlServerOfflineStoreConfig, RedisOnlineStoreConfig
from datetime import datetime, timedelta
import os
import logging
import json
import numpy
import joblib


def init():
    global store

    connection_string = os.getenv("FEAST_HIST_CONN")
    redis_endpoint = os.getenv("FEAST_REDIS_CONN")
    feast_registry = os.getenv("FEAST_REGISTRY_BLOB")

    repo_cfg = RepoConfig(
        project="production",
        provider="local",
        registry=feast_registry,
        offline_store=SqlServerOfflineStoreConfig(connection_string=connection_string),
        online_store=RedisOnlineStoreConfig(connection_string=redis_endpoint),
    )

    store = FeatureStore(config=repo_cfg)

    global model
    # AZUREML_MODEL_DIR is an environment variable created during deployment.
    # It is the path to the model folder (./azureml-models/$MODEL_NAME/$VERSION)
    model_path = os.path.join(os.getenv("AZUREML_MODEL_DIR"), "model/model.pkl")
    # deserialize the model file back into a sklearn model
    model = joblib.load(model_path)
    logging.info("Init complete")


def run(raw_data):
    j = json.loads(raw_data)

    feature_vector = store.get_online_features(
        feature_refs=[
            "driver_stats:conv_rate",
            "driver_stats:avg_daily_trips",
            "driver_stats:acc_rate",
            "customer_profile:current_balance",
            "customer_profile:avg_passenger_count",
            "customer_profile:lifetime_trip_count",
        ],
        entity_rows=[{"driver": j["driver"], "customer_id": j["customer_id"]}],
    ).to_df()
    if len(feature_vector.dropna()) > 0:
        data = feature_vector[
            [
                "driver_stats__conv_rate",
                "driver_stats__avg_daily_trips",
                "driver_stats__acc_rate",
                "customer_profile__current_balance",
                "customer_profile__avg_passenger_count",
                "customer_profile__lifetime_trip_count",
            ]
        ]

        y_hat = model.predict(data)
        return y_hat.tolist()
    else:
        return 0

