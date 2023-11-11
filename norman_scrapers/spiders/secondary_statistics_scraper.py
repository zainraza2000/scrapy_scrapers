import scrapy
from datetime import datetime
from datetime import datetime, timedelta
from norman_scrapers.constants import Pipeline, StatType, Table


class SecondaryStaisticsScraper(scrapy.Spider):
    name = 'secondary_statistics_scraper'
    start_urls = [
        'https://gflstats.info/sports/fball/2022-23b/schedule']
    base_url = "https://gflstats.info"
    required_tabs = ['box score', 'play by play', 'drive summary', 'starters']

    def __init__(self, url, game_id, *args, **kwargs):
        super(SecondaryStaisticsScraper, self).__init__(*args, **kwargs)
        self.stats_url = url
        self.game_id = game_id

    def parse(self, response):
        tab_selectors = response.xpath("//ul[@class='clearfix']").css('li')
        for tab_selector in tab_selectors:
            tab_name_raw = tab_selector.css('a::text').get()
            if tab_name_raw:
                tab_name = tab_name_raw.strip().lower()
            else:
                tab_name = ''
            if tab_name in self.required_tabs:
                yield response.follow(tab_selector.css('a::attr(href)').get(), self.extract_stats, meta={'tab_name': tab_name})

    def extract_stats(self, response):
        tab_name = response.meta['tab_name']
        drive_summary = []
        starters = []
        play_by_play = []
        scoring_summary = []

        if tab_name == 'box score':
            scoring_summary = self.get_scoring_summary(response)
            yield {'data': scoring_summary, 'table': Table.ScoringSummary.value,
                   'pipeline': Pipeline.statistics.value, 'type': StatType.secondary.value}
        elif tab_name == 'drive summary':
            drive_summary = self.get_drive_summary(response)
            yield {'data': drive_summary, 'table': Table.DriveSummary.value,
                   'pipeline': Pipeline.statistics.value, 'type': StatType.secondary.value}
        elif tab_name == 'starters':
            starters = self.get_starters(response)
            yield {'data': starters, 'table': Table.Starters.value,
                   'pipeline': Pipeline.statistics.value, 'type': StatType.secondary.value}
        elif tab_name == 'play by play':
            play_by_play = self.get_play_by_play(response)
            yield {'data': play_by_play, 'table': Table.PlayByPlay.value,
                   'pipeline': Pipeline.statistics.value, 'type': StatType.secondary.value}

    def get_scoring_summary(self, response):
        print(response)

    def get_drive_summary(self, response):
        print(response)

    def get_starters(self, response):
        print(response)

    def get_play_by_play(self, response):
        print(response)
