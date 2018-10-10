from dc.models.queries import Queries
from dc.utils.commun import Commun
from dc.utils.dbwrap import Dbwrap

q = Queries()
func = Commun()
conf = func.config_info()
db = Dbwrap(conf["path_to_database"])


class Batches:
