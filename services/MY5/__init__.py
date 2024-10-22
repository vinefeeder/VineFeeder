from base_loader import BaseLoader
from parsing_utils import rinse

class My5Loader(BaseLoader):
    def __init__(self):
        headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)',
            'Origin': 'https://www.channel5.com',
            'Referer': 'https://www.channel5.com/',
        }
        super().__init__(headers)
        
    def receive(self, inx: None, search_term: None):
    	print("Not implemented. This is a skeleton only.")
    	
    def fetch_videos(self, search_term):
        """Fetch videos from ITV using a search term."""
        print("Not implemented. This is a skeleton only.")
    	
    	

