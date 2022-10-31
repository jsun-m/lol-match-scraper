import json
import logging
import time

from http import HTTPStatus
from typing import List
import requests

log = logging.getLogger("spider")
log.setLevel(logging.DEBUG)

NA_BASE_URL = "https://na1.api.riotgames.com/lol"
AMERICAS_BASE_URL = "https://americas.api.riotgames.com/lol"
TOKEN =  "RGAPI-17297ff8-bfbf-44a0-adb5-4949538494ea"
MAX_DEPTH = 2

class LeagueSpider:
    def __init__(self):
        self.match_data = {}
        self.user_frontier = set()

        self.etiquette_counter = 0
        self.etiquette_timer = time.time()

    def _make_request(self, endpoint: str):
        response = requests.get(
            url=endpoint,
            headers={
                "X-Riot-Token": TOKEN
            }
        )

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            print("Rate limit exceeded. Sleeping for 2 minutes")
            time.sleep(130)

        response = requests.get(
            url=endpoint,
            headers={
                "X-Riot-Token": TOKEN
            }
        )

        return response

    def _request_match_base_url(self):
        return f"{AMERICAS_BASE_URL}/match/v5/matches"

    def _request_summoner_base_url(self):
        return f"{NA_BASE_URL}/summoner/v4/summoners"

    def get_summoner_data_by_name(self, summonerName: str):
        response = self._make_request(
            f"{self._request_summoner_base_url()}/by-name/{summonerName}"
        )

        if response.status_code != HTTPStatus.OK:
            print(response.content)
            return None

        return response.json()

    def get_match_data_of_user(self, userPuuid: str):
        response = self._make_request(
            f"{self._request_match_base_url()}/by-puuid/{userPuuid}/ids"
        )

        if response.status_code != HTTPStatus.OK:
            return None
        
        match_list: List[str] = response.json()
        matches_to_parse = {}

        for match in match_list:
            if match in self.match_data:
                continue

            print(f"GET Match matchId:{match}")
            match_response = self._make_request(
                f"{self._request_match_base_url()}/{match}"
            )

            if response.status_code != HTTPStatus.OK:
                print(f"Unable to GET Match matchId:{match}")
                continue
            
            matches_to_parse[match] = match_response.json()
            self.match_data[match] = matches_to_parse[match]

        return matches_to_parse
    
    def crawl(self, summoner_puuid: str, depth: int):
        print(f"Crawling user: {summoner_puuid} at current total match data of {len(self.match_data)}")

        if depth == MAX_DEPTH:
            return

        if summoner_puuid in self.user_frontier:
            return
        
        self.user_frontier.add(summoner_puuid)
        match_dict = self.get_match_data_of_user(summoner_puuid)

        if match_dict == None:
            return

        for match in match_dict.values():
            metadata = match.get("metadata")

            if metadata is None:
                print("Metadata not found:", match)
                continue

            participants = metadata["participants"]

            if participants is None:
                print("Participants not found", metadata)
                continue

            for p in participants:
                self.crawl(p, depth + 1)


    def start_crawl(self, starting_summoner_name: str):
        puuid = self.get_summoner_data_by_name(starting_summoner_name)["puuid"]
        self.crawl(puuid, 0)
        self.save_data()
    
    def save_data(self, to: str = "data.json"):
        with open(to, "w+") as f:
            f.write(json.dumps(self.match_data))

    