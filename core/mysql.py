import MySQLdb

class Mysql:
    
    # Python Mysql Class
    # by L.Conti 2017

    _host = None
    _db = None
    _user = None
    _passwd = None
    _cn = None
    _cur = None
    _log = []

    def __init__(self, host='localhost', user='root', passwd='', db='', port=3306):

        self._host = host
        self._user = user
        self._passwd = passwd
        self._db = db
        self._port = port

        c = MySQLdb.connect (
                host = self._host,
                user = self._user,
                passwd = self._passwd,
                port= self._port,
                db = self._db
        )
            
        self._cn = c
        self._cur = self._cn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

    def query_log(self):
        return self._log

    def query(self, q, data):

        q = q.strip()
        #print(q % tuple(data))
        #self._log.append(q % tuple(data))
        #self._log = self._log[:-10] 

        self._cur.execute(q, data)

        if q.startswith('SELECT'):
            return self._cur.fetchall()
        
        if q.startswith('UPDATE') or q.startswith('INSERT') or q.startswith('DELETE'):

            self._cn.commit()

            if q.startswith('INSERT'):
                return self._cn.insert_id()

        return {}
        

    def insert_id(self):

        self._cn.insert_id()
            
    def close(self):
        
        try:
            self._cur.close()
            self._cn.close()
        except:
            pass