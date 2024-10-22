from base_loader import BaseLoader
from parsing_utils import rinse

class ItvxLoader(BaseLoader):
    def __init__(self):
        headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)',
            'Origin': 'https://www.itv.com',
            'Referer': 'https://www.itv.com/',
        }
        super().__init__(headers)
        
    def receive(self, inx: None, search_term: None):
    	print("Not implemented. This is a skeleton only.")

    def fetch_videos(self, search_term):
        """Fetch videos from ITV using a search term."""
        url = f"https://textsearch.prd.oasvc.itv.com/search?query={search_term}&size=100"
        html = self.get_data(url)
        parsed_data = self.parse_data(html)

        # Assuming that parsed_data has a 'results' key containing video data
        if parsed_data and 'results' in parsed_data:
            for item in parsed_data['results']:
                series_name = item.get('programmeTitle', 'Unknown Series')
                episode = {
                    'title': item.get('programmeTitle', 'Unknown Title'),
                    'url': f"https://www.itv.com/watch/{item.get('programmeTitle' '').replace(' ', '-')}/{item.get('legacyId', {}).get('officialFormat', '')}",
                    'synopsis': item.get('synopsis', 'No synopsis available.')
                }
                self.add_episode(series_name, episode)

        # List series and episodes using beaupy
        selected_series = self.display_series_list()
        if selected_series:
            selected_episodes = self.display_episode_list(selected_series)
            return selected_episodes  # Return URLs for selected episodes
        return None
