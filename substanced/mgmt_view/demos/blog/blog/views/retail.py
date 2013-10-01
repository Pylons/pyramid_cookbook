import datetime
import pytz

from docutils.core import publish_parts
from webob import Response

from pyramid.url import resource_url
from pyramid.view import view_config
from pyramid.security import authenticated_userid

def _getentrybody(format, entry):
    if format == 'rst':
       body = publish_parts(entry, writer_name='html')['fragment']
    else:
       body = entry
    return body

@view_config(
    renderer='templates/frontpage.pt',
    content_type='Root',
    )
def blogview(context, request):
    blogentries = []
    for name, blogentry in context.items():
        if request.registry.content.istype(blogentry, 'Blog Entry'):
            blogentries.append(
                {'url': resource_url(blogentry, request),
                 'title': blogentry.title,
                 'body': _getentrybody(blogentry.format, blogentry.entry),
                 'pubdate': blogentry.pubdate,
                 'numcomments': len(blogentry['comments'].values()),
                 })
    blogentries.sort(key=lambda x: x['pubdate'].isoformat())
    blogentries.reverse()
    dates = {}
    for entry in blogentries:
        date = entry['pubdate']
        date = getattr(date, 'date', lambda: date)()
        d_entries = dates.setdefault(date, [])
        d_entries.append(entry)
    date_entries = reversed(sorted(dates.items()))
    logged_in = authenticated_userid(request)
    return dict(
        request = request,
        logged_in = logged_in,
        date_entries = date_entries,
        rss_url = request.application_url + '/' + 'rss.xml',
        )

@view_config(
    content_type='Blog Entry',
    renderer='templates/blogentry.pt',
    )
def blogentry_view(context, request):
    commenter_name = ''
    comment_text = ''
    spambot = ''
    message = ''
    pubdate = ''
    comments = context['comments'].values()
    attachments = context['attachments'].values()

    if 'form.submitted' in request.params:
        commenter_name = request.params.get('commenter_name')
        spambot = request.params.get('spambot')
        comment_text = request.params['comment_text']
        if spambot:
           message = 'Your comment could not be posted'
        elif comment_text == '':
           message = 'Please enter a comment'
        elif commenter_name == '':
           message = 'Please enter your name'
        else: 
           pubdate = datetime.datetime.now()
           comment = request.registry.content.create(
               'Comment', commenter_name, comment_text, pubdate)
           context.add_comment(comment)

    body = _getentrybody(context.format, context.entry)
    logged_in = authenticated_userid(request)
    return dict(
        blogentry = body,
        request = request,
        message = message,
        title = context.title,
        entry = context.entry,
        format = context.format,
        pubdate = context.pubdate,
        url = request.resource_url(context),
        commenter_name = commenter_name,
        comment_text = comment_text,
        comments = comments,
        attachments = attachments,
        spambot = spambot,
        logged_in = logged_in,
        frontpage_url = request.resource_url(context.__parent__),
        )

@view_config(
    content_type='File',
    name='download.html',
    )
def download_attachment(context, request):
    f = context.blob.open()
    headers = [('Content-Type', str(context.mimetype)),
               ('Content-Disposition',
                    'attachment;filename=%s' % str(context.__name__)),
              ]
    response = Response(headerlist=headers, app_iter=f)
    return response

class FeedViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _nowtz(self):
        now = datetime.datetime.utcnow() # naive
        y, mo, d, h, mi, s = now.timetuple()[:6]
        return datetime.datetime(y, mo, d, h, mi, s, tzinfo=pytz.utc)

    def _get_feed_info(self):
        context = self.context
        request = self.request
        feed = {"rss_url": request.application_url + "/rss.xml",
                "atom_url": request.application_url + "/index.atom",
                "blog_url": request.application_url,
                "title": context.sdi_title,
                "description": context.description,
                }

        def _add_updated_strings(updated, info):
            if getattr(updated, 'now', None) is None:
                y, mo, d, h, mi, s = updated.timetuple()[:6]
                updated = datetime.datetime(y, mo, d, h, mi, s, tzinfo=pytz.utc)
            info['updated_atom'] = updated.astimezone(pytz.utc).isoformat()
            info['updated_rss'] = updated.strftime('%a, %d %b %Y %H:%M:%S %z')

        blogentries = []
        for name, blogentry in context.items():
            if request.registry.content.istype(blogentry, 'Blog Entry'):
                updated = blogentry.pubdate
                info = {'url': resource_url(blogentry, request),
                        'title': blogentry.title,
                        'body': _getentrybody(blogentry.format,
                                              blogentry.entry),
                        'created': updated,
                        'pubdate': updated,
                       }
                _add_updated_strings(updated, info)
                blogentries.append((updated, info))
                
        blogentries.sort(key=lambda x: x[0].isoformat())
        blogentries = [entry[1] for entry in reversed(blogentries)][:15]
        updated = blogentries and blogentries[0]['pubdate'] or self._nowtz()
        _add_updated_strings(updated, feed)
        
        return feed, blogentries

    @view_config(
        name='rss.xml',
        renderer='templates/rss.pt',
        )
    def blog_rss(self):
        feed, blogentries = self._get_feed_info()
        self.request.response.content_type = 'application/rss+xml'
        return dict(
            feed = feed,
            blogentries = blogentries,
            )

    @view_config(
        name='index.atom',
        renderer='templates/atom.pt',
        )
    def blog_atom(self):
        feed, blogentries = self._get_feed_info()
        self.request.response.content_type = 'application/atom+xml'
        return dict(
            feed = feed,
            blogentries = blogentries,
            )
