import requests
import time

def paulAPI(data: str) -> str:
    url = "http://paulchen.bio:8000/process/"

    data = {
        "data": data
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        task_id = response.json()["task_id"]

        # Poll the task status using the task_id
        task_url = f"http://paulchen.bio:8000/task/{task_id}"
        while True:
            task_response = requests.get(task_url)

            if task_response.status_code == 200:
                task_data = task_response.json()
                if task_data["status"] == "completed":
                    return task_data["result"]
                elif "error" in task_data:
                    return f"Task failed with error: {task_data['error']}"
            else:
                return f"Task status request failed with status code: {task_response.status_code}"

            time.sleep(0.1)  # Adjust the sleep interval as needed
    else:
        return f"Request failed with status code: {response.status_code}"