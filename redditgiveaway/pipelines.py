
import random
from datetime import datetime
import json


class RedditgiveawayPipeline(object):
    items = []

    def process_item(self, item, spider):
        """just add all items to class argument"""
        self.items.append(item)
        return item

    def close_spider(self, spider):
        """This determines the winners by selecting random users from all scraped users"""
        winners = []
        while (len(winners) < spider.total_winners) and self.items:
            winner = random.choice(self.items)
            self.items.remove(winner)
            winners.append(winner)
        with open('winners{}.json'.format(datetime.now()), 'w') as winner_file:
            print('The winners are:')
            print('-' * 80)
            for winner in winners:
                print(winner['name'] , winner['url'])
            results = {
                'meta': {
                    'giveaway_url': spider.giveaway_post_url,
                    'giveaway_holder': spider.op,
                    'winner_cap': spider.total_winners,
                    'winners_got': len(winners),
                    'match_regex': spider.match_raw,
                    'min_c_karma': spider.min_c_karma,
                    'min_l_karma': spider.min_l_karma,
                    'min_days': spider.min_days_raw,
                    'ignored_users': spider.ignored_users,
                },
                'winners': [dict(w) for w in winners]
            }
            winner_file.write(json.dumps(results, indent=4))
            #     pass
