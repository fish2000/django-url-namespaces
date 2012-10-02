
from django.core.urlresolvers import reverse
#from django.core.urlresolvers import reverse_lazy
from django.conf.urls import patterns
from pprint import pprint
from url_namespaces import modulize
from url_namespaces import Namespace, View, Redirect, ReverseRedirect, KeywordReverseRedirect


class MyOtherURLs(Namespace):
        
    class Meta:
        namespace = 'testapp:views' # optional
        app_name = 'testapp' # optional
        view_prefix = '' # optional
        
    rss = View(
        r'^(?P<blog>[\w\-]+)/rss/?$',
            'testapp.views.blogrss',
            arg='yo', other_arg='dogg')
        
    index = View(
        r'^(?P<blog>[\w\-]+)/$',
            'testapp.views.blogpage')
        
    entry = View(
        r'^(?P<blog>[\w\-]+)/(?P<entry>[\w\-]+)/?$',
            'testapp.views.blogentrypage')
    
    
class MyURLs(Namespace):
        
    class Meta:
        namespace = 'testapp' # optional
        app_name = 'testapp' # optional
        view_prefix = '' # optional
        
    pages = MyOtherURLs(r'^/pages/')
        
    elsewhere = Redirect(
        r'^/yodogg?',
            "http://www.yodogg.com/")
        
    root = ReverseRedirect(
        r'^/?',
            'testapp:index', blog="test")
        
    entry_redirect = ReverseRedirect(
        r'^blog/(?P<blog>[\w\-]+)/(?P<entry>[\w\-]+)/?$',
            'testapp:entry', blog="%(blog)s", entry="%(entry)s")
        
    entry_redirect_again = KeywordReverseRedirect(
        r'^blog/(?P<blog>[\w\-]+)/(?P<entry>[\w\-]+)/?$',
            'testapp:entry')


urlpatterns = patterns('',
    MyURLs(r'^/?').connect('testapp'))



pprint(urlpatterns)


#md = modulize(ns)
#out = md.urlpatterns
#pprint(ns.evaluate())
#pprint(out)
#print ""

#pprint(ns._meta.__dict__)
#print ""
#pprint(ns.pages._meta.__dict__)
#print ""


