from datetime import timedelta, datetime
import re
import scrapy
from scrapy import Request, log
from scrapy.exceptions import CloseSpider
from redditgiveaway.items import UserItem


USAGE = "Usage:\n"\
        "Required:\n"\
        "\turl - <url to reddit comments page>\n"\
        "\tmatch - <match regex for determining qualifying comments>\n"\
        "\ttotal_winners - <amount of winners to choose (integer)>\n"\
        "Optional:\n"\
        "\tmin_c_karma - default: 150 <minimum user comment karma to be eligible for winning (int)>\n"\
        "\tmin_l_karma - default: 0 <minimum user link karma to be eligible for winning (int)>\n"\
        "\tmin_days - default: 30 <minimum user age to be eligible for winning(int)>\n"\
        "\tignored_users - <User list (separated by comma) of users to ignore>\n"


class GiveawaySpider(scrapy.Spider):
    name = "giveaway"
    allowed_domains = ["www.reddit.com"]
    giveaway_post_url = ''

    default_min_days = 30
    default_min_c_karma = 150
    default_min_l_karma = 0

    ignored_users = []
    op = ''

    def __init__(self, **kwargs):
        super(GiveawaySpider, self).__init__(**kwargs)
        if kwargs.get('help') or kwargs.get('h'):
            print(USAGE)
            raise CloseSpider(reason=USAGE)
        try:
            self.giveaway_post_url = kwargs['url']
            self.match_raw = kwargs['match']
            self.match = re.compile(self.match_raw)
            self.total_winners = int(kwargs['total_winners'])
        except KeyError:
            raise NotImplementedError(USAGE)

        self.min_c_karma = kwargs.get('min_c_karma', self.default_min_c_karma)
        self.min_l_karma = kwargs.get('min_l_karma', self.default_min_l_karma)
        self.min_days_raw = kwargs.get('min_days', self.default_min_days)
        self.ignored_users = [user.lower() for user in kwargs.get('ignore_users', '').split(',') if user]
        self.min_days = timedelta(days=self.min_days_raw)

    def start_requests(self):
        yield Request(url=self.giveaway_post_url)

    def parse(self, response):
        self.op = response.xpath("//div[@id='siteTable']//a[contains(@class, 'author')]/text()").extract()[0]
        for comment in response.xpath("//div[contains(@class, 'entry')]"):
            yield self.parse_comment(comment)

    def parse_comment(self, comment):
        """Determines whether the comment is eligible for giveaway if so proceeds to parse_user()"""

        # Filter op and ignored users out
        user_name = (comment.xpath(".//a[contains(@class, 'author')]/text()").extract() or [''])[0].lower()
        if user_name in self.ignored_users or user_name == self.op.lower():
            return

        join_xpath = lambda x, sep='': sep.join(comment.xpath(x).extract()).strip()
        # Filter non matching comments out
        comment_text = join_xpath(".//form//text()")
        if not comment_text or not re.search(self.match, comment_text):
            return

        user_url = (comment.xpath(".//a[contains(@class, 'author')]/@href").extract() or [''])[0]
        if user_url:
            return Request(user_url,
                           callback=self.parse_user,
                           meta={'comment_text': comment_text})
        else:
            log.msg('Failed to find user url for comment {}'.format(comment_text), level=log.ERROR)

    def parse_user(self, response):
        """Parses user and determines whether user is eligible for the giveaway, if so returns item"""
        try:
            age = response.xpath("//span[@class='age']/time/@datetime").extract()[0]
        except IndexError:
            log.msg('Failed to find age of user {}'.format(response.url), level=log.ERROR)
            return
        age = age.rsplit('-', 1)[0]  # cut off last bit since I don't know how to strptime last bit :D (%z doesn't work)
        age_date = datetime.strptime(age, '%Y-%m-%dT%H:%M:%S')
        # Filter out too young accounts
        if (datetime.now() - self.min_days) < age_date:
            return
        # Filter out not enough karma
        comment_karma = response.xpath("//span[contains(@class, 'comment-karma')]/text()").extract()[0]
        comment_karma = int(comment_karma.replace(',', ''))
        link_karma = response.xpath("//span[@class='karma']/text()").extract()[0]
        link_karma = int(link_karma.replace(',', ''))
        if comment_karma < self.min_c_karma or link_karma < self.min_l_karma:
            return

        item = UserItem()
        item['name'] = (response.xpath("//div[contains(@class, 'titlebox')]/h1/text()").extract() or [''])[0]
        item['url'] = response.url
        item['comment'] = response.meta['comment_text']
        return item



