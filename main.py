import time
from getpass import getpass

from pyjokes import get_joke

from util import TweeterRequest


def main():
    print("Please login to your acocuont")
    username = input("Username: ")
    password = getpass()
    print("Logging in ...")
    try:
        tweeter = TweeterRequest(username, password)
        print("log in successful")
        print("checking recent tweets ...")
        recent_twets = tweeter.get_recent_tweets()
        for tweet in recent_twets:
            print(f"({tweet['id']}) {tweet['author']['username']} tweeted at {tweet['created_at']}")
            print(tweet["text"])
            print()
        existing_jokes = set([tweet["text"] for tweet in recent_twets])
        for i in range(10):
            joke = ""
            while True:
                joke = get_joke()
                if joke not in existing_jokes:
                    existing_jokes.add(joke)
                    break
            print("posting tweet")
            print(joke)
            tweeter.post_tweet(joke)
            print("posted tweet. sleeping 1 min now")
            time.sleep(60)
    except Exception:
        print("try again")
        raise


if __name__ == "__main__":
    main()
