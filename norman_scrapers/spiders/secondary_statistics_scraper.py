import scrapy
from datetime import datetime
from datetime import datetime, timedelta
from norman_scrapers.constants import Pipeline, StatType, Table
import re
from norman_scrapers.utils import extract_integer

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
        yield response.follow(self.stats_url, self.secondary_stats)

    def secondary_stats(self, response):
        tab_selectors = response.xpath("//ul[@class='clearfix']").css('li')
        for tab_selector in tab_selectors:
            tab_name_raw = tab_selector.css('a::text').get()
            if tab_name_raw:
                tab_name = tab_name_raw.strip().lower()
            else:
                tab_name = ''
            if tab_name in self.required_tabs:
                yield response.follow(tab_selector.css('a::attr(href)').get(), self.extract_stats, meta={'tab_name': tab_name}, dont_filter=True)

    def extract_stats(self, response):
        tab_name = response.meta['tab_name']
        drive_summary = []
        starters = []
        play_by_play = []
        scoring_summary = []
        if tab_name == 'box score':
            scoring_summary = self.get_scoring_summary(response)
            if scoring_summary:
                yield {'data': scoring_summary, 'table': Table.ScoringSummary.value,
                       'pipeline': Pipeline.statistics.value, 'type': StatType.secondary.value}
        elif tab_name == 'drive summary':
            drive_summary = self.get_drive_summary(response)
            if drive_summary:
                yield {'data': drive_summary, 'table': Table.DriveSummary.value,
                       'pipeline': Pipeline.statistics.value, 'type': StatType.secondary.value}
        elif tab_name == 'starters':
            starters = self.get_starters(response)
            if starters:
                yield {'data': starters, 'table': Table.Starters.value,
                       'pipeline': Pipeline.statistics.value, 'type': StatType.secondary.value}
        elif tab_name == 'play by play':
            play_by_play = self.get_play_by_play(response)
            if play_by_play:
                yield {'data': play_by_play, 'table': Table.PlayByPlay.value,
                       'pipeline': Pipeline.statistics.value, 'type': StatType.secondary.value}

    def get_scoring_summary(self, response):
        try:
            data = []
            scoring_summary_table = None
            tables = response.xpath('//div[@class="stats-fullbox clearfix"]')
            for table in tables:
                if "Scoring Summary" in table.get():
                    scoring_summary_table = table
            if scoring_summary_table == None:
                return None
            table_rows = scoring_summary_table.css('tr')[1:]
            for row in table_rows:
                try:
                    row_text = row.css("td::text").getall()
                    prd = row_text[0].strip()
                    time = row_text[1].strip()
                    team = row.css("strong::text").get()
                    if len(row_text) == 5:
                        scoring_summary_rows = [row_text[3]]
                        score_row = row_text[4]
                    else:
                        scoring_summary_rows = [row_text[3],row_text[4]]
                        score_row = row_text[5]
                    scoring_summary = team + ' '
                    for row in scoring_summary_rows:
                        scoring_summary += row.strip().replace('\n', ' ')
                    away_score = score_row.split('-')[0].strip()
                    home_score = score_row.split('-')[1].strip()
                    data.append({'prd': prd, 'time': time, 'team': team,
                                'scoring_summary': scoring_summary, 'away_score': away_score, 'home_score': home_score, 'game_id': self.game_id})
                except:
                    continue
            return data
        except Exception as e:
            print(f'exception-------{e}')
            return None

    def get_drive_summary(self, response):
        try:
            data = []
            table_rows = response.xpath("//table")[2].css("tbody").css("tr")
            for table_row in table_rows:
                team = table_row.xpath(".//td[@class='drive-team-name']/text()").get().strip()
                quarter = extract_integer(table_row.xpath(".//td/text()")[1].get().strip())
                start = table_row.xpath(".//td/text()")[2].get().strip()
                poss = table_row.xpath(".//td/text()")[3].get().strip()
                began = table_row.xpath(".//td/text()")[4].get().strip()
                plays = extract_integer(table_row.xpath(".//td/text()")[5].get().strip())
                yards = extract_integer(table_row.xpath(".//td/text()")[6].get().strip())
                result = table_row.xpath(".//td/text()")[7].get().strip()
                data.append({"game_id": self.game_id, "team": team, "quarter": quarter, "start": start, "poss": poss, "began": began, "plays": plays,"yards": yards, "result": result})
            return data
        except Exception as e:
            print(f'exception-------{e}')
            return None

    def get_starters(self, response):
        try:
            data = []
            left_table_rows = response.xpath('//div[@class="stats-halfbox-left"]').css("table").css("tr")
            right_table_rows = response.xpath('//div[@class="stats-halfbox-right"]').css("table").css("tr")
            left_team = left_table_rows[0].css("td").css("h4::text").get().strip()
            right_team = right_table_rows[0].css("td").css("h4::text").get().strip()
            left_position = left_table_rows[1].css("th::text").get().strip()
            right_position = right_table_rows[1].css("th::text").get().strip()
            for table_row in left_table_rows[2:]:
                if table_row.css("th").get():
                    left_position = table_row.css("th::text").get().strip()
                    continue
                player = table_row.css("td::text").getall()[1]
                data.append({"game_id": self.game_id,"team": left_team,"position": left_position,"player": player})
            for table_row in right_table_rows[2:]:
                if table_row.css("th").get():
                    right_position = table_row.css("th::text").get().strip()
                    continue
                player = table_row.css("td::text").getall()[1]
                data.append({"game_id": self.game_id,"team": right_team,"position": right_position,"player": player})
            return data
        except Exception as e:
            print(f'exception-------{e}')
            return None
            

    def get_play_by_play(self, response):
        try:
            data = []
            table_rows = response.xpath('//div[@class="table-responsive"]')[2].css("table").css("tr")
            quarter = extract_integer(table_rows[1].css("td").css("div::text").get().strip())
            for table_row in table_rows[2:]:
                if '"odd' in table_row.get() or '"even' in table_row.get():
                    columns_text = table_row.css("td::text").getall()
                    if len(columns_text) > 1:
                        short_description = columns_text[0].strip() 
                        description = columns_text[1].strip()
                        data.append({"game_id": self.game_id,"quarter": quarter,"short_description": short_description,"description": description})
                    continue
                if table_row.css("th").get() or table_row.css("a").get():
                    continue
                if '"qtr' in table_row.css("td").get():
                    quarter = extract_integer(table_row.css("td").css("div::text").get().strip())
            return data
        except Exception as e:
            print(f'exception-------{e}')
            return None



