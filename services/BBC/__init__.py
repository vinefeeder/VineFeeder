from base_loader import BaseLoader
from parsing_utils import rinse

# BBC  __init__.py
from base_loader import BaseLoader
from parsing_utils import extract_params_json, prettify
from rich.console import Console
import subprocess
import sys, re, json
from beaupy import select
import jmespath

class BbcLoader(BaseLoader):
    def __init__(self):
        headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)',
            'Origin': 'https://www.bbc.com',
            'Referer': 'https://www.bbc.com/',
        }
        super().__init__(headers)
        
    def receive(self, inx: None, search_term: None):
    	print("Not implemented. This is a skeleton only.")
    	
    def fetch_videos(self, search_term):
        """Fetch videos from ITV using a search term."""
        print("Not implemented. This is a skeleton only.")
    	
    	

