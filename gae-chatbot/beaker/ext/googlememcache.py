
#
# By Preston M. (pentie@gmail.com) 2012.04.11
#

from __future__ import with_statement
from beaker.container import NamespaceManager, Container
from beaker.exceptions import InvalidCacheBackendError 
from beaker.ext.memcached import MemcachedNamespaceManager
from beaker.synchronization import null_synchronizer

googlememcache = None

class GoogleMemcacheNamespaceManager(MemcachedNamespaceManager):

    def __new__(cls, *args, **kw):
        return object.__new__(GoogleMemcacheNamespaceManager)

    @classmethod
    def _init_dependencies(cls):
        global googlememcache
        if googlememcache is not None:
            return
        try:
            googlememcache = __import__('google.appengine.api.memcache').appengine.api.memcache
        except ImportError:
            raise InvalidCacheBackendError("Google Memcache backend requires the "
                                           "'google.appengine.api.memcache' library")

    def __init__(self, namespace, **kw):
        NamespaceManager.__init__(self, namespace)
        self.mc = googlememcache

    def get_access_lock(self):
        return null_synchronizer()

    def get_creation_lock(self, key):
        # this is weird, should probably be present
        return null_synchronizer()

class GoogleMemcacheContainer(Container):
    """Container class which invokes :class:`.GoogleMemcacheNamespaceManager`."""
    namespace_class = GoogleMemcacheNamespaceManager

