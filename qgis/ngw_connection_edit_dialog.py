# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
/***************************************************************************
 NGW connection edit dialog

 NextGIS WEB API
                             -------------------
        begin                : 2014-10-31
        git sha              : $Format:%H$
        copyright            : (C) 2014 by NextGIS
        email                : info@nextgis.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
import re

from qgis.PyQt import uic
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from ..core.ngw_connection_settings import NGWConnectionSettings
from ..core.ngw_resource_factory import NGWResourceFactory
from .qgis_ngw_connection import QgsNgwConnection
from ..utils import log

from ..compat_py import urlparse


__author__ = 'NextGIS'
__date__ = 'October 2014'
__copyright__ = '(C) 2014, NextGIS'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ngw_connection_edit_dialog_base.ui'))


class NGWConnectionEditDialog(QDialog, FORM_CLASS):
    """
    Dialog for editing NGW connection settings
    ::param
    ngw_connection_settings
    If None - new connections settings instance was return
    Else - fields will be filed from param

    ::return
    If accept, DialogInstance.ngw_connection_settings contains edited instance
    """
    def __init__(self, parent=None, ngw_connection_settings=None, only_password_change=False):
        super(NGWConnectionEditDialog, self).__init__(parent)

        self._default_server_suffix = ".nextgis.com"
        self.__user_try_accept = False
        self.__only_password_change = only_password_change

        self.setupUi(self)

        self.lbConnectionTesting.setVisible(False)
        #self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        if self.__only_password_change:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            self.leUrl.setEnabled(False)
            self.leName.setEnabled(False)

        self.completer_model = QStringListModel()
        completer = QCompleter()
        completer.setModel(self.completer_model)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        self.leUrl.setCompleter(completer)

        self.cbLocalAccount.toggled.connect(self.__cbLocalAccountChecked)
        self.cbAsGuest.toggled.connect(self.__cbAsGuestChecked)

        self.leUrl.textEdited.connect(self.__url_changed)
        self.leUrl.textEdited.connect(self.__fill_conneection_name)

        # self.timerUrlChange = QTimer()
        # self.timerUrlChange.setSingleShot(True)
        # self.timerUrlChange.setInterval(500)
        # self.timerUrlChange.timeout.connect(self.__try_check_connection)
        # self.leUrl.textChanged.connect(self.timerUrlChange.start)

        self.leName.textChanged.connect(self.__name_changed_process)
        self.__user_change_connection_name = False
        self.leName.editingFinished.connect(self.__name_changed_finished)

        accessLinkHtml = u'<a href="{}"><span style=" text-decoration: underline; color:#0000ff;">{}</span></a>'.format(
            self.tr('http://docs.nextgis.com/docs_ngcom/source/ngqgis_connect.html#ngcom-ngqgis-connect-connection'),
            self.tr('Where do I get these?')
        )
        self.lAccessLink.setText(accessLinkHtml)

        self.__cbLocalAccountChecked(self.cbLocalAccount.checkState())
        self.__cbAsGuestChecked(self.cbAsGuest.checkState())

        self.ngw_conn_sett = ngw_connection_settings

        if self.ngw_conn_sett is not None:
            self.leUrl.setText(self.ngw_conn_sett.server_url)
            self.leName.setText(self.ngw_conn_sett.connection_name)

            if self.ngw_conn_sett.oauth:
                self.cbLocalAccount.setCheckState(Qt.Unchecked)
            else:
                self.cbLocalAccount.setCheckState(Qt.Checked)

            if self.ngw_conn_sett.username == "":
                self.cbAsGuest.setCheckState(Qt.Checked)
                #self.leUser.setText("administrator")
            else:
                self.cbAsGuest.setCheckState(Qt.Unchecked)
                self.leUser.setText(self.ngw_conn_sett.username)
                self.lePassword.setText(self.ngw_conn_sett.password)
        else:
            #self.leUser.setText("administrator")
            self.cbLocalAccount.setCheckState(Qt.Unchecked)
            self.cbAsGuest.setCheckState(Qt.Checked)
            self.leUser.setText('')
            self.lePassword.setText('')

        self.mutexPing = QMutex()
        self.needNextPing = False

        self.force_http = False
        self.need_check_http = False

    def set_alert_msg(self, msg):
        self.lbConnectionTesting.setVisible(True)
        self.lbConnectionTesting.setText(msg)
        self.lbConnectionTesting.setStyleSheet("color: red")

    def __url_changed(self, text):
        curent_cursor_position = self.leUrl.cursorPosition()
        lower_test = text.lower()
        self.leUrl.setText(lower_test)
        self.leUrl.setCursorPosition(curent_cursor_position)
        self.__autocomplete_url(lower_test)

    def __autocomplete_url(self, text):
        #if not self.__only_password_change:
        #    self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        text_complete = self._default_server_suffix

        if any(char in text for char in [':', '\\', '/']):
            self.completer_model.setStringList([])
            return

        first_point_pos = text.find(self._default_server_suffix[0])
        if first_point_pos != -1:
            text_after_point = text[first_point_pos:]

            if text_complete.find(text_after_point) == 0:
                text_complete = text_complete[len(text_after_point):]
            else:
                self.completer_model.setStringList([])
                return
        self.completer_model.setStringList([text + text_complete])
        self.__validate_fields()

    def __make_valid_url(self, url):
        url = url.strip()

        # Always remove trailing slashes (this is only a base url which will not be
        # used standalone anywhere).
        while url.endswith('/'):
            url = url[:-1]

        # Replace common ending when user copy-pastes from browser URL.
        url = re.sub('/resource/[0-9]+', '', url)

        o = urlparse(url)
        hostname = o.hostname

        # Select https if protocol has not been defined by user.
        if hostname is None:
            hostname = 'http://' if self.force_http else 'https://'
            return hostname + url

        # Force https regardless of what user has selected, but only for cloud connections.
        if url.startswith('http://') and url.endswith('.nextgis.com') and not url.endswith('.staging.nextgis.com') and not self.force_http:
            return url.replace('http://', 'https://')

        return url

    def __fill_conneection_name(self, url):
        if self.__user_change_connection_name is True:
            return

        url = self.__make_valid_url(url)

        o = urlparse(url)
        connection_name = o.netloc
        if connection_name.find(self._default_server_suffix) != -1:
            connection_name = connection_name.split('.')[0]

        self.leName.setText(connection_name)

    def __cbLocalAccountChecked(self, is_local_acc):
        if is_local_acc:
            self.gbLocalAccount.show()
            self.adjustSize()
        else:
            self.gbLocalAccount.hide()
            self.adjustSize()


    def __cbAsGuestChecked(self, as_guest):
        accessLinkHtml = ""
        if not as_guest:
            self.lbUser.setEnabled(True)
            self.leUser.setEnabled(True)
            self.lbPassword.setEnabled(True)
            self.lePassword.setEnabled(True)
        else:
            self.lbUser.setEnabled(False)
            self.leUser.setEnabled(False)
            self.lbPassword.setEnabled(False)
            self.lePassword.setEnabled(False)

    def __name_changed_process(self, text):
        self.__validate_fields()

    def __name_changed_finished(self):
        self.__user_change_connection_name = True

    @property
    def ngw_connection_settings(self):
        return self.ngw_conn_sett

    def __validate_fields(self):
        if not self.__user_try_accept:
            return True

        validation_result = True
        url = self.leUrl.text()
        if url == "":
            self.leUrl.setStyleSheet("background-color: #FFCCCC")
            self.leUrl.setPlaceholderText(self.tr("Fill it!"))

            validation_result = False
        else:
            self.leUrl.setStyleSheet("background-color: None")
        name = self.leName.text()
        if name == "":
            self.leName.setStyleSheet("background-color: #FFCCCC")
            self.leName.setPlaceholderText(self.tr("Fill it!"))

            validation_result = False
        else:
            self.leName.setStyleSheet("background-color: None")

        return validation_result

    def __try_check_connection(self):
        if not self.mutexPing.tryLock():
            self.needNextPing = True
            return
        self.__check_connection()

    def __check_connection(self, force_http=False):
        self.force_http = force_http # always check https connections if force_http is not set explicitly

        name = "temp"
        url = self.leUrl.text()
        url = self.__make_valid_url(url)
        user = ""
        password = ""

        ngw_conn_sett = NGWConnectionSettings(
            name,
            url,
            user,
            password,
            False
        )

        self.pinger = NGWPinger(ngw_conn_sett)
        self.thread = QThread(self)
        self.pinger.moveToThread(self.thread)
        self.thread.started.connect(self.pinger.run)

        self.pinger.getResult.connect(self.__process_ping_result)
        self.pinger.finished.connect(self.__process_ping_finish)
        self.pinger.finished.connect(self.thread.quit)

        self.lbConnectionTesting.setVisible(True)
        self.lbConnectionTesting.setStyleSheet("color: None")
        self.lbConnectionTesting.setText(self.tr("Connection test..."))
        self.thread.start()

    def __process_ping_result(self, ping_result):
        if ping_result is True:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            self.lbConnectionTesting.setText(self.tr("Connection successful!"))
            self.lbConnectionTesting.setStyleSheet("color: green")

        else:
            # Force checking http each time we fail to check some connection (often https).
            if not self.force_http:
                self.need_check_http = True
                return

            # self.lbConnectionTesting.setText(self.tr("Connection failed! Please check the URL."))
            self.lbConnectionTesting.setText(self.tr('Specified URL webgis not found! Or your webgis version is below 3'))
            self.lbConnectionTesting.setStyleSheet("color: red")

    def __process_ping_finish(self):
        if self.need_check_http:
            self.need_check_http = False
            self.__check_connection(force_http=True)
            return

        if self.needNextPing:
            self.needNextPing = False
            self.__check_connection()

            # It seems that it is important to return here so mutexPing will not
            # be unlocked while new thread works inside __check_connection().
            # Otherwise there are crashes in QGIS 3.
            # TODO: understand why it does not lead to crash in QGIS 2?
            return

        self.mutexPing.unlock()

    def accept(self):
        self.__user_try_accept = True
        if not self.__validate_fields():
            return

        url = self.leUrl.text()
        name = self.leName.text()

        url = self.__make_valid_url(url)

        oauth = not self.cbLocalAccount.checkState()

        user = ""
        passward = ""
        if self.cbAsGuest.checkState() == Qt.Unchecked:
            user = self.leUser.text()
            passward = self.lePassword.text()

        self.ngw_conn_sett = NGWConnectionSettings(
            name,
            url,
            user,
            passward,
            oauth)

        QDialog.accept(self)


class NGWPinger(QObject):
    getResult = pyqtSignal(bool)
    finished = pyqtSignal()

    def __init__(self, ngw_connection_settings):
        super(NGWPinger, self).__init__()
        self.__ngw_connection_settings = ngw_connection_settings

    def run(self):
        rsc_factory = NGWResourceFactory(
            QgsNgwConnection(self.__ngw_connection_settings, self)
        )

        try:
            rsc_factory.get_ngw_verson()
            self.getResult.emit(True)
        except:
            self.getResult.emit(False)

        self.finished.emit()
