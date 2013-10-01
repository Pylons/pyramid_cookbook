import json
import time

from persistent import Persistent
from ZODB.POSException import ConflictError

from pyramid.compat import is_nonstr_iter

class LayerFull(Exception):
    pass

class Layer(object):
    """ Append-only list with maximum length.

    - Raise `LayerFull` on attempts to exceed that length.

    - Iteration occurs in order of appends, and yields (index, object)
      tuples.

    - Hold generation (a sequence number) on behalf of `AppendStack`.
    """

    def __init__(self, max_length=100, generation=0):
        self._stack = []
        self._max_length = max_length
        self._generation = generation

    def __iter__(self):
        return enumerate(self._stack)

    def newer(self, latest_index):
        """ Yield items appended after `latest_index`.
        """
        start = latest_index + 1
        items = self._stack[start:]
        for idx, item in enumerate(items):
            yield start+idx, item

    def push(self, obj):
        if len(self._stack) >= self._max_length:
            raise LayerFull()
        self._stack.append(obj)

class AppendStack(Persistent):
    """ Append-only stack w/ garbage collection.

    - Append items to most recent layer until full;  then add a new layer.
    
    - Discard "oldest" layer starting a new one.

    - Invariant:  the sequence of (generation, id) increases monotonically.

    - Iteration occurs in order of appends, and yields
      (generation, index, object) tuples.
    """

    def __init__(self, max_layers=10, max_length=100):
        self._max_layers = max_layers
        self._max_length = max_length
        self._layers = [Layer(max_length, generation=0)]

    def __iter__(self):
        for layer in self._layers:
            for index, item in layer:
                yield layer._generation, index, item

    def __bool__(self):
        return True

    __nonzero__ = __bool__

    def __len__(self):
        return len(list(iter(self)))

    def newer(self, latest_gen, latest_index):
        for gen, index, obj in self:
            if (gen, index) >= (latest_gen, latest_index+1):
                yield gen, index, obj

    def push(self, obj, pruner=None):
        max = self._max_layers
        layers = self._layers
        last_layer = layers[-1]
        try:
            last_layer.push(obj)
        except LayerFull:
            new_layer = Layer(self._max_length,
                              generation=last_layer._generation+1)
            new_layer.push(obj)
            layers.append(new_layer)
        pruned, self._layers = layers[:-max], layers[-max:]
        if pruner is not None:
            for layer in pruned:
                pruner(layer._generation, layer._stack)

    def __getstate__(self):
        layers = [(x._generation, x._stack) for x in self._layers]
        return (self._max_layers, self._max_length, layers)

    def __setstate__(self, state):
        self._max_layers, self._max_length, layer_data = state
        self._layers = []
        for generation, items in layer_data:
            layer = Layer(self._max_length, generation)
            for item in items:
                layer.push(item)
            self._layers.append(layer)

    #
    # ZODB Conflict resolution
    #
    # The overall approach here is to compute the 'delta' from old -> new
    # (objects added in new, not present in old), and push them onto the
    # committed state to create a merged state.
    # Unresolvable errors include:
    # - any difference between O <-> C <-> N on the non-layers attributes.
    # - either C or N has its oldest layer in a later generation than O's
    #   newest layer.
    # Compute the O -> N diff via the following:
    # - Find the layer, N' in N whose generation matches the newest generation
    #   in O, O'.
    # - Compute the new items in N' by slicing it using the len(O').
    # - That slice, plus any newer layers in N, form the set to be pushed
    #   onto C.
    #   
    def _p_resolveConflict(self, old, committed, new):
        o_m_layers, o_m_length, o_layers = old
        c_m_layers, c_m_length, c_layers = committed
        m_layers = [x[:] for x in c_layers]
        n_m_layers, n_m_length, n_layers = new
        
        if not o_m_layers == n_m_layers == n_m_layers:
            raise ConflictError('Conflicting max layers')

        if not o_m_length == c_m_length == n_m_length:
            raise ConflictError('Conflicting max length')

        o_latest_gen = o_layers[-1][0]
        o_latest_items = o_layers[-1][1]
        c_earliest_gen = c_layers[0][0]
        n_earliest_gen = n_layers[0][0]

        if o_latest_gen < c_earliest_gen:
            raise ConflictError('Committed obsoletes old')

        if o_latest_gen < n_earliest_gen:
            raise ConflictError('New obsoletes old')

        new_objects = []
        for n_generation, n_items in n_layers:
            if n_generation == o_latest_gen:
                new_objects.extend(n_items[len(o_latest_items):])
            elif n_generation > o_latest_gen:
                new_objects.extend(n_items)

        while new_objects:
            to_push, new_objects = new_objects[0], new_objects[1:]
            if len(m_layers[-1][1]) == c_m_length:
                m_layers.append((m_layers[-1][0]+1, []))
            m_layers[-1][1].append(to_push)

        return c_m_layers, c_m_length, m_layers[-c_m_layers:]

def set_auditlog(context):
    conn = context._p_jar
    try:
        auditconn = conn.get_connection('audit')
    except KeyError:
        return
    root = auditconn.root()
    if not 'auditlog' in root:
        auditlog = AuditLog()
        root['auditlog'] = auditlog
    
class AuditLogEntry(object):
    def __init__(self, name, oid, payload, timestamp):
        self.name = name
        self.oid = oid
        self.payload = payload
        self.timestamp = timestamp

class AuditLog(Persistent):
    def __init__(self, max_layers=10, layer_size=100, entries=None):
        if entries is None: # for testing
            entries = AppendStack(max_layers, layer_size)
        self.entries = entries

    def __iter__(self):
        """ Iterate over the audit log entries """
        return iter(self.entries)

    def __len__(self):
        """ Return the length of the audit log entry list """
        return len(self.entries)
    
    def __bool__(self):
        return True

    __nonzero__ = __bool__
    
    def add(self, _name, _oid, **kw):
        """ Add a record the audit log.  ``_name`` should be the event name,
        ``_oid`` should be an object oid or ``None``, and ``kw`` should be a
        json-serializable dictionary """
        timestamp = time.time()
        kw.setdefault('time', timestamp)
        payload = json.dumps(kw)
        entry = AuditLogEntry(_name, _oid, payload, timestamp)
        self.entries.push(entry)

    def newer(self, generation, index_id, oids=None):
        """ Return the events newer than the combination of ``generation`` and
        ``oid``.  Filter using ``oids`` if supplied.  """
        if oids and not is_nonstr_iter(oids):
            oids = [oids]
        items = self.entries.newer(generation, index_id)
        for gen, idx, entry in items:
            if (not oids) or entry.oid in oids:
                yield gen, idx, entry

    def latest_id(self):
        """ Return the generation and the index id as a tuple, representing
        the latest audit log entry """
        layers = self.entries._layers
        last_layer = layers[-1]
        gen = last_layer._generation
        index_id = len(last_layer._stack) - 1
        return gen, index_id

def includeme(config): # pragma: no cover
    config.include('.evolve')
