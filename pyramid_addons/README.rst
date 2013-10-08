Pyramid Add-On Developer Tutorial
=================================

Temporary holding place for material in Brazil.


- (project_setup) Make a project
  - pyramid_demo
    - depends on pyramid_jinja2
  - my_demo
- config.include
  - included in the other
  - config.include('pyramid_jinja2')
  - Explain ordering on .include vs. .scan
- Settings
  - pyramid_demo expects the WSGI app to provide a copyright setting
  - pyramid_demo
    - View class gets copyright from request.settings, or "No copyright"
    - copyright statement in layout.jinja2 footer
  - my_demo
    - Assign copyright in settings
- override asset
  - In pyramid_demo:
    - make a layout with breadcrumbs etc.
    - Move the inline CSS to a static asset
  - my_demo:
    - override breadcrumbs, css
- Override view
- Custom request method
  - pyramid_demo
    - Discuss request.authenticated_user
    - Make request.layout as a "layout api"
    - Have a request.site_help returning a dict of label/href
    - Sprinkle into footer of layout.jinja2
  - my_demo
    - Add help to end of breadcrumbs
- Custom view predicate
  - Get quick_traversal/hierarchy in place
  - Add an "audience" predicate
  - Set audience=['novice', 'intermediate', 'advanced'] on content
  - @view_config(audience='novice', renderer='different template')