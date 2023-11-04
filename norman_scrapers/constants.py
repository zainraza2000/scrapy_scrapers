from enum import Enum


class Pipeline(Enum):
    leaderboard = 'leaderboard'
    schedule = 'schedule'
    statistics = 'statistics'


class Table(Enum):
    PlayerStat = 'PlayerStat'
    Game = 'Game'
    Team = 'Team'
