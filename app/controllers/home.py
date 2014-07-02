import uuid

from flask import render_template, redirect, url_for, g, flash
from flask.ext.classy import FlaskView, route
from flask.ext.mail import Message

import settings
from app import db, tasks, mail
from app.forms import DeployServerForm, ContactForm
from app.forms import duration_choices
from app.models import Server
import app.murmur as murmur


## Home views
class HomeView(FlaskView):
    @route('/', endpoint='home')
    def index(self):
        user = g.user
        form = DeployServerForm()
        form.duration.choices = duration_choices()
        return render_template('index.html', form=form)

    def post(self):
        form = DeployServerForm()
        if form.validate_on_submit():

            try:
                # Generate UUID
                gen_uuid = str(uuid.uuid4())

                # Create POST request to murmur-rest api to create a new server
                welcome_msg = "Welcome. This is a temporary GuildBit Mumble instance. View details on this server by " \
                              "<a href='http://guildbit.com/server/%s'>clicking here.</a>" % gen_uuid
                payload = {
                    'password': form.password.data,
                    'welcometext': welcome_msg,
                    'users': settings.DEFAULT_MAX_USERS,
                    'registername': settings.DEFAULT_CHANNEL_NAME
                }

                server_id = murmur.create_server_by_location(form.location.data, payload)

                # Create database entry
                s = Server()
                s.duration = form.duration.data
                s.password = form.password.data
                s.uuid = gen_uuid
                s.mumble_instance = server_id
                s.mumble_host = murmur.get_murmur_hostname(form.location.data)
                db.session.add(s)
                db.session.commit()

                # Send task to delete server on expiration
                tasks.delete_server.apply_async([gen_uuid], eta=s.expiration)
                return redirect(url_for('ServerView:get', id=s.uuid))

            except:
                import traceback

                db.session.rollback()
                traceback.print_exc()

            return render_template('index.html', form=form)
        return render_template('index.html', form=form)

    @route('/how-it-works/')
    def how_it_works(self):
        return render_template('how_it_works.html')

    @route('/donate/')
    def donate(self):
        return render_template('donate.html')

    @route('/upgrade')
    def upgrade(self):
        return render_template('upgrade.html')

    @route('/contact/', methods=['POST', 'GET'])
    def contact(self):
        form = ContactForm()
        if form.validate_on_submit():
            try:
                template = """
                              This is a contact form submission from Guildbit.com/contact \n
                              Email: %s \n
                              Comment/Question: %s \n
                           """ % (form.email.data, form.message.data)

                msg = Message(
                    form.subject.data,
                    sender=settings.DEFAULT_MAIL_SENDER,
                    recipients=settings.EMAIL_RECIPIENTS)

                msg.body = template
                mail.send(msg)
            except:
                import traceback

                traceback.print_exc()
                flash("Something went wrong!")
                return redirect('/contact')

            return render_template('contact_thankyou.html')
        return render_template('contact.html', form=form)

    @route('/about/')
    def about(self):
        return render_template('about.html')

    @route('/terms/')
    def terms(self):
        return render_template('terms.html')

    @route('/privacy/')
    def privacy(self):
        return render_template('privacy.html')

    @route('/updates/')
    def updates(self):
        return render_template('updates.html')
