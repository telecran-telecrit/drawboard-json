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

  hash = wtforms.StringField(
    model.Drawing.hash._verbose_name,
    [wtforms.validators.required(), wtforms.validators.length(max=500)],
    filters=[util.strip_filter],
  )
  json = wtforms.TextAreaField(
    model.Drawing.json._verbose_name,
    [wtforms.validators.required()],
    filters=[util.strip_filter],
  )


@app.route('/<drawing_hash>/', methods=['GET', 'POST'])
def drawing_hash(drawing_hash):
  drawing_db = model.Drawing.get_by('hash', drawing_hash)

  if not drawing_db:
    flask.abort(404)

  if drawing_id:
    drawing_db.json = json.dumps(drawing_db.json)
  form = DrawingUpdateForm(obj=drawing_db)

  if form.validate_on_submit():
    form.json.data = json.loads(form.json.data)
    form.populate_obj(drawing_db)
    drawing_db.put()
    return flask.redirect(flask.url_for('drawing_view', drawing_id=drawing_db.key.id()))

  return flask.render_template(
    'drawing/drawing_update.html',
    title='%s' % 'Drawing' if drawing_id else 'New Drawing',
    html_class='drawing-update',
    form=form,
    drawing_db=drawing_db,
  )


###############################################################################
# View
###############################################################################
@app.route('/drawing/<int:drawing_id>/')
def drawing_view(drawing_id):
  drawing_db = model.Drawing.get_by_id(drawing_id)
  if not drawing_db:
    flask.abort(404)

  return flask.render_template(
    'drawing/drawing_view.html',
    html_class='drawing-view',
    title='Drawing',
    drawing_db=drawing_db,
    api_url=flask.url_for('api.drawing', drawing_key=drawing_db.key.urlsafe() if drawing_db.key else ''),
  )
