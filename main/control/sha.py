# coding: utf-8

import json
from google.appengine.ext import ndb
import flask
import flask_wtf
import wtforms

import auth
import config
import model
import util

from main import app


###############################################################################
# Update
###############################################################################
class DrawingUpdateForm(flask_wtf.FlaskForm):
  json = wtforms.TextAreaField(
    model.Drawing.json._verbose_name,
    [wtforms.validators.required()],
    filters=[util.strip_filter],
  )


@app.route('/<drawing_hash>/', methods=['GET', 'POST'])
def drawing_hash(drawing_hash):
  drawing_db = model.Drawing.get_by('hash', drawing_hash)
  if drawing_db:
    flask.abort(403)
  drawing_db = model.Drawing(hash=drawing_hash)
  form = DrawingUpdateForm(obj=drawing_db)
  if form.validate_on_submit():
    try:
      form.json.data = json.loads(form.json.data)
      form.populate_obj(drawing_db)
      drawing_db.put()
      return flask.redirect(flask.url_for('welcome'))
    except ValueError:
      form.json.errors.append('Not a valid JSON')

  return flask.render_template(
    'drawing/drawing_create.html',
    title='New Drawing',
    html_class='drawing-create',
    form=form,
    drawing_db=drawing_db,
  )
