from flask import Flask, render_template, request, redirect, url_for
import json
import os
import uuid

app = Flask(__name__)
TASKS_FILE = 'tasks.json'

# Ensure JSON file exists
if not os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, 'w') as f:
        json.dump([], f)

# Load tasks into JSON file
def load_tasks():
    with open(TASKS_FILE, 'r') as f:
        return json.load(f)

# Save tasks into JSON file
def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)
        
# Add fixed categories
CATEGORIES = ["Work", "Personal", "Groceries", "Event"]

@app.route('/', methods=["GET"])
def index():
    tasks = load_tasks()
    sort_by = request.args.get("sort_by")
    
    if sort_by == "priority":
        priority_order = {"High": 1, "Medium": 2, "Low": 3}
        tasks.sort(key=lambda x: priority_order.get(x["priority"], 4))
    elif sort_by == "due_date":
        tasks.sort(key=lambda x: x["due_date"])        
    elif sort_by == "category":
        tasks.sort(key=lambda x: x.get("category","").lower())
    return render_template("index.html", tasks=tasks, categories=CATEGORIES, sort_by=sort_by)

@app.route('/add', methods=['POST'])
def add():
    tasks = load_tasks()  
    new_task = {
        "id": str(uuid.uuid4()),
        "title": request.form["title"],
        "due_date": request.form["due_date"],
        "priority": request.form["priority"],
        "category": request.form.get('category'),
        'completed': False
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return redirect(url_for("index"))

@app.route('/delete/<task_id>')
def delete(task_id):
    tasks = load_tasks()
    tasks = [task for task in tasks if task["id"] != task_id]
    save_tasks(tasks)
    return redirect(url_for("index"))

@app.route('/edit/<task_id>', methods=['POST'])
def edit(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = request.form["title"]
            task["due_date"] = request.form["due_date"]
            task["priority"] = request.form["priority"]
            task["category"] = request.form.get("category","").strip()
            task["completed"] = 'completed' in request.form
            break
    save_tasks(tasks)
    sort_by = request.form.get("sort_by","")
    return redirect(url_for("index", sort_by=sort_by))


#refresh the app automatically
if __name__ == '__main__':
    app.run(debug=True)
