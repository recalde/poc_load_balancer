from fastapi import FastAPI, Request, HTTPException
import aiohttp
from .config import Config
from .s3_helper import get_file_size
from .state_manager import LocalFileStateManager, DynamoDbStateManager

app = FastAPI()

# Choose state manager based on configuration
if Config.STATE_TYPE == 'LocalFile':
    state_manager = LocalFileStateManager()
else:
    state_manager = DynamoDbStateManager()

# Helper function to select a cluster based on the thresholds and load
def select_cluster(file_size):
    """
    Logic to select a cluster based on thresholds and load from the configured clusters.
    """
    for cluster_name, cluster_info in Config.CLUSTER_CONFIG.items():
        cluster_url = cluster_info.get("url")
        max_capacity = cluster_info.get("max_capacity", Config.DEFAULT_CALCULATION_THRESHOLD)
        max_file_size = cluster_info.get("max_file_size", Config.DEFAULT_MAX_FILE_SIZE)

        # Fetch current cluster state
        cluster_state = state_manager.get_cluster_state(cluster_name)

        # Check if the cluster has capacity and the file size is acceptable
        if len(cluster_state) < max_capacity and file_size < max_file_size:
            return cluster_name, cluster_url

    # If no clusters are available, raise an exception
    raise HTTPException(status_code=503, detail="All clusters are at capacity or file size exceeds limits")

@app.post("/calculate")
async def calculate(request: Request):
    # Parse the request body for inputFile and callback
    body = await request.body()
    body_text = body.decode('utf-8')

    # Extract inputFile and callback from the body
    try:
        input_file = body_text.split('input=')[1].split('\r\n')[0]
        callback_url = body_text.split('callback=')[1]
    except IndexError:
        raise HTTPException(status_code=400, detail="Invalid request body format")

    # Extract query parameters
    query_params = dict(request.query_params)
    calculation_id = query_params.get('calculationId')

    # Get file size from S3 bucket
    file_size = get_file_size(Config.S3_BUCKET, input_file)

    # Select an appropriate cluster
    selected_cluster, selected_cluster_url = select_cluster(file_size)

    # Rewriting the callback URL to the load balancer's callback API
    modified_body = body_text.replace(callback_url, f"{Config.CALLBACK_URL}/callback")

    # Save the state of the calculation
    state_data = {
        "calculationId": calculation_id,
        "fileSize": file_size,
        "cluster": selected_cluster,
        "callbackUrl": callback_url,
        "queryParams": query_params
    }
    state_manager.save_calculation_state(calculation_id, state_data)
    state_manager.save_cluster_state(selected_cluster, calculation_id, file_size)

    # Forward the request to the selected cluster
    async with aiohttp.ClientSession() as session:
        try:
            response = await session.post(f"{selected_cluster_url}/calculate", data=modified_body, params=query_params)
            response.raise_for_status()
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=500, detail=f"Error forwarding request to {selected_cluster}: {str(e)}")

    return {"status": "calculation started", "cluster": selected_cluster}


@app.post("/callback")
async def callback(request: Request):
    # Parse the callback request body
    callback_body = await request.json()

    # Extract the calculationId from the callback body
    calculation_id = callback_body.get('CalculationId')
    if not calculation_id:
        raise HTTPException(status_code=400, detail="CalculationId is missing in the callback payload")

    # Retrieve the state for the calculationId
    state_data = state_manager.get_calculation_state(calculation_id)
    if not state_data:
        raise HTTPException(status_code=404, detail="CalculationId not found in state")

    original_callback_url = state_data.get('callbackUrl')

    # Forward the callback response to the original callback URL
    async with aiohttp.ClientSession() as session:
        try:
            response = await session.post(original_callback_url, json=callback_body)
            response.raise_for_status()
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=500, detail=f"Error forwarding callback: {str(e)}")

    return {"status": "callback forwarded", "originalCallbackUrl": original_callback_url}
