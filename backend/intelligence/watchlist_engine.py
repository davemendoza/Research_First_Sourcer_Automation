watchlist = set()

def add_to_watchlist(identity):
    watchlist.add(identity)

def get_watchlist():
    return list(watchlist)
