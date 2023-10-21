import scrapy
import re
import json
from datetime import datetime
import os
from norman_scrapers.items import LeaderBoardItem


class LeaderboardScraper(scrapy.Spider):
    name = 'leaderboard_scraper'
    start_urls = [
        'https://gflstats.info/sports/fball/2022-23b/players?sort=pyg&view=&pos=qb&r=0']
    final_data = []

    def click_element(self, selector):
        print(selector)

    def parse(self, response):
        # initial function iterating through the stat origins(Overall & Conference)
        stat_origins_sel = response.xpath(
            '//ul[@class="clearfix"]')[0].css('li')
        origins = []
        types = []
        for stat_origin_sel in stat_origins_sel:
            origin_name = stat_origin_sel.css('a::text').extract()[0]
            origin_ref = stat_origin_sel.css('a::attr(href)').extract()[0]
            yield response.follow(origin_ref, self.iterate_stat_types, meta={'origin_name': origin_name})

    def iterate_stat_types(self, response):
        # iterating through href of each stat type for each stat origin
        stat_types_sel = response.xpath('//ul[@class="clearfix"]')[1].css('li')
        for stat_type_sel in stat_types_sel:
            type_name = stat_type_sel.css('a::text').extract()[0]
            type_ref = stat_type_sel.css('a::attr(href)').extract()[0]
            yield response.follow(type_ref, self.extract_table_data, meta={'origin_name': response.meta['origin_name'], 'type_name': type_name})

    def extract_table_data(self, response):
        # getting the table data for each combination of stat origin and stat type (e.g Overall Passing)
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
        item = LeaderBoardItem()
        item['stat_origin'] = self.final_data[-1]['stat_origin']
        item['stat_type'] = self.final_data[-1]['stat_type']
        item['table'] = self.final_data[-1]['table']
        yield item

    def get_table_headers(self, header_selectors):
        # getting column names of the table
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
        # getting an object consisting of data in a single row
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
        # cleaning the data
        if text:
            cleaned_string = re.sub(r'\s+', ' ', text.strip())
            return cleaned_string
        else:
            return text

    def create_json_file(self):
        current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'leaderboard_data_{current_datetime}.json'
        downloads_dir = os.path.expanduser("~\\Downloads")
        filepath = os.path.join(downloads_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as json_file:
            json.dump(self.final_data, json_file, ensure_ascii=False, indent=4)

    def closed(self, reason):
        # called when spider closes
        if reason == 'finished':
            self.create_json_file()
