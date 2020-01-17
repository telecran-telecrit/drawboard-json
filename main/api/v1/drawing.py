# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
import flask
import flask_restful

from api import helpers
import auth
import model
import util

from main import api_v1


@api_v1.resource('/<string:drawing_hash>.json', endpoint='api.hash')
class DrawingAPI(flask_restful.Resource):
  def get(self, drawing_hash):
    drawing_db = model.Drawing.get_by('hash', drawing_hash)
    if not drawing_db:
      helpers.make_not_found_exception('Drawing %s not found' % drawing_hash)
    return helpers.make_response(drawing_db, model.Drawing.FIELDS)


@api_v1.resource('/drawing/', endpoint='api.drawing.list')
class DrawingListAPI(flask_restful.Resource):
  def get(self):
    drawing_dbs, drawing_cursor = model.Drawing.get_dbs()
    return helpers.make_response(drawing_dbs, model.Drawing.FIELDS, drawing_cursor)


@api_v1.resource('/drawing/<string:drawing_key>/', endpoint='api.drawing')
class DrawingAPI(flask_restful.Resource):
  def get(self, drawing_key):
    drawing_db = ndb.Key(urlsafe=drawing_key).get()
    if not drawing_db:
      helpers.make_not_found_exception('Drawing %s not found' % drawing_key)
    return helpers.make_response(drawing_db, model.Drawing.FIELDS)


###############################################################################
# Admin
###############################################################################
@api_v1.resource('/admin/drawing/', endpoint='api.admin.drawing.list')
class AdminDrawingListAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self):
    drawing_keys = util.param('drawing_keys', list)
    if drawing_keys:
      drawing_db_keys = [ndb.Key(urlsafe=k) for k in drawing_keys]
      drawing_dbs = ndb.get_multi(drawing_db_keys)
      return helpers.make_response(drawing_dbs, model.drawing.FIELDS)

    drawing_dbs, drawing_cursor = model.Drawing.get_dbs()
    return helpers.make_response(drawing_dbs, model.Drawing.FIELDS, drawing_cursor)

  @auth.admin_required
  def delete(self):
    drawing_keys = util.param('drawing_keys', list)
    if not drawing_keys:
      helpers.make_not_found_exception('Drawing(s) %s not found' % drawing_keys)
    drawing_db_keys = [ndb.Key(urlsafe=k) for k in drawing_keys]
    ndb.delete_multi(drawing_db_keys)
    return flask.jsonify({
      'result': drawing_keys,
      'status': 'success',
    })


@api_v1.resource('/admin/drawing/<string:drawing_key>/', endpoint='api.admin.drawing')
class AdminDrawingAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self, drawing_key):
    drawing_db = ndb.Key(urlsafe=drawing_key).get()
    if not drawing_db:
      helpers.make_not_found_exception('Drawing %s not found' % drawing_key)
    return helpers.make_response(drawing_db, model.Drawing.FIELDS)

  @auth.admin_required
  def delete(self, drawing_key):
    drawing_db = ndb.Key(urlsafe=drawing_key).get()
    if not drawing_db:
      helpers.make_not_found_exception('Drawing %s not found' % drawing_key)
    drawing_db.key.delete()
    return helpers.make_response(drawing_db, model.Drawing.FIELDS)
