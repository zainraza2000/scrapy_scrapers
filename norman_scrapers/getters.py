from itemadapter import ItemAdapter
import os
from supabase import create_client, Client
import datetime


class Getter:
    def __init__(self) -> None:
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)
        pass

    def get_latest_games(self):
        data, count = self.supabase.table(
            'Game').select('*').eq('is_scraped', False).neq('box_score', None).execute()
        print(data, count)


getter = Getter()
getter.get_latest_games()
