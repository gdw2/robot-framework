#  Copyright 2008 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


from types import StringTypes

from robot.errors import DataError
from normalizing import NormalizedDict


class ConnectionCache:

    """Connection cache for different Robot test libraries that use connections.

    This cache stores connections and allows switching between them using
    generated indexes or user given aliases. Can be used for example by web
    testing libraries where there's need for multiple concurrent connections.
    
    Note that in most cases there should be only one instance of this class but
    this is not enforced.
    """

    def __init__(self, no_current_msg='No open connection'):
        self.current = None
        self.connections = []
        self.aliases = NormalizedDict()
        self.no_current_msg = no_current_msg
        
    def get_current(self):
        if self.current is None:
            raise DataError(self.no_current_msg)
        return self.current
        
    def register(self, connection, alias=None):
        """Registers given connection with optional alias and returns its index.
        
        Given connection is set to be the current connection. Alias must be 
        a string. The index of the first connection after initialization or
        close_all or empty_cache is 1, second is 2, etc.
        """
        self.current = connection
        self.connections.append(connection)
        index = len(self.connections)
        if alias is not None and type(alias) in StringTypes:
            self.aliases[alias] = index
        return index
    
    def switch(self, index_or_alias):
        """Switches to the connection specified by given index or alias.
        
        If alias is given it must be a string. Indexes can be either integers
        or strings that can be converted into integer. Raises a DataError
        if no connection with given index or alias found.
        """
        try:
            index = self._get_index(index_or_alias)
        except ValueError:
            raise DataError("Non-existing index or alias '%s'" % index_or_alias)
        self.current = self.connections[index-1]
        return self.current

    def close_all(self, closer_method='close'):
        """Closes connections using given closer method and empties cache.
        
        If simply calling the closer method is not adequate for closing
        connections, clients should close connections themselves and use
        empty_cache afterwards.         
        """
        for conn in self.connections:
            getattr(conn, closer_method)()
        self.empty_cache()
        return self.current
                
    def empty_cache(self):
        """Empties the connections cache.
        
        Indexes of new connections starts from 1 after this."""
        self.current = None
        self.connections = []
        self.aliases = NormalizedDict()
        
    def _get_index(self, index_or_alias):
        try:
            return self._resolve_alias(index_or_alias)
        except ValueError:
            return self._resolve_index(index_or_alias)
    
    def _resolve_alias(self, alias):
        if type(alias) in StringTypes:
            try:
                return self.aliases[alias]
            except KeyError:
                pass
        raise ValueError

    def _resolve_index(self, index):
        index = int(index)
        if not 0 < index <= len(self.connections):
            raise ValueError
        return index
