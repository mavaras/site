# Standard libraries
import csv
import os

# Third party libraries
from flask import (
    Flask,
    render_template,
    request,
)
from flask_cors import CORS
from misaka import (
    Markdown,
    HtmlRenderer,
)
import pandas as pd

# Local libraries
from constants import MUSIC_SPREADSHEET_LINK


POSTS_PATH = os.path.join(
    os.path.dirname(__file__),
    f'static/md/blog'
)
PROJECTS_PATH = os.path.join(
    os.path.dirname(__file__),
    f'static/md/projects'
)

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/projects')
def projects():
    projects = []
    html_renderer = HtmlRenderer()
    md_handle = Markdown(html_renderer, extensions=['tables'])
    md_files = os.listdir(PROJECTS_PATH)
    md_files.sort()
    titles = []
    for md in md_files:
        md_file = open(f'{PROJECTS_PATH}/{md}').read()
        projects.append(md_handle(md_file))

    return render_template('projects.html', projects=projects)


@app.route('/about')
def about():
    return render_template('about.html')


def read_csv():
    pd.set_option('display.max_rows', None)
    dfs = pd.read_csv(
        MUSIC_SPREADSHEET_LINK,
        sep='\t',
        encoding='utf-8',
        error_bad_lines=False,
        names=['Album', 'Author', 'Year', 'Genre', '', 'Cover'],
        quoting=csv.QUOTE_NONE
    )
    rows = [list(row) for row in dfs.values][1:]

    return rows

@app.route('/music')
def music():
    rows = read_csv()

    return render_template('music.html', rows=sorted(rows, key=lambda row: row[1]))


@app.route('/blog')
def blog():
    posts = os.listdir(POSTS_PATH)
    titles = []
    for post in posts:
        titles.append(open(f'{POSTS_PATH}/{post}').readline().split('**')[1])
    posts_info = [
        [post.split('_')[0], post.split('_')[1].split('.')[0]]
        for post in posts
    ]
    posts = [
        {'id': post_info[0], 'date': post_info[1].replace('-', '/'), 'title': titles[i]}
        for i, post_info in enumerate(posts_info)
    ]

    return render_template('blog.html', posts=posts)


@app.route('/blog/post/<post_id>')
def blog_post(post_id):
    post = ''
    for post in os.listdir(POSTS_PATH):
        if post_id in post:
            break
    html_renderer = HtmlRenderer()
    md_handle = Markdown(html_renderer, extensions=['tables'])
    md_file = open(f'{POSTS_PATH}/{post}').read()
    md = md_handle(md_file)
    md = md.replace('<p>', '<p style="text-align: justify">')

    return render_template('blog_post.html', md=md)
