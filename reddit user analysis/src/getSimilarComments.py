from src.getbestsubreddit import *
from fuzzywuzzy import fuzz

bs = BestSub()
r = bs.red_inst()
conn = bs.get_conn()
cursor = bs.get_cursor()

command = (
    """
        SELECT top_comment_id, post_id FROM user_top_comments;
    """
)
for i in range(20, 25):
    cursor.execute(command)
    conn.commit()
    comm = r.comment(cursor.fetchall()[i][0])
    cursor.execute(command)
    conn.commit()
    post = r.submission(cursor.fetchall()[i][1])
    post.comments.replace_more(limit=0)
    for comment in post.comments.list():
        red_comment = r.comment(comment)
        if comment.id != comm.id:
            ratio = (fuzz.token_set_ratio(str(comm.body).lower(), str(comment.body).lower()))
            if ratio >= 60:
                pass
                # red_ins_command = (
                #     """
                #         INSERT INTO reddit_user VALUES(%s, %s, %s, %s, false);
                #     """
                # )

                # sim_comm_ins_command = (
                #     """
                #         INSERT INTO similar_comments VALUES(%s, %s, %s, %s, %s, %s)
                #     """
                # )

                # try:
                #     red_to_insert = (red_comment.author.id, str(red_comment.author), red_comment.author.comment_karma, red_comment.author.link_karma)
                #     cursor.execute(red_ins_command, red_to_insert)
                #     conn.commit()
                # except Exception:
                #     conn.rollback()
                #     continue

                # try:
                #     sim_comm_to_insert = (red_comment.id.id, str(ratio), red_comment.author.id, comm.author.id, post.id, str(comment.body))
                #     cursor.execute(sim_comm_ins_command, sim_comm_to_insert)
                #     conn.commit()
                # except Exception:
                #     conn.rollback()
                #     continue

cursor.close()
conn.close()
