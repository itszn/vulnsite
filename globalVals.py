from cache import Cache
from database import Database
import simulation

def init(_args,_root):
    global args
    args = _args

    global db
    db = Database(clean=args.clean)

    global postCache
    postCache = Cache()

    global commentCache
    commentCache = Cache()

    global messageCache
    messageCache = Cache()

    global userNotifCache
    userNotifCache = Cache()

    global root
    root = _root

    global sim
    sim = simulation.Simulation(clean=args.clean)

    global conf
    conf = {"startingPoints":0}
