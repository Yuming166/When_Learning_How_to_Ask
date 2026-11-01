"""Spawned learner receives serialized public JSON only; server stays in parent."""
import json
from .policies import run_policy
from .security import confine_worker


def send(conn,obj):conn.send_bytes(json.dumps(obj,separators=(',',':')).encode())
def receive(conn):return json.loads(conn.recv_bytes())


class Client:
    __slots__=('__connection',)
    def __init__(self,conn):self.__connection=conn
    def _call(self,method,**args):
        send(self.__connection,{'method':method,'args':args});r=receive(self.__connection)
        if 'error' in r:raise RuntimeError(r['error'])
        return r['result']
    def reset(self):return self._call('reset')
    def query(self,j,format):return self._call('query',j=j,format=format)
    def ask_type(self,group):return self._call('ask_type',group=group)
    def get_calibration(self):return self._call('get_calibration')
    def submit(self,predictions):return self._call('submit',predictions=predictions)


def worker(conn,policy):
    isolation=confine_worker()
    while True:
        job=receive(conn)
        if job is None:break
        try:send(conn,{'done':{**run_policy(Client(conn),policy,job),'worker_isolation':isolation}})
        except Exception as exc:send(conn,{'worker_error':type(exc).__name__+': '+str(exc)})
    conn.close()
