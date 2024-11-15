from httpx import Client
from parsing_utils import parse_json, prettify
from beaupy import select, select_multiple
from rich.console import Console
from abc import abstractmethod
import os, sys, time
from rich.console import Console
from pretty import create_clean_panel  # Adjust the path as needed

console = Console()       

class BaseLoader:
    def __init__(self, headers):
        """Initialize the BaseLoader class with the provided headers.

        Parameters:
            headers (dict): The headers to be used for making HTTP requests.

        Attributes:
            client: An instance of the Client class for making HTTP requests.
            headers (dict): The headers used for making HTTP requests.
            series_data (dict): In-memory store for initial series selection.
            final_episode_data (list): List to store final episode data.
            console: An instance of the Console class for displaying output.

        """
        self.client = Client()
        self.headers = headers
        self.series_data = {}  
        self.final_episode_data = [] 
        self.browse_video_list = []
        
        self.category = None

    def clear_series_data(self):
        self.series_data={}

    def get_series_data(self):
        return self.series_data

    def get_data(self, url,headers=None, params=None ):
        """Fetch data from a given URL."""

        if not headers:
            headers = self.headers
        response = self.client.get(url, headers=headers, params=params, follow_redirects=True)
        if response.status_code != 200:
            raise Exception("Failed to retrieve data.")
        return response.text
    
    def get_options(self, url, headers=None):
        if not headers:
            headers = self.headers
        response = self.client.options(url, headers=headers, follow_redirects=True)
        if response.status_code != 200:
            raise Exception("Failed to retrieve options-data.")
        return response.headers
    
    def post_data(self, url, data=None, json=None, headers=None):
        if not headers:
            headers = self.headers
        response = self.client.post(url, data=data, json=json, headers=headers, follow_redirects=True)
        if response.status_code != 200:
            raise Exception("Failed to retrieve data.")
        return response

    def parse_data(self, html):
        """Parse HTML data into JSON format."""
        return parse_json(html)

    def add_episode(self, series_name, episode):
        """Add an episode to the series in memory."""
        if series_name not in self.series_data:
            self.series_data[series_name] = []
        self.series_data[series_name].append(episode)
    def get_number_of_episodes(self, series_name):
        return len(self.series_data.get(series_name, []))   

    def add_final_episode(self, episode):
        """build episode list for final selction for download"""
        self.final_episode_data.append(episode)

    def get_series(self, series_name=None):
        """Return all episodes from a specific series or all series data."""
        if series_name:
            return self.series_data.get(series_name, [])
        return self.series_data

    def display_series_list(self):
        """Use beaupy to list all series and allow user to select one."""
        series_list = list(self.series_data.keys())
        selected_series = select(series_list,  preprocessor=lambda val: prettify(val),  cursor="🢧", cursor_style="pink1", page_size=12, pagination=True)
        return selected_series

    def display_episode_list(self, series_name):
        """Use beaupy to display episodes for a selected series."""
        episodes = self.series_data.get(series_name, [])
        episode_list = [f"{ep['series_no']}, {ep['title']}, {ep['url']}, \n\t {ep['synopsis']}" for ep in episodes]
        selected_episodes = select_multiple(
            episode_list,  preprocessor=lambda val: prettify(val),  minimal_count=1, cursor_style="pink1" ,pagination=True, page_size = 8,
        )
        return selected_episodes
    
    def get_final_episode_list(self):
        return self.final_episode_data
    
    def display_final_episode_list(self, final_episode_data):
        """Use beaupy to display episodes for a selected series."""
        #episodes = self.series_data.get(series_name, [])
        episode_list = [f"{ep['series_no']}, {ep['title']}, {ep['url']}, \n\t {ep['synopsis']}" for ep in final_episode_data]
        selected_episodes = select_multiple(
            episode_list,  preprocessor=lambda val: prettify(val),  minimal_count=1,  cursor_style="pink1" ,pagination=True, page_size = 8,
        )
        return selected_episodes
    
    def get_selected_url(self, series_name):
        """ Return single url for series """
        episode = self.series_data.get(series_name, [])
        # list with one dictionary item
        url  = episode[0]['url']
        return url
    
    def get_episodes_series_numbers(self, series_name ):
        """Return a sorted list of series numbers for a given series name."""
        try:
            mysorted_list = sorted({int(ep['series_no']) for ep in self.series_data[series_name]})
        except Exception as e:
            print(f"Error: {e}")    
        return mysorted_list
    
    def display_non_contiguous_series(self, episode_series_numbers):
        """
        Display the non-contiguous series numbers in a grid format with 4 columns.
        This is used when the series numbers are not contiguous, so the user can
        easily see which series numbers are available.
        """
        
        num_columns = 7
        num_rows = (len(episode_series_numbers) + num_columns - 1) // num_columns

        for row in range(num_rows):
            for col in range(num_columns):
                idx = row * num_columns + col 
                if idx < len(episode_series_numbers): 
                    print(f"{episode_series_numbers[idx]:<3}", end=' ')
                    #console.print(create_clean_panel(f"{episode_series_numbers[idx]:<3}"))
                    
            print() 


    def prepare_series_for_episode_selection(self, series_name):
        """
        Prepare the series data for episode selection and display the final episode list.
        Given a selected series name, fetch its HTML and extract its episodes.
        The function will check if the series numbers are contiguous and display 
        the final episode list.
        It will return the URLs for the selected episodes.
        """
        # bail out if episode count is limited to 12
        number_episodes = self.get_number_of_episodes(series_name)
        if number_episodes <=12:
            for episode in self.series_data[series_name]: 
                    """store in list container"""
                    self.add_final_episode(episode)
            return
        try:
            self.episode_series_numbers = self.get_episodes_series_numbers(series_name)
            
        except:
            print(f"No data found")
            self.clean_terminal()
            sys.exit(0)

        # Check if the series numbers are contiguous (convert to integers for comparison)
        episode_series_numbers_int = sorted(int(num) for num in self.episode_series_numbers )

        if  episode_series_numbers_int == list(range(1, max(episode_series_numbers_int) + 1)):  # Contiguous series numbers
            max_series = max(episode_series_numbers_int)
            console.print(create_clean_panel((f"There are {max_series} series for {series_name.replace('-', ' ').title()}.\nYou may choose from 1 to {max_series}.")))
        else:  # Non-contiguous series
            console.print(create_clean_panel((f"Data for {series_name.replace('-', ' ').title()}\nSeries are non-contiguous:")))
            self.display_non_contiguous_series(self.episode_series_numbers)

        
        user_input = input("\nHint:- 2, 3, 5..13\n'all' or '0' for all-series: ? ")
        print('\n')
    
        selected_series = []
        if user_input == 'all' or user_input == '0':  
            selected_series = self.episode_series_numbers
        else:
            # Handle single digits, multiple digits, and ranges
            for part in user_input.split(','):
                part = part.strip()
                if '..' in part:  # Range of digits (e.g., 2..5)
                    start, end = map(int, part.split('..'))
                    selected_series.extend(range(start, end + 1))
                else:  # Single digit
                    selected_series.append(int(part))  # Store as int for comparison

        
        # Filter the episodes based on the selected series numbers
        for series_no in selected_series:
         
            for episode in self.series_data[series_name]: 
                if int(episode['series_no']) == int(series_no):
                    """store in list container"""
                    self.add_final_episode(episode)
                    

    def display_beaupylist(self, beaupylist):

        found = select(beaupylist, preprocessor=lambda val: prettify(val),\
                        cursor="🢧", cursor_style="pink1", page_size=8, pagination=True)
        return found
        
    def process_received_url_from_category(self, url, category=None):
        """
        Process the receive category vidoes based on the response length and URL.
        
        Parameters
        ----------
        url : str
            The URL to process.
        
        res : list
            The response from the URL.
        
        Returns
        -------
        None
        """

        if not category:  # no category
            category = self.category
        if 'Film' in category or 'Movie' in category:  # by defintion - single
            # direct download
            self.receive(1, url)
            return

        if 'film' in url or 'movie' in url:  # by defintion - single
            # direct download
            self.receive(1, url)
            return
        
        if not 'https' in url:  # browse entry
            self.receive(3, url)
            return
        else:
            #if 'https'
            # greedy search
            self.receive(0, url)
            return
        

    def clean_terminal(self):
        # clear for next use
        time.sleep(1)
        if os.name == 'posix':       
            #os.system('clear')
            print("Ready!")
            return
        else:
            #os.system('cls')
            print("Ready!")
            return
        
            
    
              

        

    ### methods that must be implemented by a service
    @abstractmethod
    def receive(self, inx, search_term: None):
        """
        search_term for video search
        or for direct url download
        Leave search_entry blank for
        further search optiions
        greedy-search with url
        browse-category search using 
        media_dict from config.yaml for service.  
        method called from vinefeeder and implemented in service/__init__
        """
        raise NotImplementedError("This method must be implemented in the service-specific loader.")
    @abstractmethod
    def fetch_videos_by_category(self, url):
        """This is a base method to be overridden by each service."""
        raise NotImplementedError("This method must be implemented in the service-specific loader.")
    
    @abstractmethod
    def second_fetch(self, url):
        """This is a base method to be overridden by each service."""
        raise NotImplementedError("This method must be implemented in the service-specific loader.")
    
    @abstractmethod
    def fetch_videos(self, search_term: str):
        """This is a base method to be overridden by each service."""
        raise NotImplementedError("This method must be implemented in the service-specific loader.")