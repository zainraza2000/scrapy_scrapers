from norman_scrapers.mutators import Mutator
from norman_scrapers.getters import Getter
from norman_scrapers.constants import Pipeline, StatType


class StatisticsPipeline:
    def __init__(self, team_dict) -> None:
        self.mutator = Mutator()
        self.getter = Getter()
        self.team_dict = team_dict

    def process_item(self, item):
        if item['type'] == StatType.primary.value:
            self.process_primary_data(item)
        elif item['type'] == StatType.secondary.value:
            self.process_secondary_data(item)

    def process_primary_data(self, item):
        scoring = item['scoring']
        statistics = item['statistics']
        self.mutator.create_scoring(scoring)
        self.mutator.create_statistics(statistics)
    
    def process_secondary_data(self,item):
        table = item['table']
        data = item['data']
        transformed_data = []
        for _data in data:
            transformed = {**_data,"team_id": self.team_dict[_data.get('team').lower()]}
            transformed.pop("team",None)
            transformed_data.append(transformed)
        self.mutator.create(data=transformed_data,table_name=table)
