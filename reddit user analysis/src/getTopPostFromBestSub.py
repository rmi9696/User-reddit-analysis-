from src.getbestsubreddit import *

bs = BestSub()
r = bs.red_inst()

# utility function for adding trending subreddit

# is_inserted = bs.get_best()
# while not is_inserted:
#     bs.get_best()

# ----------------------------------------------------------------------------
# selecting the subreddit from table

command = (
    """
        SELECT sub_name FROM popular_subreddits ORDER BY curr_time DESC LIMIT 1;
    """
)
conn = bs.get_conn()
cursor = bs.get_cursor()
cursor.execute(command)
sub = cursor.fetchone()[0]
post = r.subreddit(str(sub)).top("day")
top_post = list(post)[0]

# ----------------------------------------------------------------------------
# add reddit user

post_author_id = top_post.author.id
post_author_username = str(top_post.author)
post_author_c_karma = top_post.author.comment_karma
post_author_p_karma = top_post.author.link_karma
# command = (
#     """
#         INSERT INTO reddit_user VALUES(%s, %s, %s, %s, false);
#     """
# )
# to_insert = (post_author_id, post_author_username, post_author_c_karma, post_author_p_karma)
# try:
#     cursor.execute(command, to_insert)
#     conn.commit()
# except Exception:
#     conn.rollback()

# side note for future reference: is_chosen just means if the specified user
# is the one who will be analyzed against different users based on the comments.

# ----------------------------------------------------------------------------
# add post

post_id = top_post.id
post_title = top_post.title
post_is_text = top_post.is_self
post_subreddit_id = top_post.subreddit.id

# command = (
#     """
#         INSERT INTO post VALUES(%s, %s, %s, %s, %s, NULL);
#     """
# )
# to_insert = (post_id, post_title, post_is_text, post_subreddit_id, post_author_id)
# try:
#     cursor.execute(command, to_insert)
#     conn.commit()
# except Exception:
#     conn.rollback()

# ----------------------------------------------------------------------------
# add subreddit

subreddit_name = str(list(r.info(['t5_' + post_subreddit_id]))[0])

# command = (
#     """
#         INSERT INTO subreddit VALUES(%s, %s, %s);
#     """
# )
# to_insert = (post_subreddit_id, subreddit_name, post_author_id)
# try:
#     cursor.execute(command, to_insert)
#     conn.commit()
# except Exception:
#     conn.rollback()
cursor.close()
conn.close()
