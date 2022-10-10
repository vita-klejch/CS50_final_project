from app import app, db
from flask import render_template, session, redirect, flash, url_for, request
from helper import login_required
from app.forms import RegisterForm, LoginForm, newConnectionForm, NewNoticeForm, ChangeNoticeForm, ChangeTaskForm, NewItemForm
from app.models import User, TaskList, Task
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

      
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
        print(user)
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
    username = current_user.username
    return render_template('home.html', username=username)

@app.route('/about')    # TO DO
@login_required
def about():
    return render_template('about.html')

@app.route('/connect')
@login_required
def connect():
    # print('current user:', current_user.username, ', email:', current_user.email, ', IS connected:', current_user.is_connected)
    
    requests_recieved = current_user.requested.all()
    requests_sent = current_user.connectionRequests.all()
    connect_data = {}
    if current_user.is_connected:
        connect_data['is_connected'] = True
        connect_data['connected_with'] = User.query.get_or_404(current_user.connected_with).username
        # print('user is connected')
        return render_template('connect.html', connect_data=connect_data)
    else:
        connect_data['is_connected'] = False
        # print('user not connected')
    # print('obdrzene pozadavky: ')
    # print(requests_recieved)
    # print('odeslane pozadavky: ')
    # print(requests_sent)
    requests_recieved_data = []
    for single_request in requests_recieved:
        sub_data = {}
        sub_data['name'] = single_request.username
        sub_data['id'] = single_request.id
        requests_recieved_data.append(sub_data)
    # print('requests_recieved_data')
    # print(requests_recieved_data)

    requests_sent_data = []
    for single_request in requests_sent:
        sub_data = {}
        sub_data['name'] = single_request.username
        sub_data['id'] = single_request.id
        requests_sent_data.append(sub_data)
    # print('requests_sent_data')
    # print(requests_sent_data)
    # print(requests_sent)
    form = newConnectionForm()
    return render_template('connect.html', 
        requests_recieved_data=requests_recieved_data,
        requests_sent_data=requests_sent_data,
        newConnectionForm=form,
        connect_data=connect_data
        )

@app.route('/new_connection', methods=['POST'])
@login_required
def new_connection():
    email_to_connect = request.form['user_to_connect']
    user_to_connect = User.query.filter_by(email=email_to_connect).first()
    # print('current user: ', current_user)
    # print('user to connect: ', user_to_connect)
    if user_to_connect is None or current_user.id == user_to_connect.id:
        flash('Invalid e-mail.', 'danger')
        return redirect('/connect')

    # check if request wasnt already sent
    requests_sent = current_user.connectionRequests.all()
    if user_to_connect in requests_sent:
        flash('Request to this user was already sent.', 'danger')
        return redirect('/connect')

    # enter new reqeust into DB:
    user_to_connect.requested.append(current_user)
    db.session.commit()
    flash('Request to connect was sent.', 'primary')

    return redirect('/connect')

@app.route('/request/accept/<int:id>')
@login_required
def accept_request(id):
    print('accept STARTS NOW')
    request_to_accept = User.query.get_or_404(id)

    # chceck if request_to_reject exists in recieved requests
    requests_recieved = current_user.requested.all()
    print('requests_recieved')
    print(requests_recieved)
    if request_to_accept not in requests_recieved:
        flash('ERROR - this request do not exists.', 'danger')
        return redirect('/connect')

    # check if one of the users isn't alredy connected
    if current_user.is_connected or request_to_accept.is_connected:
        flash('One of the users is already connected. Unable to connect.', 'danger')
        return redirect('/connect')
            
    # ACCEPT request - REMOVE from 'requested DB'
    current_user.requested.remove(request_to_accept)

    # helper FCE
    # print('current user:', current_user.username, ', is_connected:', 
    #     current_user.is_connected, ', connected_with:', current_user.connected_with)
    current_user.is_connected = 1
    current_user.connected_with = request_to_accept.id
    request_to_accept.is_connected = 1
    request_to_accept.connected_with = current_user.id
    db.session.commit()
    # print('current user:', current_user.username, ', is_connected:', 
    #     current_user.is_connected, ', connected_with:', current_user.connected_with,
    #     'connected with user: ', request_to_accept.username, request_to_accept.id)

    flash('You are now connected with user '+ request_to_accept.username + '.', 'primary')
    return redirect('/connect')

@app.route('/delete_connection')
@login_required
def delete_connection():
    print('delete connection STARTS NOW')

    # chceck if connection exist
    if not current_user.is_connected:
        flash('ERROR - this user is not connected', 'danger')
        return redirect('/connect')

    connection_to_delete = User.query.get_or_404(current_user.connected_with)
    print('connection_to_delete')
    print(connection_to_delete)
              
    current_user.is_connected = 0
    current_user.connected_with = None
    connection_to_delete.is_connected = 0
    connection_to_delete.connected_with = None
    db.session.commit()
  
    flash('Connection with user '+ connection_to_delete.username + ' was deleted.', 'primary')
    return redirect('/connect')

@app.route('/request/reject/<int:id>')
@login_required
# function to reject recieved request to connect from USER with ID
def reject_request(id):
    request_to_reject = User.query.get_or_404(id)

    # chceck if request_to_reject exists in recieved requests
    requests_recieved = current_user.requested.all()
    # print('requests_recieved')
    # print(requests_recieved)
    if request_to_reject not in requests_recieved:
        flash('ERROR - this request do not exists.', 'danger')
        return redirect('/connect')
    
    # REJECT request - REMOVE from DB
    current_user.requested.remove(request_to_reject)
    db.session.commit()
    flash('Request to connect was rejected.', 'primary')
    return redirect('/connect')

