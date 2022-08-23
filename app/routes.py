from app import app, db
from flask import render_template, session, redirect, flash, url_for, request
from helper import login_required
from app.forms import RegisterForm, LoginForm, ConnectForm, NewNoticeForm, ChangeNoticeForm, ChangeTaskForm, NewItemForm
from app.models import User, TaskList, Task
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

def IDhelper(id1, id2):
    if int(id1) == int(id2):
        print('externi kontrola OK')
        return
    flash('chyba, ID nejsou stejna', 'danger')
    print('kontrola NENI ok')
    return redirect('/home')

       
@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template("index.html")

@app.route('/link')
@login_required
def link():
    return render_template('link.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        flash('User logged in', 'success')
        return redirect(next_page)
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('User logged out', 'primary')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration was successful. Now you can log in.', 'success')
        return redirect('login')
    return render_template('register.html', form=form)

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/about')    # TO DO
@login_required
def about():
    return render_template('about.html')

@app.route('/connect')  # TO DO
@login_required
def connect():
    return render_template('connect.html')

@app.route('/notice_board')
@login_required
def notice_board():
    data = []
    id = current_user.get_id()
    tasklists = TaskList.query.filter_by(user_id=id)
    # format DATA
    for list in tasklists:
        sub_data = {}
        sub_tasks = []
        sub_data["tasklist_text"] = list.text
        sub_data["tasklist_id"] = list.id
        tasks = Task.query.filter_by(tasklist_id=list.id)
        for task in tasks:            
            sub_task = {}
            sub_task['text'] = task.text
            sub_task['id'] = task.id
            sub_tasks.append(sub_task)
        
        sub_data["tasks"] = sub_tasks
        data.append(sub_data)

    # inicialize FORMS
    changeNoticeForm = ChangeNoticeForm()
    createNoticeForm = NewNoticeForm()
    createTaskForm = NewItemForm()
    changeTaskForm = ChangeTaskForm()
    return render_template('notice_board.html', data=data, changeNoticeForm=changeNoticeForm, 
    createNoticeForm=createNoticeForm, createTaskForm=createTaskForm, changeTaskForm=changeTaskForm)

@app.route('/notice/add', methods=['POST'])
def add_notice():
    # if request.method == 'POST':
        id = current_user.get_id()        
        new_text = request.form['text']
        new_task = TaskList(text=new_text, user_id=id)
        db.session.add(new_task)
        db.session.commit()
        return redirect('/notice_board')
    # else:
    #     form = NewNoticeForm()
    #     return render_template('add_notice.html', form=form)

@app.route('/task/add/<int:id>', methods=['POST'])
def add_item(id):
    # if request.method == 'POST':
        user_id = current_user.get_id()
        new_text = request.form['text']
        new_item = Task(text=new_text, tasklist_id=id, user_id=user_id)
        db.session.add(new_item)
        db.session.commit()
        return redirect('/notice_board')
    # else:
    #     form = NewItemForm()
    #     return render_template('add_item.html', form=form)
        
@app.route('/notice/update/<int:id>', methods=['POST'])
def update_notice(id):
    # if request.method == 'POST':
        notice_to_update = TaskList.query.get_or_404(id)
        user_id = current_user.get_id()
        # print('owner of the notice:', notice_to_update.owner.id, type(notice_to_update.owner.id))
        # print('active USER:', user_id, type(user_id))
        if int(notice_to_update.owner.id) != int(user_id):
            flash('Invalid action for this user', 'danger')
            return redirect('/home')
        new_text = request.form['text']
        notice_to_update.text = new_text
        db.session.commit()
        return redirect('/notice_board')
    # else:         # I DONT NEED THIS BECAUSE I AM USING MODAL TO CONTROL THIS ACTION
    #     task = TaskList.query.get_or_404(id)
    #     if task.owner.id != int(current_user.get_id()):
    #         flash('Invalid action for this user', 'danger')
    #         return redirect('/home')
    #     form = ChangeNoticeForm()
    #     return render_template('update_notice.html', form=form, old_text=task.text)

@app.route('/task/update/<int:id>', methods=['POST'])
def update_task(id):
    # if request.method == 'POST':
        task_to_update = Task.query.get_or_404(id)
        if int(task_to_update.owner.id) != int(current_user.get_id()):
            flash('Invalid action for this user', 'danger')
            return redirect('/home')
        new_text = request.form['text']
        task_to_update.text = new_text
        db.session.commit()
        return redirect('/notice_board')
    # else:         # I DONT NEED THIS BECAUSE I AM USING MODAL TO CONTROL THIS ACTION
    #     task = Task.query.get_or_404(id)
    #     if task.owner.id != int(current_user.get_id()):
    #         flash('Invalid action for this user', 'danger')
    #         return redirect('/home')
    #     form = ChangeTaskForm()
    #     return render_template('update_task.html', form=form, old_text=task.text)

@app.route('/notice/delete/<int:id>')
def delete_notice(id):
    notice_to_delete = TaskList.query.get_or_404(id)
    if int(notice_to_delete.owner.id) != int(current_user.get_id()):
        flash('Invalid action for this user', 'danger')
        return redirect('/home')

    db.session.delete(notice_to_delete)
    db.session.commit()
    return redirect('/notice_board')

@app.route('/task/delete/<int:id>')
def delete_task(id):    
    task_to_delete = Task.query.get_or_404(id)
    if int(task_to_delete.owner.id) != int(current_user.get_id()):
        flash('Invalid action for this user', 'danger')
        return redirect('/home')

    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect('/notice_board')

@app.route('/new_connection', methods=['GET', 'POST'])
@login_required
def new_connection():
    form = ConnectForm()
    return render_template('new_connection.html', form=form)



