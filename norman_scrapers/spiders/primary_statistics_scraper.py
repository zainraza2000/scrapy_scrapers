import scrapy
from datetime import datetime
from datetime import datetime, timedelta
from norman_scrapers.constants import Pipeline, StatType
from norman_scrapers.getters import Getter
import sys


class StaisticsScraper(scrapy.Spider):
    name = 'primary_statistics_scraper'
    start_urls = [
        'https://gflstats.info/sports/fball/2022-23b/schedule']
    base_url = "https://gflstats.info"

    def __init__(self, url, game_id, *args, **kwargs):
        super(StaisticsScraper, self).__init__(*args, **kwargs)
        self.stats_url = url
        self.game_id = game_id

    def parse(self, response):
        yield response.follow(self.stats_url, self.box_score_stats)

    def box_score_stats(self, response):
        try:
            scoring_data = []
            statistics = []
            away_scores = response.xpath(
                '//div[@class="stats-fullbox clearfix"]')[0].css('tr')[1].css('td::text')[1:].getall()
            home_scores = response.xpath(
                '//div[@class="stats-fullbox clearfix"]')[0].css('tr')[2].css('td::text')[1:].getall()
            for quarter in range(1, 5):
                try:
                    home_score = home_scores[quarter-1]
                except:
                    home_score = None
                try:
                    away_score = away_scores[quarter-1]
                except:
                    away_score = None
                scoring_data.append({'game_id': self.game_id, 'quarter': quarter,
                                    'home_score': home_score, 'away_score': away_score})
            stat_table_rows = response.xpath(
                "//table[@class='table  all-center']").css('tr')[1:]
            for row in stat_table_rows:
                data = {}
                if '<br>' in row.get():
                    data = self.get_multirow_data(row)
                else:
                    data = self.get_single_row_data(row)
                statistics.extend(data)
            yield {'scoring': scoring_data, 'statistics': statistics,
                   'pipeline': Pipeline.statistics.value, 'type': StatType.primary.value}
        except:
            return

    def get_multirow_data(self, row):
        try:
            stats = []
            row_data = row.css('td::text').getall()
            offset = int(len(row_data) / 3)
            for i in range(0, offset):
                stats.append({'game_id': self.game_id, 'stat_type': row_data[i+offset].lower(), 'away_value':
                              row_data[i].strip(), 'home_value': row_data[i+(offset*2)].strip()})
            return stats
        except Exception as e:
            return [{}]

    def get_single_row_data(self, row):
        try:
            row_data = row.css('td::text').getall()
            return [{'game_id': self.game_id, 'stat_type': row_data[1].lower(), 'away_value': row_data[0].strip(), 'home_value': row_data[2].strip()}]
        except:
            return [{}]
