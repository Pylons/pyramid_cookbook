import BTrees

def oobtreeify_referencemap(root): # pragma: no cover
    objectmap = root.__objectmap__
    refmap = objectmap.referencemap.refmap
    for k, refset in refmap.items():
        refset.src2target = BTrees.family64.OO.BTree(refset.src2target)
        refset.target2src = BTrees.family64.OO.BTree(refset.target2src)

def oobtreeify_object_to_path(root): # pragma: no cover
    objectmap = root.__objectmap__
    oobtree = BTrees.family64.OO.BTree
    objectmap.objectid_to_path = oobtree(objectmap.objectid_to_path)
    objectmap.path_to_objectid = oobtree(objectmap.path_to_objectid)

def includeme(config): # pragma: no cover
    config.add_evolution_step(oobtreeify_referencemap)
    config.add_evolution_step(oobtreeify_object_to_path)
