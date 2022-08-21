from app import app, db
from app.models import User, TaskList, Task

@app.shell_context_processor
def make_shell_context():
    # return {'db': db, 'User': User}
    # return {'db': db, 'User': User, 'TaskList': TaskList}
    return {'db': db, 'User': User, 'TaskList': TaskList, 'Task': Task}