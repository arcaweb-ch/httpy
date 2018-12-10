class Confparser():

    # Simple config file parser [L.Conti]

    def __init__(self, filepath):
        raw_conf = open(filepath, 'r').read().replace('\r','')
        self.conf = []
        for r in raw_conf.split('\n'):
            if '#' in r:
                r = r.partition('#')[0]
            if ' ' in r.strip():
                self.conf.append(r.strip())

    def get_all(self, var):
        values = []
        for r in self.conf:
            if r.partition(' ')[0] == var:
                values.append(r.partition(' ')[2])
        return values
        
    def get(self, var):
        for r in self.conf:
            if r.partition(' ')[0] == var:
                return r.partition(' ')[2]
        return ''
    
    def dump(self):
        return self.conf