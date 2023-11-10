# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
import datetime
from norman_scrapers.constants import Pipeline, Table
from norman_scrapers.getters import Getter
from norman_scrapers.pipeline.leaderboard_pipeline import LeaderboardPipeline
from norman_scrapers.pipeline.schedule_pipeline import SchedulePipeline
from norman_scrapers.pipeline.statistics_pipeline import StatisticsPipeline

import json


class NormanScrapersPipeline:
    def __init__(self) -> None:
        self.getter = Getter()
        self.team_dict = {}
        for team in self.getter.get_all_teams():
            name = team['name'].lower()
            id = team['id']
            self.team_dict[name] = id
        self.leaderboard_pipeline = LeaderboardPipeline()
        self.schedule_pipeline = SchedulePipeline(self.team_dict)
        self.statistics_pipeline = StatisticsPipeline(self.team_dict)
        pass

    def process_item(self, item, spider):
        if item['pipeline'] == Pipeline.leaderboard.value:
            return self.leaderboard_pipeline.process_data(item)
        elif item['pipeline'] == Pipeline.schedule.value:
            return self.schedule_pipeline.process_data(item)
        elif item['pipeline'] == Pipeline.statistics.value:
            return self.statistics_pipeline.process_item(item)
