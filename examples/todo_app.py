"""
Example Flask application demonstrating NewUI features
"""

from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from newui import NewUI

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ui = NewUI(app)

# Models
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
@ui.reactive
def index():
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return render_template('index.html', todos=todos)

@app.route('/todos', methods=['POST'])
def create_todo():
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
        title = data.get('title', '')
    else:
        title = request.form.get('title', '')
    
    todo = Todo(title=title)
    db.session.add(todo)
    db.session.commit()
    
    # Return partial update
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return ui.ajax.component_response('todo_list_with_stats', todos=todos)

@app.route('/todos/<int:id>/toggle', methods=['POST'])
def toggle_todo(id):
    todo = Todo.query.get_or_404(id)
    todo.completed = not todo.completed
    db.session.commit()
    
    # Return partial update
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return ui.ajax.component_response('todo_list_with_stats', todos=todos)

@app.route('/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    
    # Return partial update
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return ui.ajax.component_response('todo_list_with_stats', todos=todos)

# Remove the custom component registration - we'll use a template instead

if __name__ == '__main__':
    app.run(debug=True)