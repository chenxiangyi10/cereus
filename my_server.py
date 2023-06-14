import logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from celery import Celery
from pydantic import BaseModel
import aiohttp
from typing import Dict, List, Union, Any

# Configure logging to log to a file named "app.log"
logging.basicConfig(filename="app.log",
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

celery_app = Celery("worker", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1")

templates = Jinja2Templates(directory="templates")

class DataRequest(BaseModel):
    data: str
    outputSet: Dict[str, List[int]]

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, result: str = None):
    return templates.TemplateResponse("index.html", {"request": request, "result": result})

@app.post("/", response_class=HTMLResponse)
async def index_post(request: Request, input_text: str = Form(...)):
    api_url = "http://paulchen.bio:8000/process"
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json={"data": input_text, "outputSet": {}}) as response:
            if response.status == 200:
                json_response = await response.json()
                task_id = json_response.get("task_id")
            else:
                task_id = ""
    tasks_ahead = get_task_position_in_queue(task_id)
    return templates.TemplateResponse("index.html", {"request": request, "task_id": task_id, "tasks_ahead": tasks_ahead, "input_text": input_text})

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    if task.ready():
        result = task.result
        return {"status": "completed", "result": result, "state": task.state, "error": str(task.traceback)}
    else:
        return {"status": "processing", "state": task.state}

@app.post("/process/")
async def process_data(request: Request, data_request: DataRequest) -> Dict[str, Any]:
    # Log the incoming request
    logging.info(f"Received request: {await request.json()}")
    task = celery_app.send_task("worker.process_data_task", args=[data_request.data, data_request.outputSet])
    print(f"Task submitted with ID: {task.id}")
    return {"task_id": task.id}

@app.route('/task_queue_position/<task_id>', methods=['GET'])
def task_queue_position(task_id):
    task_position = get_task_position_in_queue(task_id)
    return jsonify(position=task_position)

def get_task_position_in_queue(task_id):
    i = celery_app.control.inspect()

    active_tasks = i.active() or {}
    scheduled_tasks = i.scheduled() or {}
    reserved_tasks = i.reserved() or {}
    
    print("Active tasks:", active_tasks)
    print("Scheduled tasks:", scheduled_tasks)
    print("Reserved tasks:", reserved_tasks)


    tasks = list(active_tasks.values()) + list(scheduled_tasks.values()) + list(reserved_tasks.values())
    # Find the position of the task in the task queue
    position = 0
    for task in tasks:
#        if task_dict['id'] == task_id:
#            break
        position += 1

    print(f"Task position: {position}")
    return position