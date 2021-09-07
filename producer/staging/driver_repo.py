from feast import Entity, Feature, FeatureView, ValueType
from feast.data_source import SqlServerSource
from datetime import timedelta

orders_table = "orders"
driver_hourly_table = "driver_hourly"
customer_profile_table = "customer_profile"

driver_source = SqlServerSource(
    table_ref=driver_hourly_table,
    event_timestamp_column="datetime",
    created_timestamp_column="created",
)

customer_source = SqlServerSource(
    table_ref=customer_profile_table,
    event_timestamp_column="datetime",
    created_timestamp_column="",
)

driver_fv = FeatureView(
    name="driver_stats",
    entities=["driver"],
    features=[
        Feature(name="conv_rate", dtype=ValueType.FLOAT),
        Feature(name="acc_rate", dtype=ValueType.FLOAT),
        Feature(name="avg_daily_trips", dtype=ValueType.INT32),
    ],
    input=driver_source,
    ttl=timedelta(hours=2),
)

customer_fv = FeatureView(
    name="customer_profile",
    entities=["customer_id"],
    features=[
        Feature(name="current_balance", dtype=ValueType.FLOAT),
        Feature(name="avg_passenger_count", dtype=ValueType.FLOAT),
        Feature(name="lifetime_trip_count", dtype=ValueType.INT32),
    ],
    input=customer_source,
    ttl=timedelta(days=2),
)

driver = Entity(name="driver", join_key="driver_id", value_type=ValueType.INT64)
customer = Entity(name="customer_id", value_type=ValueType.INT64)
