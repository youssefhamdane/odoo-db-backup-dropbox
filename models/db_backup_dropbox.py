# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo

import logging
import os
from xmlrpc import client as xmlrpclib
import time
import socket
import dropbox

_logger = logging.getLogger(__name__)

def execute(connector, method, *args):
    res = False
    try:
        res = getattr(connector, method)(*args)
    except socket.error as error:
        _logger.critical('Error while executing the method "execute". Error: ' + str(error))
        raise error
    return res


class db_backup_dropbox(models.Model):
    _name = 'db.backup_dropbox'

    @api.multi
    def get_db_list(self, host, port, context={}):
        uri = 'http://' + host + ':' + port
        conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
        db_list = execute(conn, 'list')
        return db_list

    @api.multi
    def _get_db_name(self):
        dbName = self._cr.dbname
        return dbName

    # Columns
    host = fields.Char('Host', required=True, default='localhost')
    port = fields.Char('Port', required=True, default=8069)
    name = fields.Char('Nom de base données', required=True,
                       default=_get_db_name)
    folder = fields.Char('dossier de sauvegarde', required='True',
                         default='/odoo/backups')
    dropbox_access_token = fields.Char('DropBox Access Token', required=True, default='')

    @api.model
    def schedule_backup(self):
        conf_ids = self.search([])

        for rec in conf_ids:
            db_list = self.get_db_list(rec.host, rec.port)

            if rec.name in db_list:
                try:
                    if not os.path.isdir(rec.folder):
                        os.makedirs(rec.folder)
                except:
                    raise
                # backup path
                bkp_file = '%s_%s.%s' % (time.strftime('%Y_%m_%d_%H_%M_%S'), rec.name, 'zip')
                file_path = os.path.join(rec.folder, bkp_file)

                # backup base données
                try:
                    fp = open(file_path, 'wb')
                    odoo.service.db.dump_db(rec.name, fp, 'zip')
                    fp.close()
                except Exception as error:
                    _logger.debug("Error dump database: " + str(error))
                    continue

                # Dropbox
                try:
                    client = dropbox.Dropbox(rec.dropbox_access_token)
                    with open(file_path, "rb") as fp:
                        client.files_upload(fp.read(), '/'+bkp_file)
                except Exception as error:
                    _logger.debug("Error upload to dropbox: "+ str(error))
                    continue
            else:
                _logger.debug("database "+rec.name+" doesn't exist")

