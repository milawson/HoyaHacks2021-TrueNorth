import os
import sys

from RedditComponent import RedditComponent
from LogicEngine import LogicEngineComponent
from DatabaseComponent import DatabaseComponent

activities = dict()

def run_truenorth_monitor(subreddit_name, database_name, grammar_relative_path):
    # Create the reddit and database clients
    reddit = RedditComponent.RedditComponent(subreddit_name)
    database = DatabaseComponent.DatabaseComponent(database_name)
    logic = LogicEngineComponent.LogicEngine(database.fetch(), grammar_relative_path)

    # Retrieve posts to answer questions for
    comment_dict = reddit.retrieve_posts()
    
    # Answer questions for all posts
    answer_dict = dict()
    for comment_id, message in comment_dict.items():
        (expression, answer, response) = logic.answer(message)
        if answer is not None:
            answer_dict[comment_id] = (expression, answer, response)

    print("Found {0} assertable posts!\n".format(len(answer_dict)))

    # Post answers to reddit where applicable
    for comment_id, (expression, answer, response) in answer_dict.items():
        if answer is True:
            print("Skipping response for comment_id={0} since comment was evaluated as true.\nThis answer was provided because of justification={1}\n".format(comment_id, expression))
        else:
            reddit.post_reply(comment_id, answer)
            print("Posting reply to comment_id={0} with response={1}.\nThis answer was provided because of justification={2}".format(comment_id, response, expression))

def register_truenorth_monitor(activity_name, subreddit_name, relative_database_path):
    grammar_relative_path = "./src/LogicEngine/grammar.fcfg"
    activities[activity_name] = (subreddit_name, os.path.join(os.path.dirname(__file__), relative_database_path), grammar_relative_path)

def main():
    # Register our monitors
    register_truenorth_monitor("smash", "smashtournamentstats", "DatabaseComponent/databases/melee_light.csv")
    register_truenorth_monitor("tennis", "tennistournamentstats", "DatabaseComponent/databases/tennis.csv")

    # Run the specified monitor
    (subreddit_name, database_name, grammar_relative_path) = activities[sys.argv[1]]
    run_truenorth_monitor(subreddit_name, database_name, grammar_relative_path)

main()