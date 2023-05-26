from src.getbestsubreddit import *

bs = BestSub()
r = bs.red_inst()
conn = bs.get_conn()
cursor = bs.get_cursor()
command = (
    """
        select post_id from post 
        inner join subreddit
        on post.subreddit_id = subreddit.subreddit_id 
        inner join popular_subreddits 
        on subreddit.subreddit_name = popular_subreddits.sub_name
        where popular_subreddits.curr_time > (select extract(epoch from now()) - 3000);
    """
)
cursor.execute(command)
post_id = cursor.fetchall()[0][0]
post = r.submission(id=post_id)
comment_id = ""
comment_author_id = ""
comment_body = ""
post_subreddit_id = post.subreddit.id
subreddit_name = str(list(r.info(['t5_' + post_subreddit_id]))[0])
comment_author = ""
author_comment_karma = 0
author_link_karma = 0

post.comment_sort = 'top'
for comment in post.comments:
    if not comment.stickied and comment.body != "[removed]":
        comment_id = comment.id
        comment_author_id = comment.author.id
        comment_body = comment.body
        comment_author = comment.author
        author_comment_karma = comment.author.comment_karma
        author_link_karma = comment.author.link_karma
        break

# ---------------------------------------------------------
# add new user

# command = (
#     """
#         INSERT INTO reddit_user VALUES(%s, %s, %s, %s, true);
#     """
# )
# to_insert = (comment_author_id, str(comment_author), author_comment_karma, author_link_karma)
# try:
#     cursor.execute(command, to_insert)
#     conn.commit()
# except Exception:
#     conn.rollback()

# -------------------------------------------------------------------------------------
# inserts into comment

# command = (
#     """
#         INSERT INTO user_comment VALUES(%s, %s, %s, %s, %s);
#     """
# )
# to_insert = (comment_id, post_id, subreddit_name, comment_body, comment_author_id)
# try:
#     cursor.execute(command, to_insert)
#     conn.commit()
# except Exception:
#     conn.rollback()

cursor.close()
conn.close()
