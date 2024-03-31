from modules import app
from .models import db, Event, Registration
from flask import render_template, url_for, request, redirect, session, flash, get_flashed_messages

from datetime import datetime


@app.route('/event', methods=["GET", "POST"])
def event():
    # events = Event.query.filter(Event.date >= datetime.utcnow()).all()
    events = Event.query.all()
    msg = get_flashed_messages()
    return render_template('event.html', msg=msg, events=events)

    
@app.route('/details/<int:event_id>', methods=['GET', 'POST'])
def details(event_id):
    event = Event.query.get(event_id)
    # event = Event.query.filter_by(id=event_id).first()
    if event is None:
        flash('Event not found.')
        return redirect(url_for('home'))
    return render_template('details.html', event=event)

    
@app.route('/event/register', methods=["GET", "POST"])
def register():
    if 'username' in session:
        if request.method == "POST":
            event_id = request.form.get('event_id')
            user_id = session['username']
            if Registration.query.filter_by(user_id=user_id, event_id=event_id).first():
                flash("You have already registered for this event")
                return redirect(url_for('event'))
            registration = Registration(user_id=user_id, event_id=event_id)
            db.session.add(registration)
            db.session.commit()
            flash("You have successfully registered for the event")
            return redirect(url_for('event'))
    return redirect(url_for('signin'))


@app.route('/event/create', methods=['GET', 'POST'])
def create_event():
    if 'username' in session:
        if session['role'] == 'Admin' or session['role'] == 'Co-Admin':
            if request.method == 'POST':
                title = request.form.get('title')
                description = request.form.get('description')
                date = request.form.get('date')
                date = datetime.strptime(date, '%Y-%m-%d').date()
                location = request.form.get('location')
                creator_id = session['username']
                organizer_name = request.form.get("organizer_name")

                event = Event(title=title, description=description, date=date, location=location, creator_id=creator_id)
                db.session.add(event)
                db.session.commit()

                flash('Event created successfully')
                return redirect(url_for('event'))

            return render_template('create_event.html')
        else:
            flash('You are not authorized to access this page')
            return redirect(url_for('event'))

    return redirect(url_for('signin'))

    
@app.route('/event_manager', methods=['GET', 'POST'])
def event_manager():
    page = request.args.get('page', 1, type=int)
    reg = Registration.query.paginate(page=page, per_page=10, error_out=False)
    total_result = Registration.query.count()
    if request.method == 'POST':
        search = request.form.get('search')
        if search:
            search_result = Event.query.filter(Event.title == search).first()
            if search_result:
                search_result = Registration.query.filter(Registration.event_id == search_result.id).all()
                total_result = len(search_result)
             
                return render_template('event_manager.html', events=search_result, total_result=total_result)
            else:
                flash('No results found')
        else:
            flash('Please enter a search term')

    msg = get_flashed_messages()
    return render_template('event_manager.html', events=reg, msg=msg, total_result=total_result)