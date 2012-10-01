import settings as test_settings
from django.conf import settings
settings.configure(**test_settings.__dict__)

if __name__ == "__main__":
    
    from django.core.urlresolvers import reverse_lazy, reverse
    from pprint import pprint
    from url_namespaces import modulize
    from url_namespaces import Namespace, View, Redirect, ReverseRedirect, KeywordReverseRedirect
    
    
    class MyOtherURLs(Namespace):
        
        class Meta:
            namespace = 'page' # optional
            app_name = 'blog' # optional
            view_prefix = 'views' # optional
        
        rss = View(
            r'^(?P<blog>[\w\-]+)/rss/?$',
                'blogrss',
                arg='yo', other_arg='dogg')
        
        index = View(
            r'^(?P<blog>[\w\-]+)/$',
                'blogpage')
        
        entry = View(
            r'^(?P<blog>[\w\-]+)/(?P<entry>[\w\-]+)/?$',
                'blogentrypage')
    
    
    class MyURLs(Namespace):
        
        class Meta:
            namespace = 'blog' # optional
            app_name = 'blog' # optional
            view_prefix = 'ost2.blog' # optional
        
        pages = MyOtherURLs(r'^/pages/')
        
        elsewhere = Redirect(
            r'^/yodogg?',
                "http://www.yodogg.com/")
        
        root = ReverseRedirect(
            r'^/?',
                'blog:index', blog="ost")
        
        entry_redirect = ReverseRedirect(
            r'^blog/(?P<blog>[\w\-]+)/(?P<entry>[\w\-]+)/?$',
                'blog:entry', blog="%(blog)s", entry="%(entry)s")
        
        entry_redirect_again = KeywordReverseRedirect(
            r'^blog/(?P<blog>[\w\-]+)/(?P<entry>[\w\-]+)/?$',
                'blog:entry')
    
    
    ns = MyURLs(r'^/?')
    md = modulize(ns)
    out = md.urlpatterns
    #pprint(ns.evaluate())
    pprint(out)
    print ""
    
    pprint(ns._meta.__dict__)
    print ""
    pprint(ns.pages._meta.__dict__)
    print ""
    
    print "REVERSE: %s" % reverse('blog:page:entry',
        urlconf=md, current_app='blog',
        kwargs=dict(blog='ost-blog', entry='yo-dogg-i-heard-you-liked-blogs'))
    #pprint(modulize(ns.grafs).urlpatterns)

