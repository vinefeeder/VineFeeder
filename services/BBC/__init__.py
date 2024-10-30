# BBC  __init__.py
"""The BBC does not follow the same structures as most other srvices
The BBC does not use  script = window.__PARAMS__ = ..."""

from base_loader import BaseLoader
from parsing_utils import rinse
from base_loader import BaseLoader
from parsing_utils import extract_params_json, prettify, parse_json
from rich.console import Console
import subprocess
import sys, re, json
from beaupy import select
import jmespath
from httpx import Client

client = Client()
console = Console()


class BbcLoader(BaseLoader):
    def __init__(self):
        headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
            'Origin': 'https://www.bbc.com',
            'Referer': 'https://www.bbc.com/',
        }
        super().__init__(headers)
        client = Client(headers=headers)

    def receive(self, inx: None, search_term: None):    
        """
        First fetch for series titles matching all or part of search_term.
        
        Uses inx, an int variable to switch:-
            0 for greedy search using url
            1 for direct url download
            2 for category browse 
            3 for search with keyword
        If search_url_entry is left blank vinefeeder generates a 
        a menu with 3 options:
            - Greedy Search by URL
            - Browse by Category
            - Search by Keyword
        results are forwarded to receive().
        If inx == 1, do direct download using url.
        If inx == 3, do keyword search.
        If inx == 0, fetch videos using a greedy search or browse-category.
        If inx == 2, fetch videos from a category url.
        If an unknown error occurs, exit with code 0.
        """
        
        # direct download
        if 'http' in search_term and inx == 1:
        
            subprocess.run(['devine', 'dl', 'iP', search_term])  # url
            #self.clean_terminal()
            return

        # keyword search
        elif inx == 3:
            print(f"Searching for {search_term}")
            return (self.fetch_videos(search_term))  
        
        # ALTERNATIVES BELOW FROM POP-UP MENU  
        elif inx == 0:  
            # from greedy-search OR selecting Browse-category
            # example: https://www.channel4.com/programmes/the-great-british-bake-off/on-demand/75228-001

            # need a search keyword(s) from url 
            # split and select series name
            search_term = search_term.split('/')[4] 
            # fetch_videos_by_category search_term may have other params to remove
            if '?' in search_term:  
                search_term = search_term.split('?')[0].replace('-',' ')
            return (self.fetch_videos(search_term))
        
        elif 'http' in search_term and inx == 2:
            self.fetch_videos_by_category(search_term)  # search_term here holds a URL!!!
            
        else:
            print(f"Unknown error when searching for {search_term}")
            
        # prepare terminal for next run    
    
        print(f"[info] Finished downloading for {search_term}")
        print("[info] Ready: waiting for service selection...")
        #return self.clean_terminal()
        return
        
    def fetch_videos(self, search_term):
        """Fetch videos from BBC using a search term."""
        
        #url = f"https://search.api.bbci.co.uk/formula/iplayer-ibl-root?q={search_term}&apikey=D2FgtcTxGqqIgLsfBWTJdrQh2tVdeaAp&seqId=0582e0f0-b911-11ee-806c-11c6c885ab56"
        url =  f"https://ibl.api.bbc.co.uk/ibl/v1/new-search?q={search_term}&rights=web&mixin=live"
        try:
            html = self.get_data(url)
            if 'No Matches' in html:
                print('Nothing found for that search; try again.')
                sys.exit(0)
            else:
                parsed_data = self.parse_data(html)  # to json
        except:
            print(f'No valid data returned for {url}')
            return
        
        #### debug ####
        #console.print_json(data=parsed_data)

        # Assuming that parsed_data has a 'results' key containing video data
        if parsed_data and 'new_search' in parsed_data:
            
            for item in parsed_data['new_search']['results']:
                series_name = item.get('title', 'Unknown Title')  # BBC has a 'title' key for series names
                
                episode = {
                    'title': item.get('title', 'Unknown Title'),
                    'url': f"{item.get('id', '')}",
                    'synopsis': item.get('synopsis', 'No synopsis available.')
                }
                self.add_episode(series_name, episode)
        else:
            print(f'No data found for {search_term}')
        # List series and episodes using beaupy
     
        selected_series = self.display_series_list()
        if selected_series:
            return self.second_fetch(selected_series)  # Return URLs for selected episodes
        return None
    
    def second_fetch(self, selected):
        # 'selected' is search term
        """
        Given a selected series name, fetch its HTML and extract its episodes.
        Or if given a direct url, fetch it and process for greedy download.
        The function will prepare the series data for episode selection and display the final episode list.
        It will return the URLs for the selected episodes.
        """
        if 'https' in selected:  # direct url provided skip url preparation
            url = selected  # 'https://www.bbc.co.uk/iplayer/episodes/m000mfhl'
            url = f"https://www.bbc.co.uk/iplayer/episode/{url.split('/')[-1]}"
        else:
            url = self.get_selected_url(selected)
            
            url = f"https://ibl.api.bbci.co.uk/ibl/v1/programmes/{url}/episodes?rights=mobile&availability=available&page=1&per_page=200&api_key=q5wcnsqvnacnhjap7gzts9y6"
            #print(url)
        
        myhtml = self.get_data(url=url)
        parsed_data = parse_json(myhtml)

        # testing
        #file = open("init_data.json", "w")
        #file.write(json.dumps(parsed_data))
        #file.close()
        #console.print_json(data=parsed_data)

        self.clear_series_data()  # Clear existing series data

        # Extract the episodes from the parsed data of the selected series
        if parsed_data and 'programme_episodes' in parsed_data:
            series_name = parsed_data['programme_episodes']['programme']['title'] or 'unknownTitle'
            
            # Go through each episode in the selected series
            episodes = parsed_data.get('programme_episodes').get('elements')
            for item in episodes:
                try:
                    episode = {
                        
                        'series_no': item['subtitle'].split(':')[0].split(' ')[1] or '01',
                        # 'title' is episode number here, some services use descriptive text
                        'title': item['subtitle'].split(':')[1].split(' ')[-1] or '01',
                        'url': "https://www.bbc.co.uk/iplayer/episode/" + item['id'],
                        'synopsis': item['synopses']['small']  or None,
                    }
                except KeyError:
                    continue  # Skip any episode that doesn't have the required information
                self.add_episode(series_name, episode)
  
        self.prepare_series_for_episode_selection(series_name) # creates list of series; allows user selection of wanted series prepares an episode list over chosen series
        selected_final_episodes = self.display_final_episode_list(self.final_episode_data)

        # specific to iP
        for item in selected_final_episodes:
            #print(item)
            mlist = item.split(',')
            url = mlist[2].strip()
            print(url)
        
            subprocess.run(['devine', 'dl', 'iP', url])
        #self.clean_terminal()
        return
