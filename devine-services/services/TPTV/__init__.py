from __future__ import annotations

import json
import re
from collections.abc import Generator
from http.cookiejar import MozillaCookieJar
from typing import Any, Optional, Union
import click
from click import Context
from devine.core.credential import Credential
from devine.core.manifests.dash import DASH
from devine.core.search_result import SearchResult
from devine.core.service import Service
from devine.core.titles import Episode, Movie, Movies, Series
from devine.core.tracks import Chapters, Subtitle, Tracks
import requests


class TPTV(Service):
    """
    Service code for TPTVencore streaming service (https://www.TPTVencore.co.uk/).

    \b
    version 1.0.1  
    Date: June 2025
    Author: A_n_g_e_l_a
    Authorization: email/password for service in devine.yaml
    Robustness:
        DRM free.

    \b
    Note:
        TPTV will not allow the usual -w S01-S04 syntax as TPTV is eclictic in what it serves. 
        Series and episodes carry little meaning on this platform.

        It is not possible to remove S00E00 from the end of a video title - devine insists.

    \b
    Tips:
        Use complete url in all cases.
        SERIES: https://tptvencore.co.uk/collection/1717422888871355373
        Note: TPTV do not specify Series and Episodes numbers in any meaningful and organized way. 
        They MAY sometimes be in the program title, but often incomplete. 
        FILM: https://tptvencore.co.uk/product/the-importance-of-being-earnest-6290333578001
        EPISODE: https://tptvencore.co.uk/product/sherlock-holmes---the-case-of-greystone-inscription-s1-ep16-6282604132001

    \b
    Examples:
        SERIES: https://tptvencore.co.uk/collection/1717422888871355373
        EPISODE: https://tptvencore.co.uk/product/sherlock-holmes---the-case-of-greystone-inscription-s1-ep16-6282604132001
        FILM: https://tptvencore.co.uk/product/the-importance-of-being-earnest-6290333578001

    """

    GEOFENCE = ("gb",)
    ALIASES = ("TPTVencore",)

    @staticmethod
    @click.command(name="TPTV", short_help="https://www.tptvencore.co.uk/", help=__doc__)
    @click.argument("title", type=str)
    @click.pass_context
    def cli(ctx: Context, **kwargs: Any) -> TPTV:
        return TPTV(ctx, **kwargs)

    def __init__(self, ctx: Context, title: str):
        self.title = title
        super().__init__(ctx)

        self.profile = ctx.parent.params.get("profile")
        if not self.profile:
            self.profile = "default"

        self.session.headers.update(self.config["headers"])

    def authenticate(self, cookies: Optional[MozillaCookieJar] = None, credential: Optional[Credential] = None) -> None:
        super().authenticate(cookies, credential)
        if not credential:
            raise EnvironmentError("Service requires Credentials for Authentication.")

        cache = self.cache.get(f"tokens_{credential.sha1}")
        # first contact
        fc_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0',
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en;q=0.5',
            'api-key': 'zq5pyPd0RTbNg3Fyj52PrkKL9c2Af38HHh4itgZTKDaCzjAyhd',
            'Referer': 'https://tptvencore.co.uk/',
            'tenant': 'encore',
            'Content-Type': 'application/json',
            'Origin': 'https://tptvencore.co.uk',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Priority': 'u=0',

            }
        payload = {}
        r = self.session.post(self.config["endpoints"]["session"], headers=fc_headers, json=payload)
        if r.status_code != 200:
            raise ConnectionError   
        else:
            session_id = r.json()['id']
            self.session.headers.update({'session': session_id})
        
        # login
        if cache and not cache.expired:
            # cached
            self.log.info(" + Using cached Tokens...")
            tokens = cache.data
        else:
            self.log.info(" + Logging in...")
            payload = {"email": credential.username, "password": credential.password}
            
            r = self.session.post(
                self.config["endpoints"]["login"],
                headers=self.session.headers,
                json={
                    "email": credential.username,
                    "password": credential.password,
                },
            )
            try:
                res = r.json()
            except json.JSONDecodeError:
                raise ValueError(f"Failed to refresh tokens: {r.text}")

            tokens = res
            self.log.info(" + Acquired tokens...")

        cache.set(tokens)

        self.authorization = tokens

    def search(self) -> Generator[SearchResult, None, None]:
        query = self.title.replace(" ", "+")
        search_url = self.config["endpoints"]["search"].replace("{query}", query)
        session_id = self.session.headers['session']
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0',
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Referer': 'https://tptvencore.co.uk/',
            'session': session_id,
            'tenant': 'encore',
            'Origin': 'https://tptvencore.co.uk',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Priority': 'u=4',
        }
        r = self.session.get(search_url, headers=headers)
        if r.status_code != 200:
            raise ConnectionError(f"Search failed with {r.status_code}: {r.text}")     

        results = r.json()["data"]
        myitems = [] 
        if isinstance(results, list):
            for result in results:
                # do lookup on list item product or collection    
                if  result.startswith('collection_'):
                    id = result.replace('collection_','')
                    collection_url = f"https://prod.suggestedtv.com/api/client/v1/collection/by-reference/{id}?extend=label"
                    response = self.session.get(collection_url, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        for item in data['children']:        
                            myitems.append(item['id'].replace('product_',''))
                    else:
                        print(f"Error: {response.status_code} - {response.text}")
                else:
                    myitems.append(result.replace('product_',''))
                    mystring = ",".join(myitems)
                
            continued_search_url = "https://prod.suggestedtv.com/api/client/v1/product?ids=" + mystring + "&extend=label"
            
            response = self.session.get(continued_search_url, headers=headers)
            response.raise_for_status
            results = response.json()
            if isinstance(results, list):
                items = results  
            elif isinstance(results, dict) and "data" in results:
                items = results["data"]
            else:
                raise ValueError("Unexpected search result format")

            for item in items:
                try:
                    yield SearchResult(
                        id_=item.get("reference"),
                        title=item.get("name"),
                        description=item.get("description", "").replace('\n', ' '),
                        label=item.get("type", ""),
                        url=f"https://tptvencore.co.uk/product/{item.get('reference')}",
                    )
                except Exception as e:
                    print(f"Failed to yield item: {e}")

    def get_titles(self) -> Union[Movies, Series]:
        data = self.get_data(self.title)
        ids = ",".join(data)

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0',
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Referer': 'https://tptvencore.co.uk/',
            'tenant': 'encore',
            'Origin': 'https://tptvencore.co.uk',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Priority': 'u=4',
        }
        session_id = self.session.headers['session']
        headers['session'] = session_id
        params = {
            'ids': ids,
            'extend': 'label',
        }

        response = self.session.get('https://prod.suggestedtv.com/api/client/v1/product', params=params, headers=headers)
        if response.status_code == 200:
            mydata=json.loads(response.text)
            titles = mydata['data']
            episodes =[
                    Episode(
                        id_=episode["id"],
                        service=self.__class__,
                        title=episode["name"],
                        season=0,
                        number=0,
                        name = '',
                        language="en",  # TODO: language detection
                        data=episode,
                    )
                    for episode in titles
                ]
            return Series(episodes)


    def get_tracks(self, title: Union[Movie, Episode]) -> Tracks:
        playlist = f"https://edge.api.brightcove.com/playback/v1/accounts/6272132012001/videos/{title.data.get("id")}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0',
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en;q=0.5',
      
            'Referer': 'https://tptvencore.co.uk/',
            'BCOV-Policy': 'BCpkADawqM1yq3Go9abHJ4lBZ0wrYStC-pS1W01hdlACHxsiIz9AvQXy1wa3iqyd6yVJLXLZnZjFkKI2BCJjbtxiJqyPMZjIezEWKrI1TTSbugkD6dAXs7Ucxq09P9zQ8ZRU4ZjTa83VFhiL',
            'Origin': 'https://tptvencore.co.uk',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Priority': 'u=4',
        }

        r = requests.get(playlist, headers=headers)
        if r.status_code != 200:
            raise ConnectionError(r.text)

        data = r.json()
        
        self.manifest = data["sources"][2].get("src")

        tracks = DASH.from_url(self.manifest, self.session).to_tracks(title.language)
        tracks.videos[0].data = data
        
        # odd couple of DRM vids found
        pattern = re.compile(r'bc:licenseAcquisitionUrl="([^"]+)"')
        m = pattern.search(r.text)
        if m:
            self.license = m.group(1)
        else:                   
            self.license = None

        # sub was picking up thumbnails
        subtitles_data = data['text_tracks']
        for subs in subtitles_data:
            if subs['label'] == 'thumbnails':
                subtitles = None
                continue
            else:
                subtitles = subs
                break

        if subtitles is not None:
                # correction for None type error
                lang = subtitles["srclang"]
                if lang == None:
                    lang = 'en'
                
                tracks.add(
                    Subtitle(
                        id_= subtitles.get("id"),
                        url= subtitles.get("src", ""),
                        codec= Subtitle.Codec.from_mime(subtitles.get("mime_type")[-3:]),
                        language = lang,
                        forced=False,)
                    )   
        return tracks

    def get_chapters(self, title: Union[Movie, Episode]) -> Chapters:
      
        return Chapters()

    def get_widevine_service_certificate(self, **_: Any) -> str:
        return None

    def get_widevine_license(self, challenge: bytes, **_: Any) -> bytes:
        r = self.session.post(url=self.license, data=challenge)
        if r.status_code != 200:
            raise ConnectionError(r.text)
        return r.content

    def get_data(self, url: str) -> dict:
        self.session.headers.update({'tenant': 'encore'})
        if 'collection' in url:
            prod_id = url.split('/')[-1]
            url = f"https://prod.suggestedtv.com/api/client/v1/collection/by-reference/{prod_id}?extend=label"
            r = self.session.get(url)
            if r.status_code != 200:
                raise ConnectionError(r.text)
            
            myjson = r.json()
            children = myjson.get('children')
            product_links = []
            for child in children:
                product_links.append(child['id']) if 'product' in child.get('classification') else None
            return product_links
        elif 'product' in url:  # single item
            prod_id = url.split('-')[-1] 
            return [prod_id]
