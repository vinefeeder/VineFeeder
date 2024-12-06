# VineFeeder

VineFeeder is a dynamic Python-based application and **framework** that presents a graphical user interface (GUI) to act as a front-end for Devine (https://github.com/devine-dl/devine) - a video-downloader

Vinefeeder enables users to more easily interact with Devine's streaming services. The project allows users to browse and select media content from multiple services, each of which is dynamically loaded as a separate module.  Each service has a configuration which will work out of the box, but Devine download options may be set on a service by service basis.

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

*Precision Episode Selection*:  Vinefeeder handles the selection of episodes and 'feeds' 
	Devine one-by-one, making Devine's -w switch defunct.


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

You can install the necessary VineFeeder packages with bash or a Window's Terminal. Make sure to install python modules to the same python environment (env) as Devine
First be sure to follow Devine's install and set-up procedure and ensure it all works correctly to your liking. **If you have installed Devine by any other way than via a 'pip install devine' then do so before running VineFeeder!  Make absolutely sure devine can be called from any folder on your system.**  Then, for VineFeeder,

    pip install -r requirements.txt


**Setup**
if you run Devine in a specific python environment  (virtual environment - venv) , first start that environment before installing VineFeeder

Clone the repository:
With bash or a Window's Terminal

    git clone https://github.com/vinefeeder/VineFeeder.git
    cd VineFeeder
    pip install -r requirements.txt



**Usage**

Run the application by executing the main script:

With bash or a Window's Terminal

    python vinefeeder.py 
    or
    python vinefeeder.py -help

As set-up on start it will run with zero modification if Devine is correctly installed. There are six UK services and TVNZ active.
Regard TVNZ as experimental for the time being. For one thing Devine's TVNZ service fails on some
Sports titles and the VineFeeder service is still in testing. If Devine fails use the URL with Ozivine -
there are reports it works. This Ozivine fork has a downloader https://github.com/liam8888999/ozivine

It is recommended to use PowerShell or Terminal in Windows and a Unix-like terminal in Linux - but select, via 
preferences, a dark background for better contrast with the colours used in Vinefeeder.

**Interacting with Services**

Once the GUI is launched, you mau interact with various streaming services by clicking on their corresponding buttons.
The 'URL or search' box MAY be used for an immediate search entry or direct-download URL or it may be left empty. 
If left empty a menu is offered.

**Help**

Starting VineFeeder with python vinefeeder.py --help will show options to set a service congfiguration - if required.

**Service Configuration**

Most users will not need alter any configuration to download videos!

However, if you have, in your past use of Devine resorted to setting Devine-download options other than -w etc.
You may continue to do with VineFeeder only you do so just once, in the config.yaml for each service.
Each service's config.yaml has an 'options:' entry just add the string you would use with devine e.g -q 720  to
ensure only 720p resolution videos are selected.

To open a config.yaml for a service:-

    python vinefeeder.py --service-folder <SERVICE-NAME>
    python vinefeeder.py --service-folder ALL4, for example
    
Edit the line starting 'options'. Use exactly the same syntax as Devine would require on its command line

Image
	![Vinefeeder GUI](https://github.com/vinefeeder/VineFeeder/blob/main/images/vinefeeder8.png)


Services are displayed in alphabetical order for easy access. From there, you can:

    Browse Categories: Select a media category to view available content.
    Search by URL: Input a direct URL to download media content.
    Download Media: Select a media item to start the download process.
    
**Services**

Currently six services are working  - All4, BBC, ITVX, My5 STV and U, all UK services and now TVNZ. 
Other services: awaiting contributors!!

**Text Entry Box**

This will be the predominant method of using VineFeeder. Search on a keyword to locate a
programme series and click on its title when search finishes, to select any combination of
episodes for download.

Additionlly the search box will take a URL for direct download. The URL may be for a single
episode and it will download directly. If you feed a URL for a *series of episode* i.e a 
series-link then Devine will download the series.

The text-entry-box is cleared automatically after use. Once a download successfully finishes
the screen displays 'Ready!' and waits for further entry.

**Series numbers**

Normally services will provide enough data to collect a series number.
When series numbers are not available, Vinfeeder sets a default number of 100.
This is for housekeeping reasons. Devine labelling defaults to 00 for any saved
videos without a specified series number.

**Backing out**

If you have followed a path to a selection and do not wish to continue then,
in most  circumstances, depending on operating system, ctrl-C will return you
to a 'Ready!' status display on the screen within a second or two, and await
further operations.

**Closing Down**

The GUI should first be shutdown by mouse-clicking the top right X. The GUI then should
release control of the Terminal. ctrl-C in the Terminal may be required if shutting down 
following an error.

**Custom Services**

Vinefeeder is a *framework* too. It has been written in such a way that most features 
needed to scape and parse a website are already written and available.

If you feel moderately confident with python, then writing a new service to allow Devine 
to be run more interactively, is relatively straightforward. Most of the processes for
downloading, parsing and displaying for selection form part of the base functions and
are already written in this framework.

Any new service will need an __init__.py to be written and to implement just four 
methods. 

The ultimate aim of a services's __init__.py is to extract a list of video-data from  a content 
provide and store it a numerous dict items in a list container. The video-data is collected in 
dict objects labelled 'episode'.

Each episode has

		    episode = {
                        'series_no': ser_number,
                        'title': ep_number,
                        'url': url,
                        'synopsis': synopsis
                    }
        
Note 'title' may be an episode number or descriptive text. It varies with provider
The dict is added to the Vinefeeder storage list by:-

                    self.add_episode(brand_slug, episode)

Note brand_slug is a series-name.  self.add_episode creates a lists of episode dicts
This happens in the __init__.py super-class of BaseLoader


To add a new service:

    Create a new folder for the service inside the services directory.
    Add the following:
        A config.yaml file with the media_dict. see examples in the existing services folder.
        
        An __init__.py file defining the loader class for the service.
        The name of the loader class is constrained. It must take the service tag name, e.g. TVNZ
        and use that to create the class-name TvnzLoader. This allows vinefeeder.py discover and
        to call its use later.
        Note: the loader class file MUST inherit (or sub-class) BaseLoader see ALL4/__init__.py  
        as an example.
        Note: Most web-sites that provide on-demand streaming have a 'browse' or 'category' 
        page where video categories may be selected for view. Use some/all of these links to 
        produce a media_dict of ( catergory: link, }
        
        There are 4 methods to implement
            receive
            fetch_videos
            second_fetch
            fetch_videos_by_category
        Follow any channel as a model except BBC and U. Most sites provide json to describe their video content. 
        Usually it is within a script.
        There are two methods to extract the json in parsing_utils depending on whether a script id
        is used or not.
        Parsing utils uses XPATH as a locator syntax. 
        ChatGPT will helpt to find the XPATH syntax if you give it the web page and tell it 
        which javascript you need.XPATH is considerably faster than alternates such as bs4.
        The BaseLoader class which your service must inherit, has methods to GET,  POST or 
        return OPTIONS from the web. 
        DO NOT USE OTHER METHODS THAN THESE PROVIDED.
        
        RECEIVE
        I find it easier to start off implementing a keyword search from the GUI text box. 
        Very few changes to an existing service receive method will be needed. 
        Copy one and adjust. Note the use of inx (index) to help specify action. 
        Vinefeeder's GUI calls the service, passing parameters in the process such as a 
        service's Devine download options. 
        By definiton some receive() parameters may be empty.
        
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
        Potentially, you may not implement this if the site does not provide a worthwhile browse by category list,
        or the data cannot be parsed readily. U falls into this category. 

VineFeeder will dynamically detect and load the new services on the next start.

**Special Devine Commands**

If your use requirements are such that each video you download using Devine needs many different parameters to be passed 
to the downloader, and set different each time, this tool may not meet your needs:
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
    

**License**

This project is licensed under the MIT License. See the LICENSE file for more details.
