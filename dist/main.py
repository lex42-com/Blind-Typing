import sqlite3
import sys
from random import randint
import time

from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QTableWidgetItem, QButtonGroup, \
    QMessageBox
from PyQt6.QtCore import Qt, QTimer
from UI import CommunityLevelsScreenUI, CreateNewLevelWindowUI, EndGameScreenUI, GameScreenUI, LogInWindowUI, \
    MainWindowUI, NewGameScreenUI, RecordsUI, RegWindowUI, VerificationUI


class CommunityLevelsScreen(QDialog, CommunityLevelsScreenUI.Ui_Dialog):
    def __init__(self, parent, flags, user):
        super().__init__(parent=parent, flags=flags)
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.user = user
        self.play_butt.clicked.connect(self.play)
        self.find.clicked.connect(self.finder)
        self.back_butt.clicked.connect(self.back)
        con = sqlite3.connect("../DataBases/DB.sqlite")
        cur = con.cursor()
        self.r = cur.execute("""SELECT user_id, name, text FROM Levels""").fetchall()
        self.full_list = []
        self.dict_of_levels = {}
        for i in self.r:
            r1 = cur.execute("""SELECT username FROM Users
            WHERE id = ?""", (i[0],)).fetchall()[0][0]
            self.full_list.append((r1, i[1]))
            self.list_of_levels.addItem("Username: " + str(r1) + "  Level name: " + str(i[1]))
            self.dict_of_levels[str(r1) + " " + str(i[1])] = i[2]

    def back(self):
        self.close()

    def finder(self):
        if self.finder_edit.text() == "":
            self.list_of_levels.clear()
            con = sqlite3.connect("../DataBases/DB.sqlite")
            cur = con.cursor()
            r = cur.execute("""SELECT user_id, name FROM Levels""").fetchall()
            for i in r:
                r1 = cur.execute("""SELECT username FROM Users
                        WHERE id = ?""", (i[0],)).fetchall()[0][0]
                self.list_of_levels.addItem("Username: " + str(r1) + "  Level name: " + str(i[1]))
            return
        self.list_of_levels.clear()
        con = sqlite3.connect("../DataBases/DB.sqlite")
        cur = con.cursor()
        r = cur.execute("""SELECT user_id, name FROM Levels
        WHERE name = ?""", (self.finder_edit.text(),)).fetchall()
        for i in r:
            r1 = cur.execute("""SELECT username FROM Users
                    WHERE id = ?""", (i[0],)).fetchall()[0][0]
            self.list_of_levels.addItem("Username: " + str(r1) + "  Level name: " + str(i[1]))

    def play(self):
        s = self.list_of_levels.selectedItems()[0].text().split()
        selected = s[1] + " " + s[4]
        e = GameScreen(self, Qt.WindowType.Window, "Уровень Коммьюнити", self.user, self.dict_of_levels[selected])
        e.show()
        self.close()


class EndGameScreen(QDialog, EndGameScreenUI.Ui_Dialog):
    def __init__(self, parent, flags, t, accuracy, speed, user, training_mode):
        super().__init__(parent=parent, flags=flags)
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.time_lable.setText("Время: " + str(t) + " c")
        self.speed_lable.setText("Скорость: " + str(speed) + " з/с")
        self.accuracy_lable.setText(str(accuracy) + " ошибок")
        con = sqlite3.connect("../DataBases/DB.sqlite")
        cur = con.cursor()
        cur.execute("""INSERT INTO Results(user_id, training_mode, speed, accuracy, time) VALUES(?, ?, ?, ?, ?)""",
                    (user, training_mode, speed, accuracy, t))
        con.commit()
        self.back_butt.clicked.connect(self.back)

    def back(self):
        self.close()


