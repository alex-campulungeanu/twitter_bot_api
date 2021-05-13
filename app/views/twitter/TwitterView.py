import tweepy
import random

from flask import Blueprint, current_app, request

from app.shared.Authentification import Auth
from app.shared.db_api import execute_query
from app.shared.request import api_response, validate_request, validate_request_cerberus
from app.shared.helper import get_string_from_inside_list
from app.constants.app_constants import PLATFORM_TWITTER_ID
from app.constants.reply_quotes import confucius_quotes
from app.utils.apis.twitter.twitter_api import create_api
from app.utils.apis.twitter.twitter_utils import sanitize_tweet
from app.models import db, PostModel, PlatformModel, PlatformConfigModel, PostPlatformModel, TwitterFollowersModel, QuoteModel, cfg_db_schema
from app.validations.twitter_schema import reaction_schema
from app.shared.Api import Api

twitter_api = Blueprint('twitter_api', __name__)


@twitter_api.route('/publish_post_to_twitter', methods=['POST'])
@Auth.auth_required
@Auth.check_permissions('publishTwitterPost')
def publish_post_to_twitter():
    res = {'status': '', 'data': {}, 'error': ''}
    api = create_api()
    post_sql = f"select p.id as post_id, p.body as post_body \
                from {cfg_db_schema}.post p \
                left join {cfg_db_schema}.post_platform pp on pp.post_id = p.id and pp.platform_id = {PLATFORM_TWITTER_ID} \
                where pp.platform_id is null \
                order by p.md5 \
                limit 1;"
    result_sql = execute_query(post_sql)
    if len(result_sql) != 0:
        db_post_body = result_sql[0]['post_body']
        db_post_id = result_sql[0]['post_id']
        db_post_body_hastags = sanitize_tweet(db_post_body, current_app.config['TWITTER_TWEET_LEN']) ## limit tweet to maximum allowed
        try:
            ## from here: https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html
            post = PostModel.query.get(db_post_id)
            platform = PlatformModel.query.get(PLATFORM_TWITTER_ID)
            post_platform = PostPlatformModel(error=0)
            post_platform.platform = platform
            post_platform.post = post
            post.platform.append(post_platform)
            db.session.add(post)
            db.session.commit()
            ## add tweet
            tw_status = api.update_status(db_post_body_hastags)
            tw_status_id = tw_status._json['id'] ## add tweet
            api.create_favorite(tw_status_id) ## like previous added tweet
        except Exception as ex_tw:
            ## if error then update post_platform error with 1
            post_platform = PostPlatformModel.query.filter_by(post_id=post.id, platform_id=platform.id).first()
            post_platform.error = 1 
            post_platform.error_msg = str(ex_tw)[:200]
            db.session.commit()
            current_app.logger.info(f'Twitter ERROR: {ex_tw}')
            res['status'] = 'notok'
            res['error'] = f'Unable to post, Twitter API problem: {ex_tw}'
            return api_response(res, status_code=500)
        res['status'] = 'ok'
        res['data'] = db_post_body
        return api_response(res)
    else:
        Api.log_db('publish_post_to_twitter', 'No more post available in DB to publish on Twitter')
        return api_response({'status': 'notok', 'data': {}, 'error': 'Posts not available'}, status_code=500)


@twitter_api.route('/publish_reaction_to_reply', methods=['POST'])
@Auth.auth_required
@Auth.check_permissions('publishTwitterPost')
def publish_reaction_to_reply():
    """Get last 10 reply on my tweets and add a like/reply/retweet 
    !!! IMPORTANT Need to get replies from last checked reply(stored in DB / since_id=p_tweet_id) to avoid duplicate reply from logged user
    """
    res = {'status': '', 'data': {}, 'error': ''}
    nr_replies_checked_cfg = current_app.config['LAST_REPLIES_CHECKED']
    last_reply_db_config = PlatformConfigModel.query.filter_by(platform_id=PLATFORM_TWITTER_ID, id_config=1).first()
    ## if no value is set in DB then get only the last reply / else get last current_app.config['LAST_REPLIES_CHECKED'] replies 
    api = create_api()
    if last_reply_db_config.value == '': 
        # current_app.logger.info('no value set')
        replies = tweepy.Cursor(api.search, q='to:{}'.format('@' + current_app.config['TWITTER_USER']),
                                result_type='recent' ,
                                tweet_mode='extended').items(1)
    else:
        # current_app.logger.info(f'value is set at: {last_reply_db_config.value}')
        replies = tweepy.Cursor(api.search, q='to:{}'.format('@' + current_app.config['TWITTER_USER']),
                                since_id=last_reply_db_config.value,  ## here get last tweet liked
                                result_type='recent' ,
                                tweet_mode='extended').items(nr_replies_checked_cfg)
    last_reply_tweet_id = last_reply_db_config.value
    replies_list = [reply for reply in replies]
    replies_list_revert = [r for r in reversed(replies_list)]
    quotes=[]
    db_quotes = QuoteModel.query.filter_by(active=1).all()
    for quote in db_quotes:
        quotes.append(quote.body)
    for reply in replies_list_revert:
        last_reply_tweet_id = reply.id
        try:
            reply_text = reply._json['full_text']
            # random_reply = sanitize_tweet(random.choice(confucius_quotes), current_app.config['TWITTER_TWEET_LEN']) ## limit tweet to maximum allowed
            random_reply = sanitize_tweet(get_string_from_inside_list(reply_text, quotes), current_app.config['TWITTER_TWEET_LEN']) ## limit tweet to maximum allowed
            ## react to reply
            api.create_favorite(last_reply_tweet_id)
            api.update_status(status = random_reply, in_reply_to_status_id = last_reply_tweet_id , auto_populate_reply_metadata=True)
        except Exception as e:
            current_app.logger.info(f"LIKE ERROR: reply: {reply.id} text: {reply._json['full_text']} for reply: {reply.in_reply_to_status_id} ERROR: {e}")
        # current_app.logger.info(f"reply: {reply.id} text: {reply._json['full_text']} for reply: {reply.in_reply_to_status_id} txt: {random.choice(confucius_quotes)}")
    last_reply_db_config.value = last_reply_tweet_id;
    db.session.commit()
    return api_response({'status': 'ok', 'data': 'Reaction to reply added !', 'error': ''})


