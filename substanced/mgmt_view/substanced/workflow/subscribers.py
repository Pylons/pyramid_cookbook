from ..util import (
    postorder,
    get_content_type,
    )

from ..event import subscribe_added

@subscribe_added()
def init_workflows_for_object(event):
    """Initialize workflows when object is added to db.
    """
    if event.moving is not None: # it's being moved
        return

    added = event.object
    registry = event.registry

    for obj in postorder(added):
        # XXX note that this logic will be called for the same set of
        # objects more than once in this scenario:
        #
        # f1 = Folder()
        # f2 = Folder()
        # someobject = SomeContentType()
        # f2['someobject'] = someobject # executed once for someobject
        # f1['f2'] = f2 # executed once for f2, then someobject
        #
        content_type = get_content_type(obj)
        if content_type is not None:
            # XXX maybe we should register workflows not relevant
            # to specific content type?
            for wf in registry.workflow.get_all_types(content_type):
                if not wf.has_state(obj):
                    wf.initialize(obj)

