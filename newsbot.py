import irc.client
import feedparser
import schedule
import time
import threading
import random

IRC_SERVER = "irc.oftc.net"
IRC_PORT = 6667
CHANNEL = "#YOURCHANNEL"
NICKNAME = "YOURNICK"
POST_INTERVAL_MINUTES = 120

# RSS feeds to track
rss_feeds = {
    "Linux Journal": "https://www.linuxjournal.com/node/feed",
    "Linux.com": "https://www.linux.com/feed",
    "It's FOSS": "https://itsfoss.com/rss",
    "Linux Magazine": "https://www.linux-magazine.com/rss/feed/lmi_news",
    "LXer": "http://lxer.com/module/newswire/headlines/rss",
    "Linux Today": "https://www.linuxtoday.com/backend/biglt.rss"
}

# Friendly intros
intros = [
    "Hey, have you seen this?",
    "Thought you’d find this interesting:",
    "Another one for the nerds:",
    "Fresh from the Linux world:",
    "Ooh, shiny:",
    "Check this out:",
    "You might like this one:",
    "Heads up, this just dropped:",
    "Some fresh bytes for your brain:",
    "New from the FOSS frontier:",
    "Ping! New article just in:",
    "Hot off the press:",
    "More Linux goodness:",
    "For your daily dose of tech:",
    "A quick read you might enjoy:"
]

seen_entries = set()

def fetch_and_post_news(connection):
    # Pick one feed at random
    name, url = random.choice(list(rss_feeds.items()))
    feed = feedparser.parse(url)

    for entry in feed.entries:
        if entry.id not in seen_entries:
            intro = random.choice(intros)
            message = f"{intro} [{name}] {entry.title} - {entry.link}"
            connection.privmsg(CHANNEL, message)
            seen_entries.add(entry.id)
            return  # Only post one article per run

def start_scheduler(connection):
    schedule.every(POST_INTERVAL_MINUTES).minutes.do(fetch_and_post_news, connection)

    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)

    thread = threading.Thread(target=run_scheduler)
    thread.daemon = True
    thread.start()

def on_connect(connection, event):
    if irc.client.is_channel(CHANNEL):
        connection.join(CHANNEL)
        fetch_and_post_news(connection)
        start_scheduler(connection)

def main():
    reactor = irc.client.Reactor()
    try:
        connection = reactor.server().connect(IRC_SERVER, IRC_PORT, NICKNAME)
    except irc.client.ServerConnectionError as e:
        print(f"Connection failed: {e}")
        return

    connection.add_global_handler("welcome", on_connect)
    reactor.process_forever()

if __name__ == "__main__":
    main()
