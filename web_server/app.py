import os
import jieba

from flask import Flask
from flask import request, render_template, redirect, url_for
from SearchEngine.search import IndexSearch
from DoubanMovieCrawler.DoubanMovieCrawler.database import col
from utils.validator import match_words

app = Flask(
    __name__,
    template_folder=os.path.join(os.getcwd(), 'templates'),
    static_folder=os.path.join(os.getcwd(), 'templates'),
    static_url_path=''
)


@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('fuzzy_search'))


@app.route('/fuzzy-search', methods=['GET'])
def fuzzy_search():
    query_words = request.args.get('query_words', None)
    page = int(request.args.get('page', '1'))

    if query_words is None:
        return render_template('fuzzy-search.html')

    data_path_name = os.path.dirname(__file__)
    searcher = IndexSearch(os.path.abspath(os.path.dirname(data_path_name)))
    scores = searcher.calculate_bm25(query_words)

    page_num = (len(scores) + 5 - 1) // 5
    results = []
    for score in scores[(page - 1) * 5:page * 5]:
        results.append(col.find_one({'douban_id': score[0]}))

    return render_template('fuzzy-search-result.html', query_words=query_words, results=results, page_num=page_num)


@app.route('/precise-search', methods=['GET'])
def precise_search():
    query_words = request.args.get('query_words', None)
    search_type = int(request.args.get('search_type', '1'))

    if query_words is None:
        return render_template('precise-search.html')

    query = jieba.lcut(query_words)
    query = list(filter(match_words, query))

    if search_type == 1:
        query = list(map(lambda i: {'name': {'$regex': i}}, query))
        results = list(col.find({'$and': query}))
    elif search_type == 2:
        query = list(map(lambda i: {'directors': {'$elemMatch': {'$regex': i}}}, query))
        results = list(col.find({'$and': query}))
    elif search_type == 3:
        query = list(map(lambda i: {'actors': {'$elemMatch': {'$regex': i}}}, query))
        results = list(col.find({'$and': query}))
    else:
        return redirect(url_for('precise_search'))

    page_num = (len(results) + 5 - 1) // 5

    return render_template('precise-search-result.html', query_words=query_words, results=results, page_num=page_num,
                           search_type=search_type)


if __name__ == '__main__':
    app.run()
