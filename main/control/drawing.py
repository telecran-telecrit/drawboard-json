# coding: utf-8

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
# Admin List
###############################################################################
@app.route('/admin/drawing/')
@auth.admin_required
def admin_drawing_list():
  drawing_dbs, drawing_cursor = model.Drawing.get_dbs(
    order=util.param('order') or '-modified',
  )
  return flask.render_template(
    'drawing/admin_drawing_list.html',
    html_class='admin-drawing-list',
    title='Drawing List',
    drawing_dbs=drawing_dbs,
    next_url=util.generate_next_url(drawing_cursor),
    api_url=flask.url_for('api.admin.drawing.list'),
  )


###############################################################################
# Admin Update
###############################################################################

class DrawingUpdateAdminForm(flask_wtf.FlaskForm):
  hash = wtforms.StringField(
    model.Drawing.hash._verbose_name,
    [wtforms.validators.required(), wtforms.validators.length(max=500)],
    filters=[util.strip_filter],
  )


@app.route('/admin/drawing/create/', methods=['GET', 'POST'])
@app.route('/admin/drawing/<int:drawing_id>/update/', methods=['GET', 'POST'])
@auth.admin_required
def admin_drawing_update(drawing_id=0):
  if drawing_id:
    drawing_db = model.Drawing.get_by_id(drawing_id)
  else:
    drawing_db = model.Drawing()

  if not drawing_db:
    flask.abort(404)

  form = DrawingUpdateAdminForm(obj=drawing_db)

  if form.validate_on_submit():
    form.populate_obj(drawing_db)
    drawing_db.put()
    return flask.redirect(flask.url_for('admin_drawing_list', order='-modified'))

  return flask.render_template(
    'drawing/admin_drawing_update.html',
    title='%s' % '%sDrawing' % ('' if drawing_id else 'New '),
    html_class='admin-drawing-update',
    form=form,
    drawing_db=drawing_db,
    back_url_for='admin_drawing_list',
    api_url=flask.url_for('api.admin.drawing', drawing_key=drawing_db.key.urlsafe() if drawing_db.key else ''),
  )


###############################################################################
# Admin Delete
###############################################################################
@app.route('/admin/drawing/<int:drawing_id>/delete/', methods=['POST'])
@auth.admin_required
def admin_drawing_delete(drawing_id):
  drawing_db = model.Drawing.get_by_id(drawing_id)
  drawing_db.key.delete()
  flask.flash('Drawing deleted.', category='success')
  return flask.redirect(flask.url_for('admin_drawing_list'))
