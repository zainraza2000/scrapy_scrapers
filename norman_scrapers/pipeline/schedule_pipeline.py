from norman_scrapers.mutators import Mutator
from norman_scrapers.getters import Getter


class SchedulePipeline:
    def __init__(self, team_dict) -> None:
        self.mutator = Mutator()
        self.getter = Getter()
        self.team_dict = team_dict

    def process_data(self, item):
        if item['is_first']:
            game_data = []
            for game in item['data']:
                game_data.append(self.get_game_object(game))
            self.mutator.create_game(game_data)
        else:
            pending_games = self.getter.get_pending_games()
            self.get_box_score_games(pending_games, item['data'])
        return item

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

    def handle_new_team(self, team_name):
        self.mutator.add_team(team_name)
        new_team = self.getter.get_team(team_name)
        if new_team:
            return new_team['id']
        return None

    def is_box_score(self, away_team_id, home_team_id, date, pending_games):
        for pending_game in pending_games:
            if pending_game['away_team_id'] == away_team_id and pending_game['home_team_id'] == home_team_id and pending_game['date'] == date and pending_game['box_score'] == '-':
                return pending_game
        return None