class GameScreen(QDialog, GameScreenUI.Ui_Dialog):
    def __init__(self, parent, flags, butt_name, user, text=""):
        super().__init__(parent=parent, flags=flags)
        self.setupUi(self)
        self.butt_name = butt_name
        self.user = user
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.start_time = time.time()
        self.dict_of_levels = {"Короткие слова Русский": "SWR", "Короткие слова Английский": "SWE",
                               "Длинные слова Русский": "LWR", "Длинные слова Английский": "LWE"}
        if text != "":
            self.game_text.setPlainText(text)
        elif self.butt_name not in self.dict_of_levels.keys():
            for i in range(200):
                self.game_text.setPlainText(self.game_text.toPlainText() + self.butt_name[randint(0, 4)])
        else:
            words = []
            for i in range(15):
                with open(f"../TXT/{self.dict_of_levels[self.butt_name]}.txt", "r", encoding="utf-8") as f:
                    text = f.readline().split()
                    words.append(
                        text[randint(0, len(text)) - 1])
            self.game_text.setPlainText(" ".join(words))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_text)
        self.timer.start(100)

    def check_text(self):
        if len(self.game_text.toPlainText()) <= len(self.user_text.toPlainText()):
            self.user_text.setReadOnly(True)
            mistakes = 0
            for i in range(len(self.game_text.toPlainText())):
                if self.game_text.toPlainText()[i] != self.user_text.toPlainText()[i]:
                    mistakes += 1

            elapsed_time = round(time.time() - self.start_time)

            speed = round(len(self.game_text.toPlainText()) / elapsed_time, 2)
            e = EndGameScreen(self, Qt.WindowType.Window, elapsed_time, mistakes, speed, self.user, self.butt_name)
            e.show()
            self.timer.stop()
            self.close()

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_C:
                event.ignore()
        else:
            super().keyPressEvent(event)


class Records(QDialog, RecordsUI.Ui_Dialog):
    def __init__(self, parent, flags):
        super().__init__(parent=parent, flags=flags)
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.back_butt.clicked.connect(self.back)
        con = sqlite3.connect("../DataBases/DB.sqlite")
        cur = con.cursor()
        r = sorted(cur.execute("""SELECT * FROM Results""").fetchmany(40), key=lambda y: y[3])
        self.results = []
        for i in r:
            mid_res = [str(cur.execute("""SELECT username FROM Users
            WHERE id = ?""", (i[1],)).fetchall()[0][0])]
            mid_res.extend([str(i[2]), str(i[3]), str(i[4]), str(i[5])])
            self.results.append(mid_res)
        for i in range(len(self.results)):
            for n in range(5):
                self.records_table.setItem(i, n, QTableWidgetItem(self.results[i][n]))

    def back(self):
        self.close()


class CreateNewLevelWindow(QDialog, CreateNewLevelWindowUI.Ui_Dialog):
    def __init__(self, parent, flags, user):
        super().__init__(parent=parent, flags=flags)
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.user = user
        self.save_new_level_butt.clicked.connect(self.save_new_lvl)
        self.back_butt.clicked.connect(self.back)

    def back(self):
        self.close()

    def save_new_lvl(self):
        con = sqlite3.connect("../DataBases/DB.sqlite")
        cur = con.cursor()
        names = list(map(lambda x: x[0], cur.execute("""SELECT name FROM Levels""")))
        if self.new_level_name.text() == "" or self.new_level_text.toPlainText() == "":
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setText("Поля не должны быть пустыми")
            msg_box.setWindowTitle("Ошибка")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            msg_box.exec()
            return
        elif self.new_level_name.text() in names:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setText("Такое имя уровня уже существует")
            msg_box.setWindowTitle("Ошибка")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            msg_box.exec()
            return
        else:
            cur.execute("""INSERT INTO Levels(user_id, name, text) VALUES(?, ?, ?)""",
                        (self.user, self.new_level_name.text(), self.new_level_text.toPlainText()))
            con.commit()
            self.close()


class NewGameScreen(QDialog, NewGameScreenUI.Ui_Dialog):
    def __init__(self, parent, flags, user):
        super().__init__(parent=parent, flags=flags)
        self.setupUi(self)
        self.user = user
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.back_butt.clicked.connect(self.back)
        self.butt_list = [self.butt, self.butt1, self.butt2, self.butt3, self.butt4, self.butt5, self.butt6, self.butt7,
                          self.butt8, self.butt9, self.butt10, self.butt11, self.butt12, self.butt13, self.butt14,
                          self.butt15, self.butt16, self.butt17, self.butt18, self.butt19, self.butt20]
        self.add_butt()

    def back(self):
        self.close()

    def start_game(self):
        e = GameScreen(self, Qt.WindowType.Window, self.sender().text(), self.user)
        e.show()
        self.close()

    def check_comm(self):
        e = CommunityLevelsScreen(self, Qt.WindowType.Window, self.user)
        e.show()
        self.close()

    def add_butt(self):
        for i in self.butt_list:
            i.clicked.connect(self.start_game)