@app.route('/request/delete/<int:id>')
@login_required
# function to delete request to USER with ID 
def delete_request(id):
    request_to_delete = User.query.get_or_404(id)

    # chceck if request_to_delete exists in sent requests
    requests_sent = current_user.connectionRequests.all()
    if request_to_delete not in requests_sent:
        flash('ERROR - this request do not exists.', 'danger')
        return redirect('/connect')
    
    # DELETE request from DB
    request_to_delete.requested.remove(current_user)
    db.session.commit()
    flash('Request to connect was deleted.', 'primary')
    return redirect('/connect')

@app.route('/notice_board')
@login_required
def notice_board():
    data = []
    id = current_user.get_id()
    tasklists = TaskList.query.filter_by(user_id=id)
    share_data = {}

    if current_user.is_connected:
        share_data['enable_sharing'] = True
        connection = User.query.get_or_404(current_user.connected_with)
        share_data['connection_name'] = connection.username
        share_data['connection_id'] = connection.id
        share_data['data'] = []
        shared_tasklists = TaskList.query.filter_by(user_id=connection.id)
        
        for list in shared_tasklists:
            # print(list.text)
            if list.is_shared:                
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
                share_data['data'].append(sub_data)

    else:
        share_data['enable_sharing'] = False
        # print('NOT connected')
    # print(share_data)

    # format DATA
    for list in tasklists:
        sub_data = {}
        sub_tasks = []
        sub_data["tasklist_text"] = list.text
        sub_data["tasklist_id"] = list.id
        sub_data["is_shared"] = list.is_shared

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
    createNoticeForm=createNoticeForm, createTaskForm=createTaskForm, 
    changeTaskForm=changeTaskForm, share_data=share_data)

# ADD new notice in Notice Board
# NO NEED to check if action is valid for current user
@app.route('/notice/add', methods=['POST'])
def add_notice():      
    new_text = request.form['text']
    new_task = TaskList(text=new_text, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return redirect('/notice_board')

# TOGGLE share setting
@app.route('/notice/toggle_share/<int:id>')
def toggle_share(id):
    tasklist = TaskList.query.get_or_404(id)

    # check if this action is valid for current user 
    # only OWNER of Tasklist can enable/disable sharing
    if tasklist.owner.id != current_user.id:
        flash('Invalid action for this user', 'danger')
        return redirect('/notice_board')

    # toggle sharing
    if tasklist.is_shared:
        tasklist.is_shared = 0
    else:
        tasklist.is_shared = 1
    
    db.session.commit()
    return redirect('/notice_board')

# create new task in Notice with some ID
@app.route('/task/add/<int:id>', methods=['POST'])
def add_item(id):
    tasklist = TaskList.query.get_or_404(id)

    # check if this action is valid for current user 
    # TASK can be added by OWNER and CONNECTION if  TASKLIST is SHARED
    control_rights = [tasklist.owner.id]
    if tasklist.is_shared:
        control_rights.append(tasklist.owner.connected_with)

    if current_user.id not in control_rights:
        flash('Invalid action for this user', 'danger')
        return redirect('/notice_board')

    new_text = request.form['text']
    new_item = Task(text=new_text, tasklist_id=id, user_id=tasklist.owner.id)
    db.session.add(new_item)
    db.session.commit()
    return redirect('/notice_board')
        
@app.route('/notice/update/<int:id>', methods=['POST'])
def update_notice(id):
    notice_to_update = TaskList.query.get_or_404(id)
    
    # check if this action is valid for current user 
    # NOTICE can be updated only by OWNER 
    if current_user.id != notice_to_update.owner.id:
        flash('Invalid action for this user', 'danger')
        return redirect('/notice_board')
        
    new_text = request.form['text']
    notice_to_update.text = new_text
    db.session.commit()
    return redirect('/notice_board')

@app.route('/task/update/<int:id>', methods=['POST'])
def update_task(id):
    task_to_update = Task.query.get_or_404(id)

    # check if this action is valid for current user 
    # TASK can be updated by OWNER and CONNECTION if it is SHARED
    control_rights = [task_to_update.owner.id]
    if task_to_update.tasks_tasklist.is_shared:
        control_rights.append(task_to_update.tasks_tasklist.owner.connected_with)

    if current_user.id not in control_rights:
        flash('Invalid action for this user', 'danger')
        return redirect('/notice_board')

    new_text = request.form['text']
    task_to_update.text = new_text
    db.session.commit()
    return redirect('/notice_board')

@app.route('/notice/delete/<int:id>')
def delete_notice(id):
    notice_to_delete = TaskList.query.get_or_404(id)

    # check if this action is valid for current user
    # NOTICE can be deleted ONLY by OWNER
    if notice_to_delete.owner.id != current_user.id:
        flash('Invalid action for this user', 'danger')
        return redirect('/notice_board')

    # delete all task from this Notice
    tasks_to_delete = Task.query.filter_by(tasklist_id=id)
    for task in tasks_to_delete:
        db.session.delete(task)
    
    # delete Notice
    db.session.delete(notice_to_delete)
    db.session.commit()
    return redirect('/notice_board')

@app.route('/task/delete/<int:id>')
def delete_task(id):    
    task_to_delete = Task.query.get_or_404(id)

    # check if this action is valid for current user 
    # TASK can be deleted by OWNER and CONNECTION if it is SHARED
    control_rights = [task_to_delete.owner.id]
    if task_to_delete.tasks_tasklist.is_shared:
        control_rights.append(task_to_delete.owner.connected_with)

    if current_user.id not in control_rights:
        flash('Invalid action for this user', 'danger')
        return redirect('/notice_board')

    # DELETE task and commit
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect('/notice_board')





