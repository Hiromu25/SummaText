from newspaper import Article


# ウェブサイトから記事の内容を取得する関数
def get_article_content(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text
