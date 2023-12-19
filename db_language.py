CREATE_SEARCHES = '''CREATE TABLE IF NOT EXISTS searches
                  (user_id INTEGER, query TEXT, movie_title TEXT)'''

CREATE_STATS = '''CREATE TABLE IF NOT EXISTS stats
                  (user_id INTEGER, movie_title TEXT, count INTEGER DEFAULT 1)'''

SHOW_HISTORY = '''SELECT DISTINCT query FROM searches WHERE user_id=?'''

SHOW_STATS = '''SELECT movie_title, count FROM stats WHERE user_id=?'''

ADD_TO_SEARCHERS = '''INSERT INTO searches (user_id, query, movie_title) VALUES (?, ?, ?)'''

select_query = """
    SELECT count FROM stats
    WHERE user_id = ? AND movie_title = ?;
"""

delete_query = """
    DELETE FROM stats
    WHERE user_id = ? AND movie_title = ?;
"""

insert_query = """
    INSERT INTO stats (user_id, movie_title, count)
    VALUES (?, ?, ?);
"""
