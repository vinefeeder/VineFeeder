import json
import re
from scrapy import Selector


def parse_json(html):
    try:
        # Replace 'undefined' with 'null' to make the JSON valid
        json_data = html.replace('undefined', 'null')
        # Parse the JSON string
        parsed_json = json.loads(json_data)
        return parsed_json
    
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def extract_params_json(html):
    """
    Extract the JSON data from the HTML content that is stored in the 
    __PARAMS__ variable. This is typically used to parse the JSON data 
    from the HTML content of a page that contains a script tag with a 
    __PARAMS__ variable.

    Args:
        html (str): The HTML content from which to extract the JSON data.

    Returns:
        dict: The parsed JSON data, or None if no __PARAMS__ variable 
              was found, or if the JSON could not be parsed.
    """
    try:
        # Use Scrapy's Selector to locate the script tag containing "__PARAMS__"
        sel = Selector(text=html)

        # Extract the script content that contains 'window.__PARAMS__'
        selected_script = sel.xpath('//script[contains(text(), "__PARAMS__")]/text()').extract_first()

        if not selected_script:
            print("No script tag with '__PARAMS__' found.")
            return None
        
        # Remove 'window.__PARAMS__ =' and trailing semicolon
        json_data = selected_script.strip().replace('window.__PARAMS__ = ', '').rstrip(';')

        # Replace 'undefined' with 'null' to make the JSON valid
        json_data = json_data.replace('undefined', 'null')

        # Parse the JSON string
        parsed_json = json.loads(json_data)

        # Debugging: Print parsed JSON to verify it worked
        #print("Parsed JSON:")
        #print(json.dumps(parsed_json, indent=4))

        return parsed_json
    
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
       
def rinse(string):
    illegals = "*'%$!(),;"
    return ''.join(c for c in string if c.isprintable() and c not in illegals)

def prettify(val):
        try:
            parts = val.split('\t') 
            title = f"[#89B4FA]{parts[0]}[/]"  
            synopsis = f"[cyan]{parts[1]}[/]"  
            return f"{title}\t{synopsis}"
        except:
            return f"[#89B4FA]{val}[/]"   
