# channel 4 __init__.py
from base_loader import BaseLoader
from parsing_utils import extract_params_json, prettify
from rich.console import Console
import subprocess
import sys, re, json
from beaupy import select
import jmespath
import vinefeeder as VF

console = Console()


class All4Loader(BaseLoader):
    def __init__(self):
        headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)',
            'Origin': 'https://www.channel4.com',
            'Referer': 'https://www.channel4.com/',
        }
        super().__init__(headers)

    # entry point from Vinefeeder
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
            #print(['devine', 'dl', 'ALL4', search_term])
            subprocess.run(['devine', 'dl', 'ALL4', search_term])  # url

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
                search_term = search_term.split('?')[0]
            return (self.fetch_videos(search_term))
        
        elif 'http' in search_term and inx == 2:
            self.fetch_videos_by_category(search_term)  # search_term here holds a URL!!!
            
        else:
            print(f"Unknown error when searching for {search_term}")
            
        # prepare terminal for next run    
    
        print(f"[info] Finished downloading for {search_term}")
        print("[info] Ready: waiting for service selection...")
        self.clean_terminal()
        return


    def fetch_videos(self, search_term):
        """Fetch videos from Channel 4 using a search term."""
        # returns json as type String
        url = f"https://all4nav.channel4.com/v1/api/search?q={search_term}&limit=100"
        try:
            html = self.get_data(url)
            if 'No Matches' in html:
                print('Nothing found for that search; try again.')
                self.clean_terminal()
            else:
                parsed_data = self.parse_data(html)  # to json
        except:
            print(f'No valid data returned for {url}')
            self.clean_terminal()
            sys.exit(0)
            return None
        

        # Assuming that parsed_data has a 'results' key containing video data
        if parsed_data and 'results' in parsed_data:
            
            for item in parsed_data['results']:
                series_name = item.get('brand', {}).get('websafeTitle', 'Unknown Series')
                episode = {
                    'title': item.get('brand', {}).get('title', 'Unknown Title'),
                    'url': f"{item.get('brand', {}).get('href', '')}",
                    'synopsis': item.get('brand', {}).get('description', 'No synopsis available.')
                }
                self.add_episode(series_name, episode)

        # List series and episodes using beaupy
        selected_series = self.display_series_list()
        if selected_series:
            return self.second_fetch(selected_series)  # Return URLs for selected episodes
        return None
    


    def second_fetch(self, selected):
        """
        Given a selected series name, fetch its HTML and extract its episodes.
        Or if given a direct url, fetch it and process for greedy download.
        The function will prepare the series data for episode selection and display the final episode list.
        It will return the URLs for the selected episodes.
        """
        if 'https' in selected:  # direct url provided skip url preparation
            url = selected
        else:
            url = self.get_selected_url(selected)
        try:
            myhtml = self.get_data(url=url)
        except:
            print(f"No valid data at {url} found.\n Exiting")
            self.clean_terminal()
            sys.exit(0)
        parsed_data = extract_params_json(myhtml)

        self.clear_series_data()  # Clear existing series data

        # Extract the episodes from the parsed data of the selected series
        if parsed_data and 'initialData' in parsed_data:
            series_name = parsed_data['initialData']['brand']['websafeTitle'] or 'unknownTitle'
            
            # Go through each episode in the selected series
            episodes = parsed_data['initialData']['brand'].get('episodes', [])
            for item in episodes:
                try:
                    episode = {
                        'series_no': item.get('seriesNumber', '00'),  # number exists or '00'
                        'title': item.get('title', 'Title unknown'),
                        'url': item.get('hrefLink'),
                        'synopsis': item['summary'] or None,
                    }
                except KeyError:
                    continue  # Skip any episode that doesn't have the required information
                self.add_episode(series_name, episode)
  
        self.prepare_series_for_episode_selection(series_name) # creates list of series; allows user selection of wanted series prepares an episode list over chosen series

        selected_final_episodes = self.display_final_episode_list(self.final_episode_data)
        for item in selected_final_episodes:
            url = item.split(',')[2].lstrip()
            if url == 'None':
                print(f"No valid URL for {item.split(',')[1]}")
                continue
            url = "https://www.channel4.com" + url
            
            # debug uncomment
            #print(url)
            #continue

            # fetch video
            subprocess.run(['devine', 'dl', 'ALL4', url])
            self.clean_terminal()


    def fetch_videos_by_category(self, browse_url):
        """
        Fetches videos from a category (Channel 4 specific).
        Args:
            browse_url (str): URL of the category page.
        Returns:
            None
        """
        beaupylist = []
        try:
            req = self.client.get(browse_url, headers=self.headers)
            
            # Parse the __PARAMS__ data (Channel 4 specific - cannot use parsing_utils/
            init_data = re.search(
                r'<script>window\.__PARAMS__ = (.*)</script>',
                req.content.decode().replace('\u200c', '').replace('\r\n', '').replace('undefined', 'null')
            )
            init_data = json.loads(init_data.group(1))

            # Extract brand items
            myjson = init_data['initialData']['brands']['items']
            # jmespath is a json parser that searches complex json
            # and, in this, case produces a simple dict from which
            # res(ults) are extracted.
            res = jmespath.search("""
            [*].{
                href: hrefLink,
                label: labelText,
                overlaytext: overlayText            
            } """, myjson)

            # Build the beaupy list for display
            for i, item in enumerate(res):
                label = item['label']
                overlaytext = item['overlaytext']
                beaupylist.append(f"{i} {label}\n\t{overlaytext}")

        except Exception as e:
            print(f"Error fetching category data: {e}")
            return

        # Use beaupy to select a video
        found = select(beaupylist, preprocessor=lambda val: prettify(val), cursor="🢧", cursor_style="pink1", page_size=8, pagination=True)
        if found:
            ind = found.split(' ')[0]
            url = res[int(ind)]['href']
            # url may be for series or single Film
            url = url.encode('utf-8', 'ignore').decode().strip()  # has spaces!

            # some categories may produce links to single videos
            # so the next action should be download and not a greedy search
            # for channel4 Film returns a list of single videos
            if 'film' in url:
                # direct download
                self.receive(1, url)
            else:
                # greedy search
                self.receive(0, url)
        else:
            print("No video selected.")
            return None
