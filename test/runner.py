
import settings as test_settings
from django.conf import settings
settings.configure(**test_settings.__dict__)

print ""
print "ROOT_URLCONF = %s" % settings.ROOT_URLCONF
print ""

if __name__ == "__main__":
    
    from django.core.urlresolvers import reverse
    from django.core.urlresolvers import NoReverseMatch
    
    try:
        print "REVERSE: %s" % reverse('testapp:views:entry',
            current_app='testapp',
            kwargs=dict(blog='ost-blog', entry='yo-dogg-i-heard-you-liked-blogs'))
    except NoReverseMatch, err:
        print "NoReverseMatch: %s" % err
    
    print ""
    
    try:
        print "REVERSE: %s" % reverse('testapp:testapp:entry',
            current_app='testapp',
            kwargs=dict(blog='ost-blog', entry='yo-dogg-i-heard-you-liked-blogs'))
    except NoReverseMatch, err:
        print "NoReverseMatch: %s" % err
    
    print ""
    
    from test import urls
    from url_namespaces import modulize
    try:
        print "REVERSE: %s" % reverse('testapp:entry',
            current_app='testapp',
            kwargs=dict(blog='ost-blog', entry='yo-dogg-i-heard-you-liked-blogs'))
    except NoReverseMatch, err:
        print "NoReverseMatch: %s" % err
    
    #from pprint import pprint
    #pprint(modulize(ns.grafs).urlpatterns)

