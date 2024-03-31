from modules import app
from modules.models import db, User
from flask import render_template, url_for, request, redirect, session, flash, get_flashed_messages


@app.route('/user_management', methods=['GET', 'POST'])
def user_management():
    if 'username' in session:
        if User.query.filter_by(username=session['username']).first().role == 'Admin':
            # The following code is for pagination to display 10 users per page
            page = request.args.get('page', 1, type=int)
            # users = User.query.all()
            users = User.query.paginate(page=page, per_page=10, error_out=False)

            if request.method == 'POST':
                search = request.form.get('search')
                if search:
                    search_result = User.query.filter(User.username.like('%' + search + '%')).all()
                    return render_template('user_management.html', users=search_result)

            msg = get_flashed_messages()
            return render_template('user_management.html', users=users, msg=msg)
        else:
            flash('You are not authorized to access this page')
            return redirect(url_for('event'))

    return redirect(url_for('signin'))

    
@app.route('/delete_user', methods=['POST'])
def delete_user():
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    if user.username == session['username']:
        flash('You cannot delete yourself')
        return redirect(url_for('user_management'))

    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully')
    else:
        flash('User not found')
    return redirect(url_for('user_management'))

    
@app.route('/change_role', methods=['POST'])
def change_role():
    username = request.form.get('username')
    new_role = request.form.get('role')

    user = User.query.filter_by(username=username).first()
    if user is None:
        return {"error": "User not found"}, 404

    user.role = new_role
    db.session.commit()

    flash('Role changed successfully')
    return redirect(url_for('user_management'))