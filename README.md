# VineFeeder

VineFeeder is a dynamic Python-based application that presents a graphical user interface (GUI) to act as a front-end for Devine (https://github.com/devine-dl/devine) - a video-downloader

Vinefeeder enables users to interact with Devine's streaming services. The project allows users to browse and select media content from multiple services, each of which is dynamically loaded as a separate module.

Features:

*Dynamic Service Loading*: Services are loaded dynamically from a predefined folder. 
    Each service has its own configuration and logic, allowing flexible media handling.
    
*Service-Specific Parsing*: Each service can define its own method of parsing media 
    content, making the platform adaptable to different service architectures.
    
*Alphabetical Service Listing*: Services are displayed as clickable buttons in 
    alphabetical order, enhancing the user experience.
    
*GUI Interface*: The interface is built using PyQt6, offering a user-friendly experience
    for selecting media content.
    
*Category Browsing*: Services support browsing by category, allowing users to explore 
    content within specific genres or collections.
    
*Video Download*: Once media content is selected, videos can be downloaded directly
    from the service using predefined tools (e.g., devine).


**Installation**

Requirements

    Python 3.8 or higher
    Required Python modules (install via pip):
        beaupy
        devine
        httpx
        jmespath
        PyQt6
        PyQt6_sip
        PyYAML
        rich
        Scrapy

You can install the necessary packages by running:

With bash or a Window's Terminal install python modules to the same python environment (env) as Devine
Be sure Devine works correctly, then

    pip install -r requirements.txt
for VineFeeder

**Setup**

Clone the repository:
With bash or a Window's Terminal

    git clone https://github.com/your-username/vinefeeder.git
    cd vinefeeder

Each streaming service should be placed in the services folder, with each service having its own folder that contains:

+ A config.yaml file with the service configuration.
+ An __init__.py file defining the service's loader class (e.g., All4Loader).  Note All4 is fully implemented and should be used as a example.

Modify the config.yaml file for each service to include its media_dict, which defines the categories and URLs used for browsing.
Modify the config.yaml services: with the full path to your VineFeeder services folder.

**Usage**

Run the application by executing the main script:

With bash or a Window's Terminal
    python vineFeeder.py

*Interacting with Services*
Once the GUI is launched, you can interact with various streaming services by clicking on their corresponding buttons.
The 'URL or search' box MAY be used for an immediate search entry or direct-download URL. If left empty a menu is offered.

Services are displayed in alphabetical order for easy access. From there, you can:

    Browse Categories: Select a media category to view available content.
    Search by URL: Input a direct URL to download media content.
    Download Media: Select a media item to start the download process.

**Custom Services**

To add a new streaming service:

    Create a new folder for the service inside the services directory.
    Add the following:
        A config.yaml file with the media_dict. see below
        An __init__.py file defining the loader class for the service (e.g., TvnzLoader).
        Note: the loader class file MUST inherit BaseLoader see ALL4/__init__.py  as an example.
        Note: Most web-sites that provide on-demand streaming have a 'browse' page where video categories may be selected for view. Use some/all of these 
        links to produce a media_dict of ( catergory: link, }

VineFeeder will dynamically detect and load the new service on the next run.

**Special Devine Commands**

If your use requirements are such that each video you download using Devine needs many parameters to be passed to the downloader this tool may not meet your needs:
see https://github.com/billybanana80/DevineGUI

If however you are happy to set your download parameters once, for each service, in Devine's config.yaml, then this project may work well for you, and provide the front-end Devine has always lacked.

**Contributing**

Contributors are welcomed to add services to front-end those services provided by Devine.
.

Images
    ![VineFeeder GUI](https://github.com/vinefeeder/VineFeeder/blob/main/images/vinefeeder1.png)
    ![VineFeeder GUI](https://github.com/vinefeeder/VineFeeder/blob/main/images/vinefeeder2.png)
    ![Vinefeeder GUI](https://github.com/vinefeeder/VineFeeder/blob/main/images/vinefeeder3.png)

**License**

This project is licensed under the MIT License. See the LICENSE file for more details.
