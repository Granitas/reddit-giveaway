BOT_NAME = 'redditgiveaway'
SPIDER_MODULES = ['redditgiveaway.spiders']
NEWSPIDER_MODULE = 'redditgiveaway.spiders'
ITEM_PIPELINES = {
    'redditgiveaway.pipelines.RedditgiveawayPipeline': 300,
}