class MainWindow(QMainWindow, MainWindowUI.Ui_MainWindow):
    def __init__(self, user):
        super().__init__()
        self.setupUi(self)
        self.user = user
        self.new_game_butt.clicked.connect(self.run_new_game)
        self.create_level_butt.clicked.connect(self.run_creation_new_level)
        self.records_butt.clicked.connect(self.run_records)
        self.exit_butt.clicked.connect(self.exit)

    def run_new_game(self):
        e = NewGameScreen(self, Qt.WindowType.Window, self.user)
        e.show()

    def run_creation_new_level(self):
        e = CreateNewLevelWindow(self, Qt.WindowType.Window, self.user)
        e.show()

    def run_records(self):
        e = Records(self, Qt.WindowType.Window)
        e.show()

    def exit(self):
        self.close()


class RegWindow(QDialog, RegWindowUI.Ui_Dialog):
    def __init__(self, parent, flags):
        super().__init__(parent=parent, flags=flags)
        self.main_window = ""
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.ready_butt.clicked.connect(self.ready_pressed)
        self.back_butt.clicked.connect(self.back)

    def back(self):
        self.close()

    def ready_pressed(self):
        con = sqlite3.connect("../DataBases/DB.sqlite")
        cur = con.cursor()
        users = {}
        usernames = cur.execute("""SELECT username FROM Users""").fetchall()
        passwordes = cur.execute("""SELECT password_hash FROM Users""").fetchall()
        for i in range(len(usernames)):
            users[str(usernames[i][0])] = str(passwordes[i][0])
        if self.username_reg_edit.text() == "" or self.password_reg_edit.text() == "":
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setText("Поля не должны быть пустыми")
            msg_box.setWindowTitle("Ошибка")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            msg_box.exec()
            return
        if self.username_reg_edit.text() in users.keys():
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setText("Такое имя уже существует")
            msg_box.setWindowTitle("Ошибка")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            msg_box.exec()
            return
        else:
            cur.execute("""INSERT INTO Users(username, password_hash) VALUES(?, ?)""",
                        (self.username_reg_edit.text(), self.password_reg_edit.text()))
            user_id = cur.execute("""SELECT id FROM Users
            WHERE username = ? AND password_hash = ?""",
                                  (self.username_reg_edit.text(), self.password_reg_edit.text())).fetchall()[0][0]
            con.commit()
            self.main_window = MainWindow(user_id)
            self.main_window.show()
            self.close()
            self.parent().close()


class LogInWindow(QDialog, LogInWindowUI.Ui_Dialog):
    def __init__(self, parent, flags):
        super().__init__(parent=parent, flags=flags)
        self.main_window = ""
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.ready_butt.clicked.connect(self.ready_pressed)
        self.back_butt.clicked.connect(self.back)

    def back(self):
        self.close()

    def ready_pressed(self):
        con = sqlite3.connect("../DataBases/DB.sqlite")

        cur = con.cursor()
        users = {}
        usernames = cur.execute("""SELECT username FROM Users""").fetchall()
        passwordes = cur.execute("""SELECT password_hash FROM Users""").fetchall()
        for i in range(len(usernames)):
            users[str(usernames[i][0])] = str(passwordes[i][0])
        if self.username_log_edit.text() == "" or self.password_log_edit.text() == "":
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setText("Поля не должны быть пустыми")
            msg_box.setWindowTitle("Ошибка")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            msg_box.exec()
        elif self.username_log_edit.text() not in users.keys():
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setText("Такого пользователя не существует")
            msg_box.setWindowTitle("Ошибка")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            msg_box.exec()
            return
        elif users[self.username_log_edit.text()] != self.password_log_edit.text():
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setText("Введен неверный пароль")
            msg_box.setWindowTitle("Ошибка")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            msg_box.exec()
            return
        else:
            user_id = cur.execute("""SELECT id FROM Users
                        WHERE username = ? AND password_hash = ?""",
                                  (self.username_log_edit.text(), self.password_log_edit.text())).fetchall()[0][0]
            self.main_window = MainWindow(user_id)
            self.main_window.show()
            self.close()
            self.parent().close()


class Verification(QDialog, VerificationUI.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.reg_butt.clicked.connect(self.run_register)
        self.login_butt.clicked.connect(self.run_log)

    def run_register(self):
        e = RegWindow(self, Qt.WindowType.Window)
        e.show()

    def run_log(self):
        e = LogInWindow(self, Qt.WindowType.Window)
        e.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Verification()
    ex.show()
    sys.exit(app.exec())
