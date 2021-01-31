import praw

reddit = praw.Reddit(client_id="RT0SLSR63_FcjA",
                     client_secret="iyhlTqhKBqldKamz6XHI6BZJj5o0Ag",
                     username='NLP_Sports_Bot',
                     password='HellowWorld1234',
                     user_agent="testscript by u/EasilyTheFinest",
                     )


class RedditComponent:

    def __init__(self, given_subreddit, posts_retrieved=20):
        self.given_subreddit = given_subreddit
        self.comment_dictionary = dict()
        self.posts_retrieved = posts_retrieved

    def retrieve_posts(self):

        new_posts = reddit.subreddit(self.given_subreddit).new(limit=self.posts_retrieved)

        for post in new_posts:
            for comment in post.comments:
                self.comment_dictionary[comment.id] = comment.body
        
        return self.comment_dictionary

    @staticmethod
    def post_reply(comment_id, message):

        comment_submit = reddit.comment(id=comment_id)
        comment_submit.reply(message)