@twitter_api.route('/publish_reaction_to_hastags', methods=['POST'])
@Auth.auth_required
@Auth.check_permissions('publishTwitterPost')
# @validate_request('reaction_type') ## eg. all, like, retweet
@validate_request_cerberus(reaction_schema)
def publish_reaction_to_hastags():
    api = create_api()
    req_data = request.get_json()
    reaction_type = req_data['reaction_type']
    last_tweet_db_config = PlatformConfigModel.query.filter_by(platform_id=PLATFORM_TWITTER_ID, id_config=2).first()
    last_user_tweet = api.user_timeline(count=1, tweet_mode='extended')[0]
    if int(last_tweet_db_config.value) != last_user_tweet._json['id'] and not hasattr(last_user_tweet , 'retweeted_status'): ## check if my last tweet is retweet, if not the do your magic, else do nothing
        hastags = [hastag['text'] for hastag in last_user_tweet._json['entities']['hashtags']]
        for hastag in hastags[:5]: ## get only 5 hastags
            for tweet in tweepy.Cursor(api.search, q=f"#{hastag}").items(3): ## get only last tweet per hastag
                try:
                    if reaction_type == 'like':
                        api.create_favorite(tweet._json['id']) ## like tweet
                    elif reaction_type == 'retweet':
                        api.retweet(tweet._json['id']) ## retweet tweet
                    elif reaction_type == 'all':
                        api.create_favorite(tweet._json['id']) ## like tweet
                        api.retweet(tweet._json['id']) ## retweet tweet
                except Exception as e:
                    current_app.logger.info(e)
        last_tweet_db_config.value = last_user_tweet._json['id']
        db.session.commit()
    return api_response({'status': 'ok', 'data': 'Reaction to hastags added !', 'error': ''})

@twitter_api.route('/get_followers', methods=['GET'])
@Auth.auth_required
@Auth.check_permissions('viewPost')
def get_followers():
    api = create_api()
    followers_list = []
    added_followers = []
    removed_followers = []
    current_user = api.me()
    for item in tweepy.Cursor(api.followers, id=current_user._json['screen_name']).items(500):
        followers_list.append(item)
    ## check if current followers exist in database
    for follower in followers_list:
        id_follower = follower._json['id_str']
        name_follower = follower._json['screen_name']
        new_user = TwitterFollowersModel.query.filter_by(id_follower=id_follower).first()
        if new_user == None:
            new_follower = TwitterFollowersModel(id_follower=id_follower, screen_name=name_follower, active=1)
            db.session.add(new_follower)
            db.session.commit()
            added_followers.append({'id': id_follower, 'name': name_follower})
    ## check if follower from database are still with us
    followers_db = TwitterFollowersModel.query.filter_by(active=1).all()
    for follower in followers_db:
        if follower.id_follower not in [item._json['id_str'] for item in followers_list]:
            follower.active = 0
            db.session.add(follower)
            db.session.commit()
            removed_followers.append({'id': follower.id_follower, 'name': follower.screen_name})
    result = {'added_followers': added_followers, 'removed_followers': removed_followers}
    return api_response({'status': 'ok', 'data':  result, 'error': ''})

@twitter_api.route('/repopulate_post_platform', methods=['GET'])
@Auth.auth_required
@Auth.check_permissions('administration')
def repopulate_post_platform():
    api = create_api()
    current_user = api.me()
    for status in tweepy.Cursor(api.user_timeline, id=current_user._json['screen_name'], count=500, tweet_mode="extended").items(500): 
        try:
            only_text = status.full_text[:status.full_text.index('\n#')]
            tw = PostModel.query.filter_by(body=only_text).first()
            platform = PlatformModel.query.get(1)
            if tw != None:
                try:
                    post_platform = PostPlatformModel(error=0)
                    post_platform.platform = platform
                    post_platform.post = tw
                    tw.platform.append(post_platform)
                    db.session.add(tw)
                    db.session.commit()
                except Exception as e:
                    print(f'Exception on id {tw.id}:  {e}')
            else:
                print(f'Not found {status.full_text}')
        except Exception as e2:
            print(f'Exception on {status.full_text}: {e2}')
    return api_response({'status': 'ok', 'data': 'ok', 'error': ''})
