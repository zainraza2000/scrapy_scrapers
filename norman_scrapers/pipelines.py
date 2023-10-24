# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
from supabase import create_client, Client
import datetime
from constants import Constants


class NormanScrapersPipeline:
    def __init__(self) -> None:
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)
        pass

    def process_item(self, item, spider):
        if item['pipeline'] == Constants.leaderboard:
            return self.leaderboard_pipeline(item)
        elif item['pipeline'] == Constants.schedule:
            return self.schedule_pipeline(item)
        elif item['pipeline'] == Constants.statistics:
            return self.statistics_pipeline(item)

    def schedule_pipeline(self, item):
        print(item)

    def statistics_pipeline(self, item):
        print(item)

    def leaderboard_pipeline(self, item):
        bulk_insert = []
        for table_rows in item['data']:
            bulk_insert.extend(self.get_objects(table_rows))
        self.insert_into_table(bulk_insert, 'PlayerStat')
        return item

    def get_objects(self, item):
        post_objs = []
        rank = int(item['Rk'])
        player = item['Name']
        team = item['team']
        date = datetime.date.today().isoformat()
        stat_type = item['stat_type']
        is_stat = False
        for key in item:
            if is_stat:
                post_objs.append({"stat_name": key, "team": team, "player": player,
                                  "value": item[key], "rank": rank, "date": date, "stat_type": stat_type})
            if key == 'team':
                is_stat = True
        return post_objs

    def insert_into_table(self, data, table_name):
        self.supabase.table(table_name).insert(
            data).execute()
