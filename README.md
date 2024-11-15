# VineFeeder

VineFeeder is a dynamic Python-based application that presents a graphical user interface (GUI) to act as a front-end for Devine (https://github.com/devine-dl/devine) - a video-downloader

Vinefeeder enables users to more easily interact with Devine's streaming services. The project allows users to browse and select media content from multiple services, each of which is dynamically loaded as a separate module.  Each service has a confuration which will work out of the box, but Devine download options may be set on a service by service basis.

Features:

*Dynamic Service Loading*: Services are loaded dynamically from a predefined folder. 
    Each service has its own configuration and logic, allowing flexible media handling.
    
*Service-Specific Parsing*: Each service can define its own method of parsing media 
    content, making the platform adaptable to different service architectures.
    Additionally each service may store a string of download options for devine such as 
    video resolution or subtitle format.
    
*Alphabetical Service Listing*: Services are displayed as clickable buttons in 
    alphabetical order, enhancing the user experience.
    
*GUI Interface*: The interface is built using PyQt6, offering a user-friendly experience
    for selecting media content.
    
*Category Browsing*: Services support browsing by category, allowing users to explore 
    content within specific genres or collections.
    
*Video Download*: Once media content is selected, videos can be downloaded directly
    from the service using predefined tools (e.g., devine).
    
*Ultra-High-definition*:  Videos in UHD are automatically requested from sites that provide such quality.
hlg_status in config.yaml may be set to False to not do this.


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

You can install the necessary packages with bash or a Window's Terminal. Make sure to install python modules to the same python environment (env) as Devine
First be sure Devine works correctly to your liking, then, for VineFeeder,

    pip install -r requirements.txt


**Setup**

Clone the repository:
With bash or a Window's Terminal

    git clone https://github.com/your-username/vinefeeder.git
    cd vinefeeder

Each streaming service should be placed in the services folder, with each service having its own folder that contains:

+ A config.yaml file with the service configuration.
+ An __init__.py file defining the service's loader class (e.g., All4Loader).  Note All4 is fully implemented and should be used as a example.

Modify the config.yaml file for each service to include its media_dict, which defines the categories and URLs used for browsing.
Modify Devine's download options under the config.yaml sub-heading of options enter a string of options as you would use on the command line with Devine

**Usage**

Run the application by executing the main script:

With bash or a Window's Terminal

    python vinefeeder.py

*Interacting with Services*
Once the GUI is launched, you can interact with various streaming services by clicking on their corresponding buttons.
The 'URL or search' box MAY be used for an immediate search entry or direct-download URL. If left empty a menu is offered.
Each service's config.yaml may have an 'options:' entry just add the string you would use with devine.
Starting vinefeeder with python vinefeeder.py --help will show options to set a service congfiguration - if required.

Services are displayed in alphabetical order for easy access. From there, you can:

    Browse Categories: Select a media category to view available content.
    Search by URL: Input a direct URL to download media content.
    Download Media: Select a media item to start the download process.
**Services**

Currently six services are working  - All4, BBC, ITVX, My5 STV and U, all UK services. 
Other services: awaiting conributors!!

**Custom Services**

To add a new service:

    Create a new folder for the service inside the services directory.
    Add the following:
        A config.yaml file with the media_dict. see examples in the existing services folder
        An __init__.py file defining the loader class for the service (e.g., TvnzLoader).
        Note: the loader class file MUST inherit BaseLoader see ALL4/__init__.py  as an example.
        Note: Most web-sites that provide on-demand streaming have a 'browse' or 'category' page where 
        video categories may be selected for view. Use some/all of these 
        links to produce a media_dict of ( catergory: link, }
        There are 4 methods to implement
            receive
            fetch_videos
            second_fetch
            fetch_videos_by_category
        Follow any channel as a model except BBC and U. Most sites provide json to describe their video content. 
        Usually it is within a script.
        There are two methods to extract the json in parsing_utils depending on whether a script id is used or not.
        Parsing utils uses XPATH as a locator syntax. ChatGPT will helpt to find the XPATH syntax if you give it 
        the web page and tell it which javascript you need.
        The BaseLoader class which your service must inherit, has methods to GET,  POST or return OPTIONS from the web. 
        DO NOT USE OTHER METHODS THAN THESE PROVIDED.
        RECEIVE
        I find it easier to start off implementing a keywork search from the GUI text box. Very few changes to an existing 
        service receive method will be needed.
        FETCH_VIDEOS
        Fetch_videos is very service specific and will need to send data to a web-site and processs the response to provide 
        an 'episode' list for display. 
        Here 'episode' is a container for a web site's response of suggestion of a single video or series that match the 
        search-word.
        In the example below the parsed_data contains json from which we extract to add to BaseLoader's episode list via 
        self.add_episode(series_name, episode)
        
        if parsed_data and 'results' in parsed_data:
            for item in parsed_data['results']:
                series_name = item.get('brand', {}).get('websafeTitle', 'Unknown Series')
                episode = {
                    'title': item.get('brand', {}).get('title', 'Unknown Title'),
                    'url': f"{item.get('brand', {}).get('href', '')}",
                    'synopsis': item.get('brand', {}).get('description', 'No synopsis available.')
                }
                self.add_episode(series_name, episode)
                
        SECOND_FETCH
        Again the process is much the same as in fetch_videos() a web site has its html harvested, 
        a script is extracted from which json is pulled using the facility methods in BaseLoader and parsing _utils.
        FETCH_VIDEO_BY_CATEGORY
        Displays the media_dict from congig.yaml - so put any category heading andn links in the new service config.
        One a category is selected again parse json and follow an existing service for a model answer adjusting to suite the 
        syntax required by our new service.  

VineFeeder will dynamically detect and load the new services on the next start.

**Special Devine Commands**

If your use requirements are such that each video you download using Devine needs many different parameters to be passed to the downloader this tool may not meet your needs:
see https://github.com/billybanana80/DevineGUI

If however you are happy to set your download parameters once, variable for each service, the service's config.yaml, 
then this project may work well for you, and provide the front-end Devine has always lacked.

**Contributing**

Contributors are welcomed to add services to front-end those services provided by Devine - see above.
Presently six UK services are fully configured; contributions for other services welcome.
.

Images
    ![VineFeeder GUI](https://github.com/vinefeeder/VineFeeder/blob/main/images/vinefeeder1.png)
    ![VineFeeder GUI](https://github.com/vinefeeder/VineFeeder/blob/main/images/vinefeeder2.png)
    ![Vinefeeder GUI](https://github.com/vinefeeder/VineFeeder/blob/main/images/vinefeeder3.png)
    ![Vinefeeder GUI](https://github.com/vinefeeder/VineFeeder/blob/main/images/vinefeeder4.png)
    ![Vinefeeder GUI](https://github.com/vinefeeder/VineFeeder/blob/main/images/vinefeeder5.png)
    ![Vinefeeder GUI](https://github.com/vinefeeder/VineFeeder/blob/main/images/vinefeeder6.png)
    ![Vinefeeder GUI](https://github.com/vinefeeder/VineFeeder/blob/main/images/vinefeeder7.png)
    ![Vinefeeder GUI](https://github.com/vinefeeder/VineFeeder/blob/main/images/vinefeeder8.png)

**License**

This project is licensed under the MIT License. See the LICENSE file for more details.
