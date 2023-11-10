import datetime
from norman_scrapers.mutators import Mutator
from norman_scrapers.getters import Getter


class LeaderboardPipeline:
    def __init__(self) -> None:
        self.mutator = Mutator()
        self.getter = Getter()

    def process_data(self, item):
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
