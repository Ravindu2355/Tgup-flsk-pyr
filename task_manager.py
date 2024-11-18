import json
import os

# Path to the JSON file
TASKS_FILE = "tasks.json"

# Function to read tasks from the JSON file
def read_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as file:
            data = json.load(file)
            return data.get("tasks", [])
    else:
        return []  # Return an empty list if the file doesn't exist

# Function to write a new task to the JSON file
def write_task(chat_id, url):
    tasks = read_tasks()  # Read the current tasks
    new_task = {"chat_id": chat_id, "url": url}
    tasks.append(new_task)  # Add the new task to the list
    
    # Write the updated task list back to the JSON file
    with open(TASKS_FILE, "w") as file:
        json.dump({"tasks": tasks}, file, indent=4)

# Function to clear all tasks (optional)
def clear_tasks():
    with open(TASKS_FILE, "w") as file:
        json.dump({"tasks": []}, file, indent=4)
