VineFeeder

VineFeeder is a dynamic Python-based application that presents a graphical user interface (GUI) which acts as a front-end for Devine (https://github.com/devine-dl/devine)

Vinefeeder enables users to interact with various streaming services. The project allows users to browse and select media content from multiple services, each of which is dynamically loaded as a separate module.
Features

    Dynamic Service Loading: Services are loaded dynamically from a predefined folder. 
    Each service has its own configuration and logic, allowing flexible media handling.
    Service-Specific Parsing: Each service can define its own method of parsing media 
    content, making the platform adaptable to different service architectures.
    Alphabetical Service Listing: Services are displayed as clickable buttons in 
    alphabetical order, enhancing the user experience.
    GUI Interface: The interface is built using PyQt6, offering a user-friendly experience
    for selecting media content.
    Category Browsing: Services support browsing by category, allowing users to explore 
    content within specific genres or collections.
    Video Download: Once media content is selected, videos can be downloaded directly
    from the service using predefined tools (e.g., devine).

Installation
Requirements

    Python 3.8 or higher
    Required Python modules (install via pip):
        httpx
        PyQt6
        beaupy
        yaml
        jmespath

You can install the necessary packages by running:

bash

pip install -r requirements.txt

Setup

    Clone the repository:

bash

git clone https://github.com/your-username/vinefeeder.git
cd vinefeeder

    Each streaming service should be placed in the services folder, with each service having its own folder that contains:
        A config.yaml file with the service configuration.
        An __init__.py file defining the service's loader class (e.g., All4Loader).  Note All4 is fully implemented and should be used as a example.

    Modify the config.yaml file for each service to include its media_dict, which defines the categories and URLs used for browsing.
    Modify the config.yaml services: with the full path to your VineFeeder services folder.

Usage

Run the application by executing the main script:

bash

python vineFeeder.py

Interacting with Services

Once the GUI is launched, you can interact with various streaming services by clicking on their corresponding buttons.

The 'URL or search' box MAY be used for an immediate search entry or direct-download URL. If left empty a menu is offered.

Services are displayed in alphabetical order for easy access. From there, you can:

    Browse Categories: Select a media category to view available content.
    Search by URL: Input a direct URL to download media content.
    Download Media: Select a media item to start the download process.

Custom Services

To add a new streaming service:

    Create a new folder for the service inside the services directory.
    Add the following:
        A config.yaml file with the media_dict.
        An __init__.py file defining the loader class for the service (e.g., TvnzLoader).

VineFeeder will dynamically detect and load the new service on the next run.
Contributing

We welcome contributions! If you want to add a new feature, fix a bug, or improve existing functionality, please fork the repository and submit a pull request.
Steps to Contribute

    Fork the project.
    Create your feature branch:

    bash

git checkout -b feature/your-feature

Commit your changes:

bash

git commit -m 'Add your feature'

Push to the branch:

bash

    git push origin feature/your-feature

    Open a pull request.

Images
    ![VineFeeder GUI](https://github.com/vinefeeder/VineFeeder/blob/main/images/vinefeeder1.png)
    ![VineFeeder GUI](https://github.com/vinefeeder/VineFeeder/blob/main/images/vinefeeder2.png)

License

This project is licensed under the MIT License. See the LICENSE file for more details.
