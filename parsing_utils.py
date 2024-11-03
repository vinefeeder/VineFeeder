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

def extract_params_json(html, discriminator="__PARAMS__", index=0):
    """
    For scripts like <script>window.__PARAMS__ = ...;</script>
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Extract the JSON data from the HTML content that is stored in the 
    __PARAMS__ variable. This is typically used to parse the JSON data 
    from the HTML content of a page that contains a script tag with a 
    __PARAMS__ variable.
    pass other discriminator if needed. 

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
        #selected_script = sel.xpath(f'//script[contains(text(), "{discriminator}")]/text()').extract_first()

        scripts = sel.xpath(f'//script[contains(text(), "{discriminator}")]/text()')
        
        if 0 <= index < len(scripts):
            selected_script = scripts[index].get()
        else:
            return None        
        
        # Remove 'window.__PARAMS__ =' and trailing semicolon
        json_data = selected_script.strip().replace(f'window.{discriminator} = ', '').rstrip(';').replace('\u200c', '').replace('\r\n', '')

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
       
def extract_script_with_id_json(html, discriminator, index=0):
    """
    For scripts like <script id="__NEXT_DATA__" type="application/json">
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Extract the JSON data from the HTML content that is stored in the 
    __PARAMS__ variable. This is typically used to parse the JSON data 
    from the HTML content of a page that contains a script tag with a 
    __PARAMS__ variable.
    pass other discriminator if needed. 

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
        #selected_script = sel.xpath(f'//script[contains(text(), "{discriminator}")]/text()').extract_first()
        # xpath = '//script[@id="__NEXT_DATA__" and @type="application/json"]/text()'
        scripts = sel.xpath(f'//script[@id="{discriminator}" and @type="application/json"]/text()')
        
        if 0 <= index < len(scripts):
            selected_script = scripts[index].get()
        else:
            return None        
        
        # Remove 'window.__PARAMS__ =' and trailing semicolon
        json_data = selected_script.strip().replace(f'window.{discriminator} = ', '').rstrip(';').replace('\u200c', '').replace('\r\n', '')

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
    
    
def extract_with_xpath(html, pattern, delete_pattern=None, index=0):
    """
    For scripts like <script id="__NEXT_DATA__" type="application/json">
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Extract the JSON data from the HTML content that is stored in the 
    __PARAMS__ variable. This is typically used to parse the JSON data 
    from the HTML content of a page that contains a script tag with a 
    __PARAMS__ variable.
    pass other discriminator if needed. 

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
        #selected_script = sel.xpath(f'//script[contains(text(), "{discriminator}")]/text()').extract_first()
        # xpath = '//script[@id="__NEXT_DATA__" and @type="application/json"]/text()'
        scripts = sel.xpath(f'{pattern}/text()')
        
        if 0 <= index < len(scripts):
            selected_script = scripts[index].get()
        else:
            return None        
        
        # Remove 'window.__PARAMS__ =' and trailing semicolon
        json_data = selected_script.strip().replace(f'{delete_pattern}', '').rstrip(';').replace('\u200c', '').replace('\r\n', '')

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
    """Remove non-printable characters from a string."""
    illegals = "*'%$!(),;"
    return ''.join(c for c in string if c.isprintable() and c not in illegals)

def prettify(val, splitchar: str = '\t'):
    """
    called as a beaupy.preprocessor to colour url and synopsis text.
    Format a string value with color codes.

    This function takes a string value, splits it by tab characters,
    (optionally, alllows a custom split character), 
    and formats the first part as a title with a specific color code, 
    and the second part as a synopsis with another color code. 
    If splitting fails, it returns the value formatted as a title.

    Args:
        val (str): The string value to be prettified.

    Returns:
        str: The formatted string with color codes.
    """
    try:
        parts = val.split(splitchar) 
        title = f"[#89B4FA]{parts[0]}[/]"  
        synopsis = f"[cyan]{parts[1]}[/]"  
        return f"{title}\t{synopsis}"
    except:
        return f"[#89B4FA]{val}[/]"   
def split(strng, sep, pos):

    """
    Split a string into two parts at a specified position.

    This function takes a string and splits it into two parts using a given 
    separator. It returns two substrings: the first containing the elements 
    before the specified position, and the second containing the elements 
    from the specified position onward.

    Args:
        strng (str): The input string to be split.
        sep (str): The separator to use for splitting the string.
        pos (int): The position at which to split the string.

    Returns:
        tuple: A tuple containing two strings. The first string is the 
               concatenation of elements before the specified position, 
               and the second string is the concatenation of elements 
               from the specified position onward.
    """

    strng = strng.split(sep)
    return sep.join(strng[:pos]), sep.join(strng[pos:])


'''
check for bbc 8 alpha-numerics
#https://www.bbc.co.uk/iplayer/episodes/p09pm77q/
                pattern = r'(?<!\w)(?=[a-zA-Z0-9]{8})(?![a-zA-Z]{8})[a-zA-Z0-9]{8}(?!\w)'
                # Search for the pattern in the input string
                match = re.search(pattern, search_term)

                if match:
                        return (self.fetch(search_term))
'''