# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
import datetime
from norman_scrapers.constants import Pipeline, Table
from norman_scrapers.mutators import Mutator
from norman_scrapers.getters import Getter
import json


class NormanScrapersPipeline:
    def __init__(self) -> None:
        self.mutator = Mutator()
        self.getter = Getter()
        self.team_dict = {}
        for team in self.getter.get_all_teams():
            name = team['name'].lower()
            id = team['id']
            self.team_dict[name] = id
        pass

    def process_item(self, item, spider):
        if item['pipeline'] == Pipeline.leaderboard.value:
            return self.leaderboard_pipeline(item)
        elif item['pipeline'] == Pipeline.schedule.value:
            return self.schedule_pipeline(item)
        elif item['pipeline'] == Pipeline.statistics.value:
            return self.statistics_pipeline(item)

    def schedule_pipeline(self, item):
        if item['is_first']:
            game_data = []
            for game in item['data']:
                game_data.append(self.get_game_object(game))
            self.mutator.create_game(game_data)
        else:
            pending_games = self.getter.get_pending_games()
            self.get_box_score_games(pending_games, item['data'])
        return item

    def statistics_pipeline(self, item):
        print(item)

    def leaderboard_pipeline(self, item):
        bulk_insert = []
        for table_rows in item['data']:
            bulk_insert.extend(self.get_objects(table_rows))
        self.mutator.create_player_stat(bulk_insert)
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

    def get_team_id(team_name, teams):
        for team in teams:
            if team.get('name').lower() == team_name:
                return team['id']

    def get_game_object(self, data):
        try:
            away_team_id = self.team_dict[data.get('away_team').lower()]
        except:
            away_team_id = self.handle_new_team(data.get('away_team'))
        try:
            home_team_id = self.team_dict[data.get('home_team').lower()]
        except:
            home_team_id = self.handle_new_team(data.get('home_team'))
        data.pop('away_team', None)
        data.pop('home_team', None)
        data['away_team_id'] = away_team_id
        data['home_team_id'] = home_team_id
        return data

    def handle_new_team(self, team_name):
        self.mutator.add_team(team_name)
        new_team = self.getter.get_team(team_name)
        if new_team:
            return new_team['id']
        return None

    def get_box_score_games(self, pending_games, scraped_games):
        filtered_games = list(
            filter(lambda scraped_game: scraped_game['box_score'] != '-', scraped_games))
        for game in filtered_games:
            box_score_game = self.is_box_score(
                self.team_dict[game['away_team'].lower()], self.team_dict[game['home_team'].lower()], game['date'], pending_games)
            if box_score_game:
                print("Updating --------", box_score_game, game)
                self.mutator.update_box_score(
                    box_score_game['id'], game['box_score'])

    def is_box_score(self, away_team_id, home_team_id, date, pending_games):
        for pending_game in pending_games:
            if pending_game['away_team_id'] == away_team_id and pending_game['home_team_id'] == home_team_id and pending_game['date'] == date and pending_game['box_score'] == '-':
                return pending_game
        return None
