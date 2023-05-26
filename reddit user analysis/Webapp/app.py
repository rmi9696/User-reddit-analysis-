from flask import Flask, render_template, request
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

app = Flask(__name__)

# Connect to AWS RDS Database
path = ""
password = ""
connectionRoute = open('DBCredentials.txt', "r")

for credential in connectionRoute:
    if len(path) == 0:
        path = credential
    else:
        password = credential

# path = connectionRoute.read()

engine = create_engine(path)

con = engine.connect()

# HOME PAGE
@app.route('/')
def index():
    availableUsers = con.execute('''SELECT username FROM chosen_users''')
    userList = []

    for user in availableUsers:
        userList.append(user[0])

    return render_template("index.html", len=len(userList), userList=list(userList))

# QUERY ZONE AUTHENTICATION
@app.route('/queryauth')
def queryauth():
    return render_template("auth.html")

# QUERY ZONE
@app.route('/queryzone')
def queryzone():
    input = request.args.get('password')
    requery = request.args.get('requery')

    isCorrect = False

    if input == password or requery != None:
        isCorrect = True

    return render_template("queryzone.html", isCorrect=isCorrect)

# QUERY RESULTS PAGE
@app.route('/queryResults')
def queryresults():
    userQuery = request.args.get('userquery')
    columnTitles = ""
    tuplesReceived = ''
    tuples = []
    titles = []
    validQuery = ''

    try:
        tuplesReceived = con.execute(userQuery)

        words = userQuery.split()

        if words[0].upper() not in ('INSERT', 'UPDATE', 'DELETE'):
            for tuple in tuplesReceived:
                tuples.append(tuple)

            columnTitles = con.execute(userQuery).keys()

            for title in columnTitles:
                titles.append(title)
        validQuery = True
    except:
        validQuery = False

    return render_template('results.html',
                           tuplesReceived=tuples,
                           numTuples = len(tuples),
                           validQuery=validQuery,
                           columnTitles=titles,
                           numColumns = len(columnTitles))

# REPORT PAGE
@app.route('/report')
def report():
    userName = request.args.get('userName')
    karmaStats = con.execute('''SELECT user_id, comment_karma, post_karma FROM chosen_users WHERE username = \'{redditUser}\''''
                             .format(redditUser=userName))

    postKarma = ''
    commentKarma = ''
    userId = ''

    for tuple in karmaStats:
        userId = tuple[0]
        commentKarma = int(tuple[1])
        postKarma = int(tuple[2])


    topCommentDistribution = {}

    topCommentStats = con.execute('''WITH T
                                     AS 
                                    (SELECT * FROM chosen_users C 
                                     JOIN user_top_comments U 
                                     ON C.user_id = U.user_id)
                                     SELECT DISTINCT(subreddit_name), COUNT(top_comment_id)
                                     FROM subreddit S
                                     JOIN T ON T.subreddit_id = S.subreddit_id
                                     WHERE username = \'{redditUser}\'
                                     GROUP BY subreddit_name'''.format(redditUser=userName))

    for tuple in topCommentStats:
        topCommentDistribution[tuple[0]] = tuple[1]




    topCommentTopSubs = con.execute('''
                                    WITH T
                                    AS 
                                    (SELECT * FROM chosen_users C 
                                     JOIN user_top_comments U 
                                     ON C.user_id = U.user_id)
                                     SELECT DISTINCT(subreddit_name)
                                     FROM subreddit S
                                     JOIN T ON T.subreddit_id = S.subreddit_id
                                     WHERE username = \'{redditUser}\'
                                     INTERSECT
                                     SELECT sub_name FROM popular_subreddits'''.format(redditUser=userName))
    
    overlappingTopSubs = []
    
    for tuple in topCommentTopSubs:
        overlappingTopSubs.append(tuple[0])
    
    # Pie Chart of Percentage of Subs user has top comments in that are "Top Subs"
    # Data to Plot
    labels = 'Top Subs', 'Non-top Subs'
    data = []
    colors = ['lightcoral', 'lightskyblue']
    explode = (0.1, 0)
    
    data.append(len(overlappingTopSubs))
    data.append(5 - len(overlappingTopSubs))

    plt.pie(data, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')

    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0) # Rewind to beginning of file
    figdata_png = base64.b64encode(figfile.getvalue()).decode('utf8') # Extract string (stream of bytes)
    plt.clf()

    similarityData = con.execute('''SELECT similarity_percent
                              FROM similar_comments SC
                              JOIN chosen_users ON chosen_users.user_id = references_user_id
                              AND username = \'{redditUser}\' '''.format(redditUser=userName))

    # Box Plot of Similarity Percentages
    percentList = []

    for tuple in similarityData:
        percentList.append(int(tuple[0]))

    sampleSize = len(percentList)
    fig = plt.figure(1, figsize=(10, 10))

    ax = fig.add_subplot(111)

    labels = [userName]
    bp = ax.boxplot(percentList,
                    patch_artist=True,
                    vert=True,
                    labels=labels)

    ax.set_title('Distribution of Similarity Percentages (Boxplot)')
    ax.yaxis.grid(True)
    ax.set_xlabel('User Analyzed')
    ax.set_ylabel('Degree of Similarity(%)')
    plt.setp(bp['boxes'], facecolor='lightgreen')



    plt.savefig(figfile, format='png')
    figfile.seek(0)  # Rewind to beginning of file
    boxplot = base64.b64encode(figfile.getvalue()).decode('utf8')  # Extract string (stream of bytes)
    plt.clf()

    # Violin Plot of Similarity Percentages
    ax = sns.violinplot(data=percentList)
    ax.set_xticklabels(labels)
    ax.set_title('Distribution of Similarity Percentages (Violinplot)')
    ax.set_xlabel('User Analyzed')
    ax.set_ylabel('Degree of Similarity (%)')

    plt.savefig(figfile, format='png')
    figfile.seek(0)
    violinplot = base64.b64encode(figfile.getvalue()).decode('utf8')  # Extract string (stream of bytes)
    plt.clf()
    
    
    recentInteractedPosts = con.execute('''WITH recent_comments AS 
                                           (SELECT * 
                                            FROM chosen_users C 
                                            JOIN user_comment U ON C.user_id = U.user_id)
                                            SELECT post_title, P.post_id
                                            FROM post P
                                            JOIN recent_comments ON recent_comments.post_id = P.post_id
                                            WHERE username = \'{redditUser}\''''.format(redditUser=userName))

    posts = {}

    for tuple in recentInteractedPosts:
        posts[tuple[0]] = tuple[1]

    return render_template('report.html',
                           userName=userName,
                           postKarma=postKarma,
                           commentKarma=commentKarma,
                           userId=userId,
                           topCommentDistribution=topCommentDistribution,
                           pieChart=figdata_png,
                           boxplot=boxplot,
                           violinplot=violinplot,
                           posts=posts)


if __name__ == '__main__':
    app.run()
