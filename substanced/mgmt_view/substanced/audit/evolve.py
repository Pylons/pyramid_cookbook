from substanced.audit import (
    AuditLog,
    set_auditlog,
    )
from substanced.util import postorder

def remove_bogus_auditlogs(root):
    i = 0
    # Blow away even the root auditlog, as it will have references to
    # AuditLogEntry objects that inherit from Persistent
    for resource in postorder(root):
        i += 1
        if hasattr(resource, '__auditlog__'):
            del resource.__auditlog__
        resource._p_deactivate()
        if i % 1000 == 0:
            resource._p_jar.cacheGC()

def add_root_auditlog(root):
    root.__auditlog__ = AuditLog()

def use_external_db(root):
    if hasattr(root, '__auditlog__'):
        del root.__auditlog__
    set_auditlog(root)
        
def includeme(config):
    config.add_evolution_step(remove_bogus_auditlogs)
    config.add_evolution_step(add_root_auditlog)
    config.add_evolution_step(use_external_db)

