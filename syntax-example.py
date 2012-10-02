    # urls.py (née 'URLConf')

    from django.conf.urls import patterns
    from url_namespaces import (Namespace, View, Redirect, \
                                ReverseRedirect, KeywordReverseRedirect)


    class MyOtherURLs(Namespace):
        
        class Meta:
            namespace = 'testapp:views'
            app_name = 'testapp'
            view_prefix = ''
        
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
            namespace = 'testapp'
            app_name = 'testapp'
            view_prefix = ''
        
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