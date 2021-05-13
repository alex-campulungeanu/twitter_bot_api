from app.shared.helper import generate_hastags
from app import app

def sanitize_tweet(tweet, tw_length=280, suffix='...'):
    tw_hastags = tweet + "\n" + ' '.join(generate_hastags(tweet, app.config["TWITTER_HASTAGS_NR"]))
    if len(tw_hastags) <= tw_length:
        return tw_hastags
    else:
        tw_length_without_suffix = tw_length - len(suffix)
        truncate_tw = ' '.join(tw_hastags[:tw_length_without_suffix+1].split(' ')[0:-1])  + ' ' + suffix
        return truncate_tw