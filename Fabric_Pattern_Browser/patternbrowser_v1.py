import sys
import os
import shutil
import yaml
import platform
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, 
                             QLabel, QHBoxLayout, QCheckBox, QTreeView, QSplitter, QLineEdit,
                             QMenu, QInputDialog, QMessageBox)
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QModelIndex, QSortFilterProxyModel, QPoint

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

def convert_path(path):
    if platform.system() == "Windows":
        if path.startswith("//wsl$/"):
            # Convert WSL path to Windows path
            parts = path.split('/')
            drive = parts[3].lower()
            windows_path = f"{drive}:\{'/'.join(parts[4:])}"
            return windows_path.replace('/', '\\')
        elif path.startswith("/mnt/"):
            # Convert WSL path to Windows path
            drive = path[5].upper()
            return f"{drive}:{path[6:].replace('/', '\\')}"
    elif platform.system() == "Linux":
        if ':' in path:
            # Convert Windows path to WSL path
            drive = path[0].lower()
            return f"/mnt/{drive}{path[2:].replace('\\', '/')}"
    return path

class FileBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_file = 'file_browser_settings.yaml'
        self.settings = self.load_settings()
        self.current_file = None
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
        self.folder_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.folder_view.customContextMenuRequested.connect(self.show_context_menu)
        self.folder_view.selectionModel().currentChanged.connect(self.on_current_changed)  # Add this line
        folder_layout.addWidget(self.folder_view)

        splitter.addWidget(folder_widget)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        self.folder_label = QLabel('Current Folder: None', self)
        content_layout.addWidget(self.folder_label)

        self.text_edit = QTextEdit(self)
        font = QFont("Courier", 10)
        self.text_edit.setFont(font)
        content_layout.addWidget(self.text_edit)

        self.save_changes_button = QPushButton('Save Changes', self)
        self.save_changes_button.clicked.connect(self.save_changes)
        content_layout.addWidget(self.save_changes_button)

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
                settings = yaml.safe_load(f)
                if 'root_folder' in settings:
                    settings['root_folder'] = convert_path(settings['root_folder'])
                return settings
        return {'dark_mode': False, 'root_folder': ''}

    def save_settings(self):
        settings_to_save = self.settings.copy()
        if 'root_folder' in settings_to_save:
            settings_to_save['root_folder'] = convert_path(settings_to_save['root_folder'])
        with open(self.settings_file, 'w') as f:
            yaml.dump(settings_to_save, f)

    def apply_saved_settings(self):
        if self.settings['dark_mode']:
            self.dark_mode_checkbox.setChecked(True)
            self.toggle_dark_mode(Qt.Checked)
        if self.settings['root_folder']:
            try:
                self.populate_folder_structure(self.settings['root_folder'])
                self.folder_label.setText(f'Current Folder: {self.settings["root_folder"]}')
            except FileNotFoundError:
                QMessageBox.warning(self, "Warning", "The saved root folder is not accessible. Please select a new folder.")
                self.select_folder()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Root Folder")
        if folder:
            folder = convert_path(folder)
            self.settings['root_folder'] = folder
            self.save_settings()
            self.folder_label.setText(f'Current Folder: {folder}')
            self.populate_folder_structure(folder)

    def populate_folder_structure(self, root_folder):
        self.folder_model.clear()
        root_item = self.folder_model.invisibleRootItem()
        try:
            self.add_folder_to_model(root_item, root_folder)
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", f"Unable to access the folder: {root_folder}")
            self.select_folder()

    def add_folder_to_model(self, parent_item, folder_path):
        folder_path = convert_path(folder_path)
        folder_name = os.path.basename(folder_path)
        item = QStandardItem(folder_name)
        item.setData(folder_path, Qt.UserRole)
        parent_item.appendRow(item)

        try:
            for entry in os.scandir(folder_path):
                if entry.is_dir():
                    self.add_folder_to_model(item, entry.path)
        except PermissionError:
            print(f"Permission denied: {folder_path}")
        except FileNotFoundError:
            print(f"Folder not found: {folder_path}")

    def on_folder_clicked(self, index):
        self.update_folder_content(index)

    def on_current_changed(self, current, previous):
        self.update_folder_content(current)

    def update_folder_content(self, index):
        source_index = self.proxy_model.mapToSource(index)
        item = self.folder_model.itemFromIndex(source_index)
        folder_path = item.data(Qt.UserRole)
        self.display_folder_content(folder_path)

    def display_folder_content(self, folder_path):
        folder_path = convert_path(folder_path)
        self.folder_label.setText(f'Current Folder: {folder_path}')
        content = []
        self.current_file = None
        try:
            for entry in os.scandir(folder_path):
                if entry.is_file() and entry.name.lower() == "system.md":
                    try:
                        with open(entry.path, 'r', encoding='utf-8') as file:
                            file_content = file.read()
                        content.append(f"File: {entry.path}\n\n{file_content}")
                        self.current_file = entry.path
                    except Exception as e:
                        content.append(f"Error reading file: {entry.path}\n{str(e)}")
            
            if content:
                self.text_edit.setText("\n\n".join(content))
            else:
                self.text_edit.setText("No system.md files found in this folder.")
                self.current_file = None
        except FileNotFoundError:
            self.text_edit.setText(f"Error: Folder not found - {folder_path}")
        except PermissionError:
            self.text_edit.setText(f"Error: Permission denied - {folder_path}")

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
                QMenu { background-color: #2b2b2b; color: #ffffff; border: 1px solid #555555; }
                QMenu::item:selected { background-color: #4b4b4b; }
            """)
        else:
            self.setStyleSheet("")

    def show_context_menu(self, position):
        index = self.folder_view.indexAt(position)
        if index.isValid():
            source_index = self.proxy_model.mapToSource(index)
            item = self.folder_model.itemFromIndex(source_index)
            folder_path = item.data(Qt.UserRole)

            context_menu = QMenu(self)
            copy_action = context_menu.addAction("Copy Folder Name")
            new_folder_action = context_menu.addAction("Create New Folder")
            rename_folder_action = context_menu.addAction("Rename Folder")
            clone_folder_action = context_menu.addAction("Clone Folder")
            delete_folder_action = context_menu.addAction("Delete Folder")

            action = context_menu.exec_(self.folder_view.viewport().mapToGlobal(position))

            if action == copy_action:
                self.copy_folder_name(item.text())
            elif action == new_folder_action:
                self.create_new_folder(folder_path)
            elif action == rename_folder_action:
                self.rename_folder(folder_path)
            elif action == clone_folder_action:
                self.clone_folder(folder_path)
            elif action == delete_folder_action:
                self.delete_folder(folder_path)

    def copy_folder_name(self, folder_name):
        clipboard = QApplication.clipboard()
        clipboard.setText(folder_name)
        QMessageBox.information(self, "Copied", f"Folder name '{folder_name}' copied to clipboard.")

    def create_new_folder(self, parent_folder):
        new_folder_name, ok = QInputDialog.getText(self, "Create New Folder", "Enter folder name:")
        if ok and new_folder_name:
            new_folder_path = os.path.join(convert_path(parent_folder), new_folder_name)
            try:
                os.makedirs(new_folder_path)
                QMessageBox.information(self, "Success", f"Folder '{new_folder_name}' created successfully.")
                self.populate_folder_structure(self.settings['root_folder'])
            except OSError as e:
                QMessageBox.critical(self, "Error", f"Failed to create folder: {str(e)}")

    def rename_folder(self, folder_path):
        folder_path = convert_path(folder_path)
        old_name = os.path.basename(folder_path)
        new_name, ok = QInputDialog.getText(self, "Rename Folder", "Enter new folder name:", text=old_name)
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(folder_path), new_name)
            try:
                os.rename(folder_path, new_path)
                QMessageBox.information(self, "Success", f"Folder renamed from '{old_name}' to '{new_name}' successfully.")
                self.populate_folder_structure(self.settings['root_folder'])
            except OSError as e:
                QMessageBox.critical(self, "Error", f"Failed to rename folder: {str(e)}")

    def clone_folder(self, folder_path):
        folder_path = convert_path(folder_path)
        old_name = os.path.basename(folder_path)
        new_name, ok = QInputDialog.getText(self, "Clone Folder", "Enter name for cloned folder:", text=f"{old_name}_copy")
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(folder_path), new_name)
            try:
                shutil.copytree(folder_path, new_path)
                QMessageBox.information(self, "Success", f"Folder '{old_name}' cloned to '{new_name}' successfully.")
                self.populate_folder_structure(self.settings['root_folder'])
            except OSError as e:
                QMessageBox.critical(self, "Error", f"Failed to clone folder: {str(e)}")

    def delete_folder(self, folder_path):
        folder_path = convert_path(folder_path)
        reply = QMessageBox.question(self, 'Delete Folder',
                                     f"Are you sure you want to delete the folder '{os.path.basename(folder_path)}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                shutil.rmtree(folder_path)
                QMessageBox.information(self, "Success", f"Folder '{os.path.basename(folder_path)}' deleted successfully.")
                self.populate_folder_structure(self.settings['root_folder'])
            except OSError as e:
                QMessageBox.critical(self, "Error", f"Failed to delete folder: {str(e)}")

    def save_changes(self):
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(self.text_edit.toPlainText())
                QMessageBox.information(self, "Success", "Changes saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save changes: {str(e)}")
        else:
            QMessageBox.warning(self, "Warning", "No file is currently open for editing.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileBrowser()
    ex.show()
    sys.exit(app.exec_())