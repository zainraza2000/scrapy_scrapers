import subprocess
from norman_scrapers.constants import Spiders
from norman_scrapers.getters import Getter
from norman_scrapers.mutators import Mutator
import schedule
import time

class Job:
    def __init__(self) -> None:
        self.getter = Getter()
        self.mutator = Mutator()

    def leaderboard_spider_job(self):
        command = f"scrapy crawl {Spiders.Leaderboard.value}"
        subprocess.run(command, shell=True)

    def schedule_spider_job(self):
        command = f"scrapy crawl {Spiders.Schedule.value}"
        subprocess.run(command,shell=True)

    def game_statistics_spider_job(self):
        getter = Getter()
        unscraped_box_scores = getter.get_unscraped_box_scores()
        for unscraped_box_score in unscraped_box_scores:
            try:
                id = unscraped_box_score["id"]
                url = unscraped_box_score["box_score"]
                primary_command = f"scrapy crawl {Spiders.PrimaryStats.value} -a url={url} -a game_id={id}"
                subprocess.run(primary_command, shell=True)
                secondary_command = f"scrapy crawl {Spiders.SecondaryStats.value} -a url={url} -a game_id={id}"
                subprocess.run(secondary_command, shell=True)
                self.mutator.mark_scraped(id=id)
            except:
                continue
    def schedule_tasks(self):
        schedule.every().monday.at("08:00").do(self.leaderboard_spider_job)
        schedule.every().monday.at("08:05").do(self.schedule_spider_job)
        schedule.every().monday.at("08:10").do(self.game_statistics_spider_job)

        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    job = Job()
    job.schedule_tasks()