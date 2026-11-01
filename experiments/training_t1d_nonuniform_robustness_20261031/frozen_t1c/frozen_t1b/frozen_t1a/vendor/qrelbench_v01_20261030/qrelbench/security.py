"""Linux-only file confinement for the built-in learner worker.

Landlock denies handled new file operations and TCP bind/connect after bootstrap.
Existing JSON pipe descriptors remain usable. Parent is non-dumpable to prevent
same-UID child ptrace/process_vm_readv. This is not a general kernel sandbox.
"""
import ctypes
import os
import platform


def protect_evaluator():
    libc=ctypes.CDLL(None,use_errno=True)
    if libc.prctl(4,0,0,0,0)!=0:raise OSError(ctypes.get_errno(),'PR_SET_DUMPABLE failed')


def confine_worker():
    if platform.system()!='Linux' or platform.machine()!='x86_64':raise RuntimeError('Audited Linux x86_64 sandbox required')
    if len(os.listdir('/proc/self/task'))!=1:raise RuntimeError('Single-threaded worker bootstrap required')
    libc=ctypes.CDLL(None,use_errno=True)
    abi=libc.syscall(444,0,0,1)
    if abi<4:raise RuntimeError('Landlock ABI >=4 required; refuse unconfined worker')
    class Ruleset(ctypes.Structure):
        _fields_=[('handled_access_fs',ctypes.c_uint64),('handled_access_net',ctypes.c_uint64)]
    rule=Ruleset((1<<15)-1,3)
    fd=libc.syscall(444,ctypes.byref(rule),ctypes.sizeof(rule),0)
    if fd<0:raise OSError(ctypes.get_errno(),'Landlock ruleset creation failed')
    try:
        if libc.prctl(38,1,0,0,0)!=0:raise OSError(ctypes.get_errno(),'NO_NEW_PRIVS failed')
        if libc.syscall(446,fd,0)!=0:raise OSError(ctypes.get_errno(),'Landlock confinement failed')
    finally:os.close(fd)
    return {'landlock_abi':abi,'handled_new_file_operations':'denied','tcp_bind_connect':'denied',
            'no_new_privileges':True,'single_thread_bootstrap':True,
            'scope':'controlled JSON RPC; pre-existing descriptors retained; stat metadata allowed; not a general kernel sandbox'}
