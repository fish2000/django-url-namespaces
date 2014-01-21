django-url-namespaces
=====================

This is a somewhat-functional attempt to bring a more intuitive and less spaghettified syntax to Django's URLConf. It implements a declarative class-based syntax:


    # urls.py (née 'URLConf')

    from django.conf.urls import patterns
    from url_namespaces import (Namespace, View, Redirect, \
                                ReverseRedirect, KeywordReverseRedirect)


    class MyOtherURLs(Namespace):
        """ URL namespaces are classes, 
            the URLs they contain are properties
            of those classes. """
        
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
        """ Namespaces can be nested """
        
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

    # These classes generate standard URL patterns
    # and use url(), reverse(), RegexURLResolver;
    # the project aims for compatibility with Django's
    # URLConf structures. 
    
    urlpatterns = patterns('',
        MyURLs(r'^/?').connect('testapp'))


Djano-URL-Namespaces implements a host of combinator objects, representing intuitive ideas e.g. `View`, `Redirect`, `Namespace` &c,
which can be modularly rearranged without the worries incumbent in getting ones' hands dirty with the rather fragile Django-native
URLConf syntax.

At the time of writing the project is in a state of somewhat indeterminate disrepair; namespaces don't nest quite right, there's a lot of sketchy code commented out and not enough docstrings, etc. If this is the sort of thing that floats your boat, know that I never turn away an entertaining pull-request, indeed!


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/fish2000/django-url-namespaces/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

