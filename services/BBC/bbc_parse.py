from scrapy import Selector
import json
from httpx import Client
from rich.console import Console
console = Console()


def bbc_extract_application_json(html, discriminator="application/ld+json", index=1):
    """
    Extract the JSON data from the HTML content that is stored in the
    script tag of type 'application/ld+json'.
    
    Args:
        html (str): The HTML content from which to extract the JSON data.
        discriminator (str): The content type to search for.
        index (int): The index of the script tag to extract.
        
    Returns:
        dict: The parsed JSON data, or None if no matching script was found,
              or if the JSON could not be parsed.
    """
    try:
        # Use Scrapy's Selector to locate the script tag
        sel = Selector(text=html)

        # Extract all script tags with the type 'application/ld+json'
        scripts = sel.xpath(f'//script[@type="{discriminator}"]/text()').getall()

        if not scripts:
            print("No scripts of type 'application/ld+json' found.")
            return None

        if 0 <= index < len(scripts):
            selected_script = scripts[index]
        else:
            return None

        # Parse the JSON directly from the script content
        parsed_json = json.loads(selected_script)

        return parsed_json

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
def get_data( url, headers=None):
        """Fetch data from a given URL."""
        if not headers:
            headers = headers
        response = client.get(url, headers=headers, follow_redirects=True)
        if response.status_code != 200:
            raise Exception("Failed to retrieve data.")
        return response.text  


if __name__ == "__main__":
    # say hello
    client = Client()
    prog_json = get_data("https://www.bbc.co.uk/programmes/p09pm77q.json")

    prog_json = json.loads(prog_json)
    #object►programme►aggregated_episode_count 
    aggregated_episode_count = prog_json['programme']['aggregated_episode_count']
    print(aggregated_episode_count)
    episode_count = 0
    page = 0
    while episode_count < aggregated_episode_count:
        # https://www.bbc.co.uk/programmes/p09pm77q/episodes/player?page=1
        try:
            ep_data_html = get_data(f"https://www.bbc.co.uk/programmes/p09pm77q/episodes/player?page={page +1}")
            ep_data_json = bbc_extract_application_json(ep_data_html, "application/ld+json", 1)
            console.print_json(data=ep_data_json)
            '''for episode in ep_data['programme']['episodes']:
                episode_count += 1
                print(episode_count, episode['title'], episode['url'])'''
            page += 1
        except:
            break
