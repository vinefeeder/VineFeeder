from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import QTimer
import sys
import os
import importlib.util
import yaml
from beaupy import select
import threading
from pretty import pretty_print
from rich.console import Console
from beaupy import select
from parsing_utils import prettify
import click

PAGE_SIZE = 8  # size of beaupy pagination


console = Console()


"""
Example usage:
    python vinefeeder.py --help       # Show help text
    python vinefeeder.py              # Launch VineFeeder GUI
"""


class VineFeeder(QWidget):
    
    def __init__(self):
        """
        Initialize the VineFeeder object.

        This method sets up the VineFeeder object by calling necessary functions to 
        initialize the UI, store available services dynamically, load services, 
        and create buttons dynamically.
        """
        super().__init__()
        self.init_ui()
        self.available_services = {}  # Store available services dynamically
        self.available_service_media_dict = {}
        self.available_services_hlg_status = {}
        self.available_services_options = {}
        self.load_services()  # Discover and load services
        self.create_service_buttons()  # Create buttons dynamically

    def init_ui(self):
        """
        Initialize the UI components and layout.

        This method creates the necessary UI components and sets up the layout. 
        It also connects the dark mode checkbox to the toggle_dark_mode method.
        """
        self.setWindowTitle("VineFeeder")
        layout = QVBoxLayout()

        self.search_url_label = QLabel("URL or search word")
        layout.addWidget(self.search_url_label)
        self.search_url_entry = QLineEdit()
        layout.addWidget(self.search_url_entry)

        highlighted_frame = QFrame()
        self.highlighted_layout = QVBoxLayout()
        highlighted_frame.setLayout(self.highlighted_layout)
        highlighted_frame.setStyleSheet("border: 1px solid blue;")  # Remove the border initially
        layout.addWidget(highlighted_frame)

        self.dark_mode_checkbox = QCheckBox("Dark Mode")
        self.dark_mode_checkbox.setChecked(True)  # Set dark mode by default
        self.dark_mode_checkbox.stateChanged.connect(self.toggle_dark_mode)
        layout.addWidget(self.dark_mode_checkbox, alignment=Qt.AlignmentFlag.AlignLeft)

        self.setLayout(layout)

        # Use a timer to delay the dark mode application slightly
        QTimer.singleShot(100, self.toggle_dark_mode)  # 100ms delay to ensure rendering


    def toggle_dark_mode(self):
        """
        Toggle the application's dark mode on or off.

        This method is connected to the dark mode checkbox's stateChanged signal. 
        When the checkbox is checked, the application is set to dark mode. When unchecked, 
        the application is set to light mode.

        In dark mode, the window and text colors are changed to dark colors, 
        and the search label and dark mode checkbox text are changed to white. 
        Buttons are also set to have a white text color and a dark grey background color.

        In light mode, the window and text colors are set back to their default values, 
        and the search label and dark mode checkbox text are changed back to black. 
        Buttons are also reset to their default appearance.

        NOTE: This method uses a QTimer to delay the application of the dark mode style slightly. 
        This is to ensure that the rendering of the UI components is complete 
        before applying the style changes.
        """
        if self.dark_mode_checkbox.isChecked():
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            self.setPalette(palette)
            self.search_url_label.setStyleSheet("color: white;")
            self.dark_mode_checkbox.setStyleSheet("color: white;")
            
            # Set button text to white in dark mode, remove red border
            for i in range(self.highlighted_layout.count()):
                button = self.highlighted_layout.itemAt(i).widget()
                if isinstance(button, QPushButton):
                    button.setStyleSheet("""
                        color: white;
                        background-color: #4e4e4e;
                        border: none;
                        padding: 5px;
                    """)
                    button.repaint()  # Force update of the button's appearance

        else:
            self.setPalette(QApplication.palette())
            self.search_url_label.setStyleSheet("color: black;")
            self.dark_mode_checkbox.setStyleSheet("color: black;")
           
            
            # Set button text to black in light mode, remove red border
            for i in range(self.highlighted_layout.count()):
                button = self.highlighted_layout.itemAt(i).widget()
                if isinstance(button, QPushButton):
                    button.setStyleSheet("""
                        color: black;
                        background-color: #aeaeae;
                        border: none;
                        padding: 5px;
                    """)
                    button.repaint()  # Force update of the button's appearance


    def load_services(self):
        """Dynamically load services from the services folder."""
        services_path = "./services"  # This can be dynamically loaded from config.yaml
        if not os.path.exists(services_path):
            print(f"Services folder {services_path} not found!")
            return

        for service in os.listdir(services_path):
            service_dir = os.path.join(services_path, service)
            if os.path.isdir(service_dir):
                config_file = os.path.join(service_dir, "config.yaml")
                init_file = os.path.join(service_dir, "__init__.py")
                if os.path.exists(config_file) and os.path.exists(init_file):
                    # Load the service config
                    with open(config_file, "r") as f:
                        service_config = yaml.safe_load(f)
                        service_name = service_config.get("service_name", service)
                        service_media_dict = service_config.get("media_dict", {})
                        service_hlg_status = service_config.get("hlg_status", False)
                        service_options = service_config.get("options", {})
                        self.available_services_hlg_status[service_name] = service_hlg_status #UHD wanted?
                        self.available_services_options[service_name] = service_options
                        self.available_service_media_dict[service_name] = service_media_dict
                        # Add the service to available_services dict
                        self.available_services[service_name] = init_file

    def create_service_buttons(self):
        """Create buttons for each dynamically loaded service in alphabetical order."""
        # Sort the services alphabetically by their names
        for service_name in sorted(self.available_services.keys()):
            button = QPushButton(service_name)
            button.clicked.connect(self.run_load_service_thread(service_name))  # Bind to threaded service loading
            self.highlighted_layout.addWidget(button)


    
    def do_action_select(self, service_name):
        """
        Top level choice for action required. Called if search_box is empty.
        Uses beaupy to display a list of 4 options: 
            - Search by keyword
            - Greedy Search by URL
            - Browse by Category
            - Download by URL
        Uses the selected option to call the appropriate function:
            - 0 for greedy search with url
            - 1 for direct url download
            - 2 for browse 
            - 3 for search with keyword
        Returns a tuple of the function selector and the url or None if no valid data is entered.
        """       

        fn = [
            "Greedy Search by URL",
            'Download by URL',
            'Browse by Category',
            "Search by keyword(s)",
            ]
        
        action = select(fn, preprocessor=lambda val: prettify(val),  cursor="🢧", cursor_style="pink1")
        inx = 0 # default to greedy       
        if 'Greedy' in action:
            url = input('URL for greedy search ')
            return 0, url, None
            
        elif 'Download' in action:
            url = input('URL for direct download ')
            return 1, url, None
        
        elif 'Browse' in action:
            media_dict = self.available_service_media_dict[service_name]
            beaupylist = []
            for item in media_dict:
                beaupylist.append(item)
            found = select(beaupylist,  preprocessor=lambda val: prettify(val),   cursor="🢧", cursor_style="pink1",  page_size=PAGE_SIZE, pagination=True)
            url = media_dict[found]
            return 2, url, found  # found is category
        
        elif 'Search' in action:
            keyword = input('Keyword(s) for search ')
            return 3, keyword, None
        
        else:
            print("No valid data entered!")
            sys.exit()


    def run_load_service_thread(self, service_name):
        """Start a new thread to load the service."""
        return lambda: threading.Thread(target=self.load_service, args=(service_name,)).start()

    def load_service(self, service_name):
        """Dynamically load the service's __init__.py when the button is clicked."""
        init_file = self.available_services.get(service_name)
        if init_file:
            try:
                # Load the service module
                spec = importlib.util.spec_from_file_location(service_name, init_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"[info] Loaded service: {service_name}\n\n")

                # Get text from input box, or pass None if empty
                text = self.search_url_entry.text().strip()
                text_to_pass = text if text else None
                

                # Dynamically instantiate the loader class
                loader_class_name = f"{service_name.capitalize()}Loader"  # Assuming class name is based on service name (e.g., Chan4Loader)
                
                if hasattr(module, loader_class_name):
                    loader_class = getattr(module, loader_class_name)
                    loader_instance = loader_class()  # Instantiate the service class
                    hlg_status = self.available_services_hlg_status[service_name] # UHD if available.
                    options = self.available_services_options[service_name]
                    if hasattr(loader_instance, 'receive'):
                        
                        if text_to_pass:
                            if 'http' in text_to_pass:  
                                loader_instance.receive(1, text_to_pass, None, hlg_status, options)
                                self.clear_search_box()  # inx 1 signifies direct download
                                loader_instance.clean_terminal()
                                sys.exit(0)
                            else:
                                loader_instance.receive(3, text_to_pass, None, hlg_status, options) # inx 3 for keyword search
                                self.clear_search_box()
                                loader_instance.clean_terminal()
                                sys.exit(0)
                        else:
                            inx, text_to_pass, found = self.do_action_select(service_name)  # returns a (int , url)
                            loader_instance.receive(inx, text_to_pass, found, hlg_status, options)
                            loader_instance.clean_terminal()
                            sys.exit(0)
                    else:
                        print(f"Service class {loader_class_name} has no 'receive' method")
                else:
                    print(f"No class {loader_class_name} found in {service_name}")
            except Exception as e:
                print(f"Error loading service: {service_name}, {e}")
        else:
            print(f"Service {service_name} not found!")
    def clear_search_box(self):
        self.search_url_entry.clear()


@click.command(help='VineFeeder: A tool to download videos from various streaming services.\
\n\nExample usage:\n\n    python vinefeeder.py --help       # Show help text\n\n    python vinefeeder.py              # Launch VineFeeder GUI')
def main():
    # say hello nicely
    pretty_print()
    app = QApplication(sys.argv)
    window = VineFeeder()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
