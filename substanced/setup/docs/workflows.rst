Workflows
=========

A workflow is a collection of :term:`transitions` that :term:`transition`
between :term:`states`. Specifically, :mod:`substanced.workflow` implements
`event-driven finite-state machine
<https://en.wikipedia.org/wiki/Finite-state_machine>`_ workflows.

Workflows are used to ease following tasks when content goes through the
lifecycle:

- updating security (adding/removing permissions)
- sending emails
- ...

States and transitions together with metadata are stored on the
:class:`~substanced.workflow.Workflow`. Workflows are stored in
``config.registry.workflows``. The only thing that content has from the
workflow machinery is ``content.__workflow_state__`` attribute that stores a
dict of all workflow types and corresponding states assigned. When content is
added to the database (:class:`~substanced.event.ObjectAdded` event is
emitted), all relevant registered workflows are initialized for it.


Features
--------

- Site-wide workflows
- Multiple workflows per object
- Content type specific workflows
- Restrict transitions by permission
- Configurable callbacks when entering state
- Configurable callbacks when executing transition
- Reset workflow to initial state

Adding a workflow
-----------------

Suppose we want to add a simple workflow::

   /-----\   <-- to_draft -----   /---------\
   |draft|                        |published|
   \-----/   --- to_publish -->   \---------/

Using :func:`~substanced.workflow.add_workflow` Pyramid configuration
directive::

    >>> workflow = Workflow(initial_state="draft", type="article")
    >>> workflow.add_state("draft")
    >>> workflow.add_state("published")
    >>> workflow.add_transition('to_publish', from_state='draft', to_state='published')
    >>> workflow.add_transition('to_draft', from_state='published', to_state='draft')

    ... 

    >>> config.add_workflow(workflow, ('News',))

Interaction with the workflow
-----------------------------

Retrieve a :class:`~substanced.workflow.Workflow` instance using
the :func:`substanced.workflow.get_workflow`::

    >>> from substanced.workflow import get_workflow

    >>> workflow = get_workflow(request, type='article', content_type='News')

Suppose there is a `context` object at hand, you can
:meth:`~substanced.workflow.Workflow.reset` its workflow to initial state::

    >>> workflow.reset(context, request)

You could check it :meth:`~substanced.workflow.Workflow.has_state` and assert
:meth:`~substanced.workflow.Workflow.state_of` `context` is initial state name
of the workflow::

    >>> assert workflow.has_state(context) == True
    >>> assert workflow.state_of(context) == workflow.initial_state

List possible transitions from the current state of the workflow
with :meth:`~substanced.workflow.Workflow.get_transitions`::

    >>> workflow.get_transitions(context, request)
    [{'from_state': 'draft',
      'callback': None,
      'permission': None,
      'name': 'to_publish',
      'to_state': 'published'}]

Execute a :meth:`~substanced.workflow.Workflow.transition`::

    >>> workflow.transition(context, request, 'to_publish')

List all states of the workflow with
:meth:`~substanced.workflow.Workflow.get_states`::

    >>> workflow.get_states(context, request)
    [{'name': 'draft',
      'title': 'draft',
      'initial': True,
      'current': False,
      'transitions': [{'from_state': 'draft',
                       'callback': None,
                       'permission': None,
                       'name': 'to_publish',
                       'to_state': 'published'}],
      'data': {'callback': None}},
     {'name': 'published',
      'title': 'published',
      'initial': False,
      'current': True,
      'transitions': [{'from_state': 'published',
                       'callback': None,
                       'permission': None,
                       'name': 'to_draft',
                       'to_state': 'draft'}],
      'data': {'callback': None}}]

Execute a :meth:`~substanced.workflow.Workflow.transition_to_state`::

    >>> workflow.transition_to_state(context, request, 'draft')

Using callbacks
---------------

Typically you will want to define custom actions when transition is executed
or when content enters a specific state. Let's define a transition with
a callback::

    >>> def cb(context, **kw):
    ...     print "keywords: ", meta

    >>> workflow.add_transition('to_publish_with_callback',
    ...                         from_state='draft',
    ...                         to_state='published',
    ...                         callback=cb)


When you execute the transition, callback is called::

    >>> workflow.transition(context, request, 'to_publish_with_callback')
    keywords: {'workflow': <Workflow ...>, 'transition': {'to_state': 'published', 'from_state': 'draft', ...}, request=<Request ...>}

To know more about callback parameters, read
:meth:`~substanced.workflow.Workflow.add_transition` signature.
