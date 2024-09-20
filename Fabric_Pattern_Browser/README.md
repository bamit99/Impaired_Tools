# File Browser with Pattern Viewer

## Overview

This File Browser with Pattern Viewer is a Python-based desktop application that allows users to navigate through their file system and view the contents of specific files. It's particularly designed to display the contents of `system.md` files within selected folders, making it useful for browsing and viewing structured documentation or notes.

## Features

- File system navigation with a tree view
- Automatic content display of `system.md` files
- Dark mode toggle
- Folder search functionality
- Context menu for folder operations (copy, create, rename, clone, delete)
- Ability to save changes to viewed files
- Cross-platform compatibility (Windows, Linux)
- Persistent settings (remembers last opened folder and dark mode preference)

## Requirements

- Python 3.6+
- PyQt5
- PyYAML

## Installation

1. Ensure you have Python 3.6 or higher installed on your system.
2. Install the required dependencies:

   ```
   pip install PyQt5 PyYAML
   ```

3. Clone this repository or download the `patternbrowser_v1.py` file.

## Usage

1. Run the program:

   ```
   python patternbrowser_v1.py
   ```

2. Use the "Select Root Folder" button to choose the starting directory for browsing.
3. Navigate through the folder structure using the tree view on the left side of the application.
4. The content of `system.md` files will automatically be displayed in the text area on the right when a folder is selected.
5. Use the "Save Changes" button to save any edits made to the displayed file.
6. Toggle dark mode using the checkbox at the bottom of the window.

## Navigation

- Use mouse clicks or arrow keys to navigate through the folder structure.
- The content display updates automatically as you select different folders.

## Folder Operations

Right-click on a folder in the tree view to access the following operations:

- Copy Folder Name
- Create New Folder
- Rename Folder
- Clone Folder
- Delete Folder

## Search

Use the search bar above the folder tree to filter folders based on their names.

## Settings

The application saves your last used root folder and dark mode preference. These settings are stored in a `file_browser_settings.yaml` file in the same directory as the script.

## Note

This application is designed to work with `system.md` files. If a selected folder doesn't contain a `system.md` file, a message will be displayed indicating that no such file was found.

## Troubleshooting

If you encounter any issues with file or folder access, ensure that you have the necessary permissions for the directories you're trying to access.

## Contributing

Contributions to improve the File Browser with Pattern Viewer are welcome. Please feel free to submit pull requests or create issues for bugs and feature requests.

## License

This project is open-source and available under the MIT License.