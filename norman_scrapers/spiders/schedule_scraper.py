import scrapy
from datetime import datetime
from datetime import datetime, timedelta
from norman_scrapers.constants import Pipeline
from norman_scrapers.utils import string_to_timestamp
import sys


class ScheduleScraper(scrapy.Spider):
    name = 'schedule_scraper'
    start_urls = [
        'https://gflstats.info/sports/fball/2022-23b/schedule']
    base_url = "https://gflstats.info"

    def __init__(self, is_first='false', *args, **kwargs):
        super(ScheduleScraper, self).__init__(*args, **kwargs)
        self.is_first = bool(is_first.lower() == 'true')

    def parse(self, response):
        games_by_months = response.xpath("//tbody[@class='event-group']")
        for games_by_month in games_by_months:
            month_name = games_by_month.xpath(
                ".//tr[@class='month-title bg-primary text-light']").css('div::text').get()
            for req in self.iterate_games_by_month(month_name, games_by_month):
                yield req

    def iterate_games_by_month(self, month_name, games_by_month):
        game_selectors = games_by_month.css("tr")
        games = []
        current_date = ''
        for game_selector in game_selectors:
            if ('class="event-row away' in game_selector.get()):
                date = game_selector.css("td::text").get().strip()
                if date:
                    current_date = date.strip()
                game = self.extract_game_data(
                    month_name, current_date, game_selector)
                if game:
                    games.append(game)
        yield {"data": games, "pipeline": Pipeline.schedule.value, "is_first": self.is_first}

    def extract_game_data(self, month, date, game_selector):
        away_team = game_selector.css("td.team.awayteam").css(
            "span.font-weight-normal::text").get()
        if away_team:
            away_team = away_team.strip()
        else:
            return
        away_score = game_selector.css("td.e_result.e_awayresult::text").get()
        if away_score is None:
            away_score = game_selector.css(
                "td.e_result.e_awayresult.winner::text").get()
        if away_score:
            away_score = away_score.strip()
        home_team = game_selector.css(
            "td.team.hometeam::text").getall()[1].strip()
        home_score = game_selector.css(
            "td.result.homeresult::text").get()
        if home_score is None:
            home_score = game_selector.css(
                "td.result.homeresult.winner::text").get()
        if home_score:
            home_score = home_score.strip()
        status = game_selector.css("td.status::text").get()
        if status:
            status = status.strip()
        links = game_selector.css("td.links")
        box_score = '-'
        for link in links:
            try:
                if ('box' in link.xpath(".//span[@class='text d-md-none d-lg-inline-block']/text()").get().lower()):
                    box_score = link.css("a::attr(href)").get()
            except:
                break
        if box_score and box_score != '-':
            box_score = self.base_url + box_score
        return {'away_team': away_team, 'away_score': away_score, 'home_team': home_team, 'home_score': home_score, 'status': status, 'box_score': box_score, 'date': string_to_timestamp(f'{month}, {date}')}
