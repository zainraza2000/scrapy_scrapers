import os
from supabase import create_client, Client
from norman_scrapers.constants import Table
import datetime


class Getter:
    def __init__(self) -> None:
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)
        pass

    def get_latest_games(self):
        data, count = self.supabase.table(
            Table.Game.value).select('*').eq('is_scraped', False).neq('box_score', None).execute()
        print(data, count)

    def get_game_stats_by_date(self, date):
        data, count = self.supabase.table(
            Table.PlayerStat.value).select('*').eq('date', date).execute()
        return data[1]

    def get_all_teams(self):
        data, count = self.supabase.table(
            Table.Team.value).select('*').execute()
        return data[1]

    def get_team(self, team_name):
        data, count = self.supabase.table(Table.Team.value).select(
            '*').eq('name', team_name).execute()
        if len(data[1]) > 0:
            return data[1][0]
        return data[1]

    def get_pending_games(self):
        data, count = self.supabase.table(Table.Game.value).select(
            '*').eq('is_scraped', False).eq('box_score', '-').execute()
        return data[1]

    def get_unscraped_box_scores(self):
        data, count = self.supabase.table(Table.Game.value).select(
            'id,box_score').eq('is_scraped', False).neq('box_score', '-').execute()
        return data[1]
