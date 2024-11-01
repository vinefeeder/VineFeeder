# BBC  __init__.py
"""The BBC does not follow the same structures as most other srvices
The BBC does not use  script = window.__PARAMS__ = ..."""

from base_loader import BaseLoader
from parsing_utils import rinse
from base_loader import BaseLoader
from parsing_utils import extract_params_json,  parse_json, split
from rich.console import Console
import subprocess
import sys, json, re
import jmespath


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
        # TWO ALTERNATES FROM GUI-TEXT ENTRY; POULATED WITH KEYWORD OR URL
        # direct download from url
        if 'http' in search_term and inx == 1:
            # check form of url https://www.bbc.co.uk/iplayer/episode/m00049t7 minimum
            # https://www.bbc.co.uk/iplayer/episodes/p09twdp8/showtrial?seriesId=m0023h9h breaks devine
            # https://www.bbc.co.uk/iplayer/episode/b008bjg1/a-perfect-spy-episode-1
            search_term = split(search_term, '?', 1)[0].replace('episodes', 'episode')
            
            subprocess.run(['devine', 'dl', 'iP', search_term], stderr=subprocess.STDOUT)  # url
            return

        # keyword search
        elif inx == 3:
            print(f"Searching for {search_term}")
            return (self.fetch_videos(search_term))  
        
        # ALTERNATIVES BELOW FROM POP-UP MENU  
        elif inx == 0 and 'https' in search_term:  
            # from greedy-search OR selecting Browse-category

            if 'episodes' in search_term:
                # https://www.bbc.co.uk/iplayer/episodes/p09twdp8/showtrial?seriesId=m0023h9h
                search_term = split(search_term, '/', 6)[1]  # search_term 
                # fetch_videos_by_category search_term may have other params to remove
                if '?' in search_term:  
                    search_term = search_term.split('?')[0].replace('-',' ')
                return (self.fetch_videos(search_term))     
            else:
                print(f"No search term found  in {search_term}\nTry again with a series name in the url.")
                sys.exit(0)
                
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
            # thanks to kenyard for help with url preparation
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
            try:
                series_name = parsed_data['programme_episodes']['programme']['title'] or 'unknownTitle'
            except KeyError:
                print(f"No data found for {url}")
                sys.exit(1)
            except:
                print(f"No episodes currently available for {url}")
                print(f"Try again but be sure to use the series utmost top level url!")
                sys.exit(1)
        
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
                except:
                    try:
                        episode = {
                            'series_no': 0,
                            # 'title' is episode number here, some services use descriptive text
                            'title': item['subtitle'],  # could be date
                            'url': "https://www.bbc.co.uk/iplayer/episode/" + item['id'],
                            'synopsis': item['synopses']['small']  or None,
                        }
                    except KeyError:
                        continue
                     # Skip any episode that doesn't have the required information
                self.add_episode(series_name, episode)
  
        self.prepare_series_for_episode_selection(series_name) # creates list of series; allows user selection of wanted series prepares an episode list over chosen series
        selected_final_episodes = self.display_final_episode_list(self.final_episode_data)

        # specific to BBC
        for item in selected_final_episodes:
            #print(item)
            mlist = item.split(',')
            url = mlist[2].strip()
            print(url)
            subprocess.run(['devine', 'dl', 'iP', url], stderr=subprocess.STDOUT, )
        return
    
    def fetch_videos_by_category(self, browse_url):
        """
        Fetches videos from a category (Channel 4 specific).
        Args:
            browse_url (str): URL of the category page.
        Returns:
            None
        """
        beaupylist =[]

        req = self.client.get(browse_url, headers=self.headers)
        init_data = extract_params_json(req.content.decode(), '__IPLAYER_REDUX_STATE__')
        
        
        '''
        # for bug fixing
        console.print_json(data=init_data)
        file = open("init_data.json", "w")
        file.write(json.dumps(init_data))
        file.close()
        '''

        myjson = init_data
        #console.print_json(data=myjson)
        category = myjson['bundles'][0]['id']

        res = jmespath.search(
            """
            bundles[*].entities[*].episode[].{
                href: id,
                label: title.default,
                overlaytext: synopsis.small
            }
            """,
            myjson
        )
        #console.print_json(data=res)

        # Build the beaupylist for display
        for i, item in enumerate(res):
                label = item['label']
                overlaytext = item['overlaytext']
                beaupylist.append(f"{i} {label}\n\t{overlaytext}") # \n\t used to split text later

        found = self.display_beaupylist(beaupylist)
        if found:
            if not 'film' in category:
                #extract search_term for greedy search
                search_term = found.split('\n\t')[0][2:]
                return self.process_received_url_from_category(search_term, res)
            else:
                ind = found.split(' ')[0]
                url = res[int(ind)]['href']
                # url may be for series or single Film
                url = f"https://www.bbc.co.uk/iplayer/episode/{url}"
                url = url.encode('utf-8', 'ignore').decode().strip()  # has spaces!

                # process short-cut download or do greedy search on url
                return self.process_received_url_from_category(url, category)
            
        else:
            print("No video selected.")
            sys.exit(0)


