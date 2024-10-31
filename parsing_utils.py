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
