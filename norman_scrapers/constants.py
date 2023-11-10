from enum import Enum


class Pipeline(Enum):
    leaderboard = 'leaderboard'
    schedule = 'schedule'
    statistics = 'statistics'


class Table(Enum):
    PlayerStat = 'PlayerStat'
    Game = 'Game'
    Team = 'Team'
    Scoring = 'Scoring'
    Statistic = 'Statistic'


class StatType(Enum):
    primary = 'primary'
    secondary = 'secondary'
