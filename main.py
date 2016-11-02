#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import SolitaireAPI
from models import User
from models import Game


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email and unfinisehd games
           about games. Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None).fetch()
        have_incomplete_game = False
        for user in users:
            active_games = Game.query(ancestor=user.key).filter(Game.game_over==False).fetch()

            if active_games:
                subject = 'This is a reminder!'
                body = 'Hello {}, try out Solitaire Game!'.format(user.user_name)
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail)
], debug=True)
