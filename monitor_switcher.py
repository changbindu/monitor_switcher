from PyQt5.QtWidgets import QApplication, QDialog, QHBoxLayout, QLayout, QGridLayout, QListWidgetItem, QListWidget, QListView, QPushButton, QMenu, QAction, QLabel, QLineEdit
from PyQt5.QtCore import QDate, QSize, Qt, QSettings
from PyQt5.QtGui import QIcon
import paramiko
import os
import sys


class MonitorSource:
    def __init__(self, name):
        self.name = name

    def close(self):
        raise NotImplemented

    def open(self):
        raise NotImplemented


class LinuxMonitorSource(MonitorSource):
    def __init__(self, name, address, username, password):
        self.address = address
        self.username = username
        self.password = password
        MonitorSource.__init__(self, name)

    def __ssh_cmd(self, command):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.address, username=self.username, password=self.password)
        print("execute remote command %s" % command)
        stdin, stdout, stderr = ssh.exec_command(command, timeout=5)
        for l in stdout:
            print("stdout : %s" % l.strip())
        for l in stderr:
            print("stderr : %s" % l.strip())

    def open(self):
        self.__ssh_cmd("xset -d :0 dpms force on")

    def close(self):
        self.__ssh_cmd("xset -d :0 dpms force off")


class WindowsMonitorSource(MonitorSource):
    def __init__(self, name):
        MonitorSource.__init__(self, name)

    def __local_cmd(self, command):
        print("execute local command %s" % command)
        result = os.popen(command).readlines()
        print(result)

    def open(self):
        self.__local_cmd("displayswitch.exe /extend")

    def close(self):
        self.__local_cmd("displayswitch.exe /internal")


class SettingsDialog(QDialog):
    def __init__(self, qsettings, parent=None):
        super(SettingsDialog, self).__init__(parent)

        self.qsettings = qsettings

        addresslabel = QLabel("Linux Desktop Address:")
        self.addressEdit = QLineEdit()
        addresslabel.setBuddy(self.addressEdit)
        self.addressEdit.setText(self.qsettings.value("linux/address"))

        usernamelabel = QLabel("Linux Desktop Username:")
        self.usernameEdit = QLineEdit()
        usernamelabel.setBuddy(self.usernameEdit)
        self.usernameEdit.setText(self.qsettings.value("linux/username"))

        passwordlabel = QLabel("Linux Desktop Password:")
        self.passwordEdit = QLineEdit()
        passwordlabel.setBuddy(self.passwordEdit)
        self.passwordEdit.setText(self.qsettings.value("linux/password"))
        self.passwordEdit.setEchoMode(QLineEdit.Password)

        okButton = QPushButton("OK")
        okButton.setDefault(True)
        okButton.clicked.connect(self.save_settings)

        mainLayout = QGridLayout()
        mainLayout.setSizeConstraint(QLayout.SetFixedSize)
        mainLayout.addWidget(addresslabel, 0, 0)
        mainLayout.addWidget(self.addressEdit, 0, 1)
        mainLayout.addWidget(usernamelabel, 1, 0)
        mainLayout.addWidget(self.usernameEdit, 1, 1)
        mainLayout.addWidget(passwordlabel, 2, 0)
        mainLayout.addWidget(self.passwordEdit, 2, 1)
        mainLayout.addWidget(okButton, 3, 1)
        self.setLayout(mainLayout)

    def save_settings(self):
        self.qsettings.setValue("linux/address", self.addressEdit.text());
        self.qsettings.setValue("linux/username", self.usernameEdit.text());
        self.qsettings.setValue("linux/password", self.passwordEdit.text());
        self.close()

class MonitorSwitcher(QDialog):
    def __init__(self, parent=None):
        super(MonitorSwitcher, self).__init__(parent)

        self.qsettings = QSettings("MonitorSwitcher", "changbin.du@gmail.com");

        button_win = QPushButton('', self)
        button_win.setIcon(QIcon('images/windows.png'))
        button_win.setIconSize(QSize(200, 200))
        button_win.setToolTip("Click to switch the display of your shared monitor to Windows screen")
        button_win.clicked.connect(self.switch_to_windows_monitor)

        button_ubuntu = QPushButton('', self)
        button_ubuntu.setIcon(QIcon('images/ubuntu.png'))
        button_ubuntu.setIconSize(QSize(200, 200))
        button_ubuntu.setToolTip("Click to switch the display of your shared monitor to Ubuntu screen")
        button_ubuntu.clicked.connect(self.switch_to_ubuntu_monitor)

        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(button_win)
        horizontalLayout.addWidget(button_ubuntu)

        self.setLayout(horizontalLayout)
        self.setWindowTitle("MonitorSwitcher - Switch display of shared monitor")
        #self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda point: self.popMenu.exec_(self.mapToGlobal(point)))
        self.popMenu = QMenu(self)
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.on_context_menu_settings)
        self.popMenu.addAction(settings_action)

        self.m_win = WindowsMonitorSource("Windows Laptop")
        self.m_ubuntu = LinuxMonitorSource("Ubuntu Desktop",
                                           self.qsettings.value("linux/address"),
                                           self.qsettings.value("linux/username"),
                                           self.qsettings.value("linux/password"))

    def on_context_menu_settings(self, point):
        dialog = SettingsDialog(self.qsettings)
        dialog.exec_()
        self.m_ubuntu.address = self.qsettings.value("linux/address")
        self.m_ubuntu.username = self.qsettings.value("linux/username")
        self.m_ubuntu.password = self.qsettings.value("linux/password")

    def switch_to_windows_monitor(self):
        self.m_win.open()
        self.m_ubuntu.close()

    def switch_to_ubuntu_monitor(self):
        self.m_win.close()
        self.m_ubuntu.open()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MonitorSwitcher()
    ex.show()
    sys.exit(app.exec_())
