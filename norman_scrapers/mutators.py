from itemadapter import ItemAdapter
import os
from supabase import create_client, Client
import datetime
from norman_scrapers.constants import Table
from norman_scrapers.getters import Getter


class Mutator:
    def __init__(self) -> None:
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)
        self.getter = Getter()
        pass

    def create(self, data, table_name):
        self.supabase.table(table_name).insert(
            data).execute()

    def update_by_id(self, data, id, table_name):
        self.supabase.table(table_name).update(data).eq('id', id).execute()

    def create_player_stat(self, data):
        self.create(data, Table.PlayerStat.value)

    def create_game(self, data):
        self.create(data, Table.Game.value)

    def add_team(self, team_name):
        self.create({'name': team_name}, Table.Team.value)

    def update_box_score(self, game_id, box_score):
        self.update_by_id({'box_score': box_score}, game_id, Table.Game.value)

    def create_scoring(self, scoring):
        self.create(scoring, table_name=Table.Scoring.value)

    def create_statistics(self, statistics):
        self.create(statistics, table_name=Table.Statistic.value)

    def mark_scraped(self,id):
        self.update_by_id(data={"is_scraped": True},id=id,table_name=Table.Game.value)