import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QColorDialog, QDialog, QMainWindow, QDateTimeEdit, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QColor, QIcon
from data.bodies import BODIES, ID_TO_NAME
from ephemeris.api_search import query_horizons
from ephemeris.horizons import fetch_horizons_data
from visualization.plot import plot_trajectories

import matplotlib
matplotlib.use('Qt5Agg')

# Source: https://www.pythonguis.com/tutorials/creating-your-first-pyqt-window/

class BodySelectionDialog(QDialog):
    def __init__(self, api_search_dict):
        super().__init__()
        self.selected_id = None
        self.api_search_dict = api_search_dict

        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)

        self.ephemeris_body_list = QListWidget()

        self.ephemeris_search = QPushButton("Select which match you want to proceed with")
        self.ephemeris_search.clicked.connect(self.on_select)

        for match in api_search_dict:
            self.ephemeris_body_list.addItem(match)

        layout.addWidget(self.ephemeris_body_list)
        layout.addWidget(self.ephemeris_search)

        self.setLayout(layout)

    def on_select(self):
        selected = self.ephemeris_body_list.currentItem()
        if selected:
            self.selected_id = self.api_search_dict[selected.text()]
            self.accept()
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ephemeris Visualizer")
        self.resize(600, 800)

        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)

        self.start_date = QDateTimeEdit()
        self.start_date.setCalendarPopup(True)

        self.end_date = QDateTimeEdit()
        self.end_date.setCalendarPopup(True)

        self.step_size = QLineEdit()
        self.step_size.setPlaceholderText("Valid inputs are in a singular unit of m, d, or h (e.g. 1h, 30m, 3d)")

        self.ephemeris_body_list = QListWidget()
        self.ephemeris_body_list.itemChanged.connect(self.on_item_changed)
        self.ephemeris_body_list.itemDoubleClicked.connect(self.on_item_double_clicked)


        self.ephemeris_body_input = QLineEdit()
        self.ephemeris_body_input.setPlaceholderText("Valid ephemeris body inputs begin with an upper case letter (e.g. Orion, Cassini, Pluto)")

        self.ephemeris_search = QPushButton("Add New Body")
        self.ephemeris_search.clicked.connect(self.on_search)

        self.generate_results = QPushButton("Generate Results")
        self.generate_results.clicked.connect(self.on_generate)
        
        for name in BODIES:
            color = BODIES[name]['color']
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(color))
            item = QListWidgetItem(QIcon(pixmap), name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Unchecked)
            self.ephemeris_body_list.addItem(item)

        layout.addWidget(QLabel("<b>Start Date</b>"))
        layout.addWidget(self.start_date)
        layout.addWidget(QLabel("<b>End Date</b>"))
        layout.addWidget(self.end_date)
        layout.addWidget(QLabel("<b>Step Size Increment</b>"))
        layout.addWidget(self.step_size)
        layout.addWidget(QLabel("<b>Ephemeris Body List (Double click on item to change color) </b>"))
        layout.addWidget(self.ephemeris_body_list)
        layout.addWidget(QLabel("<b>New Ephemeris Body</b>"))
        layout.addWidget(self.ephemeris_body_input)
        layout.addWidget(self.ephemeris_search)
        layout.addWidget(self.generate_results)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        layout.addStretch()
    
    def on_generate(self):
        selected_names = []
        satellite_id_list = []
        for i in range(self.ephemeris_body_list.count()):
            item = self.ephemeris_body_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_names.append(item.text())
                satellite_id_list.append(BODIES[item.text()]['id'])

        start_time = self.start_date.dateTime().toString("yyyy-MM-dd")
        stop_time  = self.end_date.dateTime().toString("yyyy-MM-dd")
        title = ", ".join(selected_names) + f" | {start_time} to {stop_time}"
        step_val = self.step_size.text()
        
        data_map = fetch_horizons_data(satellite_id_list, start_time, stop_time, step_val)
        plot_trajectories(data_map, parent=self, title=title)

    def on_item_changed(self, item):
        if item.checkState() == Qt.Checked:
            print(f"'{item.text()}' checked")
        elif item.checkState() == Qt.Unchecked:
            print(f"'{item.text()}' unchecked")

    def on_item_double_clicked(self, item):
        color = QColorDialog.getColor()
        if color.isValid():
            BODIES[item.text()]['color'] = color.name()
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(color))
            item.setIcon(QIcon(pixmap))

    def on_search(self):
        body_input = self.ephemeris_body_input.text()
        result = query_horizons(body_input)

        if result == {}:
            print("No match found for user input: " + body_input)
        elif isinstance(result, dict):
            print("Multiple matches found for user input: " + body_input)
            dialog = BodySelectionDialog(result)
            if dialog.exec_() == QDialog.Accepted and dialog.selected_id:
                result = dialog.selected_id
                color = QColorDialog.getColor()
                if color.isValid():
                    BODIES[body_input] = {'id': result, 'color': color.name()}
                    ID_TO_NAME[result] = body_input
                    pixmap = QPixmap(16, 16)
                    pixmap.fill(QColor(color))
                    item = QListWidgetItem(QIcon(pixmap), body_input)
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    item.setCheckState(Qt.Checked)
                    self.ephemeris_body_list.addItem(item)
        else:
            print("Match found!")
            color = QColorDialog.getColor()
            if color.isValid():
                BODIES[body_input] = {'id': result, 'color': color.name()}
                ID_TO_NAME[result] = body_input
                pixmap = QPixmap(16, 16)
                pixmap.fill(QColor(color))
                item = QListWidgetItem(QIcon(pixmap), body_input)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setCheckState(Qt.Checked)
                self.ephemeris_body_list.addItem(item)