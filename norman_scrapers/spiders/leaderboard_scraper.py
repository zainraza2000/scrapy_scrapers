import scrapy
import re
import json
from datetime import datetime
import os


class LeaderboardScraper(scrapy.Spider):
    name = 'leaderboard_scraper'
    start_urls = [
        'https://gflstats.info/sports/fball/2022-23b/players?sort=pyg&view=&pos=qb&r=0']
    final_data = []

    def click_element(self, selector):
        print(selector)

    def parse(self, response):
        stat_origins_sel = response.xpath(
            '//ul[@class="clearfix"]')[0].css('li')
        origins = []
        types = []
        for stat_origin_sel in stat_origins_sel:
            origin_name = stat_origin_sel.css('a::text').extract()[0]
            origin_ref = stat_origin_sel.css('a::attr(href)').extract()[0]
            yield response.follow(origin_ref, self.parse_secondary, meta={'origin_name': origin_name})

    def parse_secondary(self, response):
        stat_types_sel = response.xpath('//ul[@class="clearfix"]')[1].css('li')
        for stat_type_sel in stat_types_sel:
            type_name = stat_type_sel.css('a::text').extract()[0]
            type_ref = stat_type_sel.css('a::attr(href)').extract()[0]
            yield response.follow(type_ref, self.extract_data, meta={'origin_name': response.meta['origin_name'], 'type_name': type_name})

    def extract_data(self, response):
        origin_name = response.meta['origin_name']
        type_name = response.meta['type_name']
        header_selectors = response.css('thead').css('th')
        table_headers = self.get_table_headers(header_selectors)
        row_selectors = response.css('tbody').css('tr')
        self.final_data.append(
            {'stat_origin': origin_name, 'stat_type': type_name, 'table': []})
        for row_selector in row_selectors:
            self.final_data[-1]['table'].append(
                self.get_row_object(row_selector, table_headers))

    def get_table_headers(self, header_selectors):
        headers = []
        for header_selector in header_selectors:
            header_text = header_selector.css('a::text').get()
            if not header_text:
                header_text = header_selector.css('::text').get()
                if header_text == "&nbsp":
                    header_text = "team"
            headers.append(header_text.strip())
        return headers

    def get_row_object(self, row_selector, table_headers):
        data_selectors = row_selector.css('td')
        if len(table_headers) != len(data_selectors.getall()):
            raise ValueError(
                "table_headers and row_selector arrays must have the same length")
        i = 0
        result = {}
        for data_selector in data_selectors:
            data_text = data_selector.css('a::text').get()
            if not data_text:
                data_text = data_selector.css('::text').get()
            result[table_headers[i]] = self.get_cleaned_text(data_text)
            i += 1
        return result

    def get_cleaned_text(self, text):
        cleaned_string = re.sub(r'\s+', ' ', text.strip())
        return cleaned_string

    def create_json_file(self):
        current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'leaderboard_data_{current_datetime}.json'
        results_dir = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), 'results')
        os.makedirs(results_dir, exist_ok=True)
        filepath = os.path.join(results_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as json_file:
            json.dump(self.final_data, json_file, ensure_ascii=False, indent=4)

    def closed(self, reason):
        if reason == 'finished':
            self.create_json_file()
