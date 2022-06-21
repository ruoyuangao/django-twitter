from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        # we should never put database action inside for loop
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)