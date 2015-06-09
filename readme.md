 ## About
 
 reddit-giveaway is a scrapy spider for choosing a winner for giveaways held in reddit post. It is possible to filter eligable users and comments with regex and user meta settings for quick and accurate results  
  
 ## Requirements
 
 Python 2.7+  
 Scrapy
 
 ## Usage:  
 
 Required:  
 `url` - url to reddit comments page  
 `match` - match regex for determining qualifying comments  
 `total_winners` - amount of winners to choose (integer)  
 Optional:  
 `min_c_karma` - (default: 200) minimum user comment karma to be eligible for winning (int)  
 `min_l_karma` - (default: 0) minimum user link karma to be eligible for winning (int)  
 `min_days` - (default: 30) minimum user age to be eligible for winning(int)
 
 ## Example:
 
 `scrapy crawl giveaway -a url="http://www.reddit.com/r/GameDeals/comments/395icr/gogcom_dealoverload_all_600_summer_promo_deals/" -a match='witcher' -a total_winners=5`  
 will print out random winners and save them to winners<current_date>.json
