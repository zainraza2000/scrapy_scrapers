import datetime
from norman_scrapers.mutators import Mutator
from norman_scrapers.getters import Getter


class LeaderboardPipeline:
    def __init__(self,team_dict) -> None:
        self.mutator = Mutator()
        self.getter = Getter()
        self.team_dict = team_dict

    def process_data(self, item):
        bulk_insert = []
        for table_rows in item['data']:
            bulk_insert.extend(self.get_objects(table_rows))
        self.mutator.delete_player_stat()
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
        try:
            team_id = self.team_dict[team.lower()]
        except:
            team_id = self.handle_new_team(team)
        for key in item:
            if is_stat:
                post_objs.append({"stat_name": key, "team_id": team_id, "player": player,
                                  "value": item[key], "rank": rank, "date": date, "stat_type": stat_type})
            if key == 'team':
                is_stat = True
        return post_objs
    
    def handle_new_team(self, team_name):
        self.mutator.add_team(team_name)
        new_team = self.getter.get_team(team_name)
        if new_team:
            return new_team['id']
        return None
