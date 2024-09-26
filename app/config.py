import os
import json

class Config:
    # Fetch cluster config from ENV (as JSON string).
    # Example ENV: {"gp-6-prod": {"url": "http://gp-6-prod", "max_capacity": 100, "max_file_size": 104857600}}
    CLUSTER_CONFIG = json.loads(os.getenv("CLUSTER_CONFIG", '{}'))

    # Default thresholds for calculation capacity and file size
    DEFAULT_CALCULATION_THRESHOLD = int(os.getenv("DEFAULT_CALCULATION_THRESHOLD", "10"))
    DEFAULT_MAX_FILE_SIZE = int(os.getenv("DEFAULT_MAX_FILE_SIZE", "104857600"))  # 100MB

    # State management configuration (either "LocalFile" or "DynamoDb")
    STATE_TYPE = os.getenv("STATE_TYPE", "LocalFile")

    # S3 configuration for bucket name
    S3_BUCKET = os.getenv("S3_BUCKET")

    # Load balancer callback URL
    CALLBACK_URL = os.getenv("CALLBACK_URL")
