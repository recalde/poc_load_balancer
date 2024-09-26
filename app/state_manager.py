import os
import json
import boto3

class LocalFileStateManager:
    def __init__(self):
        self.cluster_dir = "mnt/cluster/"
        self.requests_dir = "mnt/requests/"

    def save_cluster_state(self, cluster_name, calculation_id, file_size):
        """
        Save the state of a cluster for in-progress calculations.
        """
        with open(f"{self.cluster_dir}{cluster_name}.json", 'a') as f:
            f.write(json.dumps({"calculationId": calculation_id, "fileSize": file_size}))

    def save_calculation_state(self, calculation_id, state_data):
        """
        Save state for a specific calculation (calculationId).
        """
        with open(f"{self.requests_dir}{calculation_id}.json", 'w') as f:
            f.write(json.dumps(state_data))

    def get_cluster_state(self, cluster_name):
        """
        Retrieve the current state for a specific cluster.
        """
        try:
            with open(f"{self.cluster_dir}{cluster_name}.json", 'r') as f:
                return json.loads(f.read())
        except FileNotFoundError:
            return []

    def get_calculation_state(self, calculation_id):
        """
        Retrieve the state for a specific calculation (calculationId).
        """
        try:
            with open(f"{self.requests_dir}{calculation_id}.json", 'r') as f:
                return json.loads(f.read())
        except FileNotFoundError:
            return None


class DynamoDbStateManager:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.cluster_table = os.getenv("DYNAMODB_CLUSTER_TABLE", "Cluster_State")
        self.request_table = os.getenv("DYNAMODB_REQUEST_TABLE", "Calculation_Request")

    def save_cluster_state(self, cluster_name, calculation_id, file_size):
        """
        Save the cluster state in DynamoDB.
        """
        table = self.dynamodb.Table(self.cluster_table)
        table.put_item(Item={
            'ClusterName': cluster_name,
            'CalculationId': calculation_id,
            'FileSize': file_size
        })

    def save_calculation_state(self, calculation_id, state_data):
        """
        Save the calculation state in DynamoDB.
        """
        table = self.dynamodb.Table(self.request_table)
        table.put_item(Item={
            'CalculationId': calculation_id,
            **state_data
        })

    def get_cluster_state(self, cluster_name):
        """
        Retrieve the cluster state from DynamoDB.
        """
        table = self.dynamodb.Table(self.cluster_table)
        response = table.get_item(Key={'ClusterName': cluster_name})
        return response.get('Item', [])

    def get_calculation_state(self, calculation_id):
        """
        Retrieve the calculation state from DynamoDB.
        """
        table = self.dynamodb.Table(self.request_table)
        response = table.get_item(Key={'CalculationId': calculation_id})
        return response.get('Item')
