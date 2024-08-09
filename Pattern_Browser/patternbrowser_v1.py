import sys
import os
import yaml
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, 
                             QLabel, QHBoxLayout, QCheckBox, QTreeView, QSplitter, QLineEdit)
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QModelIndex, QSortFilterProxyModel

class FolderFilterProxyModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, source_parent):
        if self.filterRegExp().isEmpty():
            return True

        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        item = source_model.itemFromIndex(index)
        
        if item.hasChildren():
            for i in range(item.rowCount()):
                if self.filterAcceptsRow(i, index):
                    return True

        return self.filterRegExp().indexIn(item.text()) != -1

class FileBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_file = 'file_browser_settings.yaml'
        self.settings = self.load_settings()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('File Browser')
        self.setGeometry(100, 100, 1000, 600)

        main_layout = QVBoxLayout()

        splitter = QSplitter(Qt.Horizontal)

        folder_widget = QWidget()
        folder_layout = QVBoxLayout(folder_widget)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search folders...")
        self.search_input.textChanged.connect(self.filter_folders)
        folder_layout.addWidget(self.search_input)

        self.folder_model = QStandardItemModel()
        self.proxy_model = FolderFilterProxyModel()
        self.proxy_model.setSourceModel(self.folder_model)
        self.proxy_model.setRecursiveFilteringEnabled(True)
        self.folder_view = QTreeView()
        self.folder_view.setModel(self.proxy_model)
        self.folder_view.clicked.connect(self.on_folder_clicked)
        self.folder_view.setHeaderHidden(True)  # Hide the header
        folder_layout.addWidget(self.folder_view)

        splitter.addWidget(folder_widget)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        self.folder_label = QLabel('Current Folder: None', self)
        content_layout.addWidget(self.folder_label)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        font = QFont("Courier", 10)
        self.text_edit.setFont(font)
        content_layout.addWidget(self.text_edit)

        splitter.addWidget(content_widget)

        main_layout.addWidget(splitter)

        button_layout = QHBoxLayout()
        self.select_folder_button = QPushButton('Select Root Folder', self)
        self.select_folder_button.clicked.connect(self.select_folder)
        button_layout.addWidget(self.select_folder_button)

        self.dark_mode_checkbox = QCheckBox('Dark Mode', self)
        self.dark_mode_checkbox.stateChanged.connect(self.toggle_dark_mode)
        button_layout.addWidget(self.dark_mode_checkbox)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Apply saved settings
        self.apply_saved_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                return yaml.safe_load(f)
        return {'dark_mode': False, 'root_folder': ''}

    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            yaml.dump(self.settings, f)

    def apply_saved_settings(self):
        if self.settings['dark_mode']:
            self.dark_mode_checkbox.setChecked(True)
            self.toggle_dark_mode(Qt.Checked)
        if self.settings['root_folder']:
            self.populate_folder_structure(self.settings['root_folder'])
            self.folder_label.setText(f'Current Folder: {self.settings["root_folder"]}')

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Root Folder")
        if folder:
            self.settings['root_folder'] = folder
            self.save_settings()
            self.folder_label.setText(f'Current Folder: {folder}')
            self.populate_folder_structure(folder)

    def populate_folder_structure(self, root_folder):
        self.folder_model.clear()
        root_item = self.folder_model.invisibleRootItem()
        self.add_folder_to_model(root_item, root_folder)
        print(f"Number of top-level items: {root_item.rowCount()}")
        print(f"Items in proxy model: {self.proxy_model.rowCount()}")

    def add_folder_to_model(self, parent_item, folder_path):
        folder_name = os.path.basename(folder_path)
        item = QStandardItem(folder_name)
        item.setData(folder_path, Qt.UserRole)
        parent_item.appendRow(item)

        for entry in os.scandir(folder_path):
            if entry.is_dir():
                self.add_folder_to_model(item, entry.path)

    def on_folder_clicked(self, index):
        source_index = self.proxy_model.mapToSource(index)
        item = self.folder_model.itemFromIndex(source_index)
        folder_path = item.data(Qt.UserRole)
        self.display_folder_content(folder_path)

    def display_folder_content(self, folder_path):
        self.folder_label.setText(f'Current Folder: {folder_path}')
        content = []
        for entry in os.scandir(folder_path):
            if entry.is_file() and entry.name.lower() == "system.md":
                try:
                    with open(entry.path, 'r', encoding='utf-8') as file:
                        file_content = file.read()
                    content.append(f"File: {entry.path}\n\n{file_content}\n\n")
                except Exception as e:
                    content.append(f"Error reading file: {entry.path}\n{str(e)}\n\n")
        
        if content:
            self.text_edit.setText("".join(content))
        else:
            self.text_edit.setText("No system.md files found in this folder.")

    def filter_folders(self, text):
        self.proxy_model.setFilterRegExp(text)
        self.folder_view.expandAll()

    def toggle_dark_mode(self, state):
        self.settings['dark_mode'] = state == Qt.Checked
        self.save_settings()
        if state == Qt.Checked:
            self.setStyleSheet("""
                QWidget { background-color: #2b2b2b; color: #ffffff; }
                QTextEdit { background-color: #1e1e1e; color: #ffffff; border: 1px solid #555555; }
                QPushButton { background-color: #3b3b3b; color: #ffffff; border: 1px solid #555555; padding: 5px; }
                QPushButton:hover { background-color: #4b4b4b; }
                QCheckBox { color: #ffffff; }
                QLabel { color: #ffffff; }
                QTreeView { background-color: #1e1e1e; color: #ffffff; border: 1px solid #555555; }
                QTreeView::item:hover { background-color: #3b3b3b; }
                QTreeView::item:selected { background-color: #4b4b4b; }
                QLineEdit { background-color: #1e1e1e; color: #ffffff; border: 1px solid #555555; padding: 5px; }
            """)
        else:
            self.setStyleSheet("")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileBrowser()
    ex.show()
    sys.exit(app.exec_())