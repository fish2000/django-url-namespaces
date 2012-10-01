
"""

from django.conf.urls.defaults import patterns, url, include

app_patterns = patterns('ost2.twemoir',
    url(r'^grafs/(?P<option>[\w\-]+)/?$',
        'views.paragraphs',
        name="grafs_option"),

    url(r'^blog/(?P<blog>[\w\-]+)/(?P<entry>[\w\-]+)/?$',
        redirect_to, {
            'url': app_reverse_lazy('blog:entry',
                kwargs={ 'blog': "%(blog)s", 'entry': "%(entry)s", }),
            },
        name="entry_redirect"),
    
    url(r'^/?',
        redirect_to, {
            'url': app_reverse_lazy('blog:index',
                kwargs={ 'blog': "ost", }),
            },
        name="root"),
        
)

urlpatterns = patterns('',
    url(r'', include(app_patterns,
        namespace='twemoir', app_name='twemoir')),
)

class MyURLs(Namespace):
    
    class Meta:
        namespace = 'blog' # optional
        app_name = 'blog' # optional
        view_prefix = 'ost2.twemoir' # optional
    
    grafs_option = View(
        r'^grafs/(?P<option>[\w\-]+)/?$',
            'views.paragraphs')
    
    grafs_option_args = View(
        r'^grafs/(?P<option>[\w\-]+)/?$',
            'views.paragraphs',
            arg='yo', other_arg='dogg')
    
    elsewhere = Redirect(
        r'^/yodogg?',
            "http://www.yodogg.com/")
    
    root = ReverseRedirect(
        r'^/?',
            'blog:index', blog="ost")
        
    entry_redirect = ReverseRedirect(
        r'^blog/(?P<blog>[\w\-]+)/(?P<entry>[\w\-]+)/?$',
            'blog:entry', blog="%(blog)s", entry="%(entry)s")
    
    entry_redirect = KeywordReverseRedirect(
        r'^blog/(?P<blog>[\w\-]+)/(?P<entry>[\w\-]+)/?$',
            'blog:entry')
    
    
    
    



"""

class ArgumentSinkDescriptor(object):
    def __init__(self, arg_sink):
        self.name = arg_sink.name
    
    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                "The '%s' attribute can only be accessed from %s instances."
                % (self.arg_sink.name, owner.__name__))
        return instance.__dict__[self.name].evaluate()
    
    def __set__(self, instance, options):
        instance.__dict__[self.name].process(**options)

class ArgumentSink(object):
    creation_counter = 0
    
    def __init__(self, *args, **kwargs):
        self.creation_counter = ArgumentSink.creation_counter
        ArgumentSink.creation_counter += 1
        self._args = args
        self._kwargs = kwargs
    
    def contribute_to_class(self, cls, name):
        self.name = name
        setattr(cls, name, self)
        if hasattr(cls, '_meta'):
            if hasattr(cls._meta, 'options'):
                self._options = cls._meta.options
                self.process(**cls._meta.options)
    
    def process(self, **options):
        for option_name, option in self._options.iteritems():
            setattr(self, option_name, options.pop(option_name, option))
    
    def evaluate(self):
        return \
            tuple(self._args) + \
            tuple(self._kwargs.items())

class URLBase(ArgumentSink):
    def __init__(self, url_pattern, action, *args, **kwargs):
        self.url_pattern = url_pattern
        self.action = action
        super(URLBase, self).__init__(*args, **kwargs)
    
    def evaluate(self):
        from django.conf.urls.defaults import url
        return url(
            self.url_pattern, self.action, self._kwargs,
            name=self.name)

class View(URLBase):
    def evaluate(self):
        if isinstance(self.action, basestring):
            if isinstance(self.view_prefix, basestring):
                if len(self.view_prefix) > 0:
                    new_action = ".".join([self.view_prefix, self.action])
                    self.action = new_action
        return super(View, self).evaluate()

class Redirect(URLBase):
    def evaluate(self):
        from django.views.generic.simple import redirect_to
        if isinstance(self.action, basestring):
            redirect_url = self.action
            self.action = redirect_to
            self._kwargs = dict(url=redirect_url)
        return super(Redirect, self).evaluate()

class ReverseRedirect(URLBase):
    def evaluate(self):
        from django.core.urlresolvers import reverse_lazy
        from django.views.generic.simple import redirect_to
        if isinstance(self.action, basestring):
            redirect_url_name = self.action
            reverse_kw = dict()
            self.action = redirect_to
            if self.app_name:
                reverse_kw.update({ 'current_app': self.app_name, })
            if len(self._kwargs) > 0:
                reverse_kw.update({ 'kwargs': self._kwargs, })
            elif len(self._args) > 0:
                reverse_kw.update({ 'args': self._args, })
            self._kwargs = dict(url=reverse_lazy(redirect_url_name, **reverse_kw))
        return super(ReverseRedirect, self).evaluate()

class KeywordReverseRedirect(ReverseRedirect):
    def __init__(self, url_pattern, action, *args, **kwargs):
        import re
        kwre = re.compile(url_pattern)
        if kwre.groups > 0:
            for kw in kwre.groupindex.keys():
                if isinstance(kw, basestring):
                    kwargs.update({ kw: "%%(%s)s" % kw })
        super(KeywordReverseRedirect, self).__init__(url_pattern, action, *args, **kwargs)

class NamespaceOptions(object):
    def __init__(self, meta):
        self.options = {}
        self.options['view_prefix'] = getattr(meta, 'view_prefix', '')
        self.options['namespace'] = getattr(meta, 'namespace', '')
        self.options['app_name'] = getattr(meta, 'app_name', '')
    
    def namespaced_name(self, name):
        if name.startswith(self.options['namespace'].lower()):
            return name
        return "%s:%s" % (self.options['namespace'].lower(), name.lower())
    
    def contribute_to_class(self, cls, name):
        cls._meta = self
        self.names = {}
        self.urls = []

class Namespacer(type):
    
    def __new__(cls, name, bases, attrs):
        super_new = super(Namespacer, cls).__new__
        parents = [b for b in bases if isinstance(b, Namespacer)]
        if not parents:
            return super_new(cls, name, bases, attrs)
        
        # Create the class.
        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, { '__module__': module })
        attr_meta = attrs.pop('Meta', None)
        if attr_meta:
            meta = attr_meta
        else:
            attr_meta = type('Meta', (object,), {})
            meta = getattr(new_class, 'Meta', None)
        
        #namespace = getattr(meta, 'namespace', getattr(meta, 'app_name', None))
        
        new_class.add_to_class('_meta', NamespaceOptions(meta))
        new_class.add_to_class('Meta', attr_meta)
        
        for parent in parents[::-1]:
            if hasattr(parent, '_meta'):
                new_class._meta.names.update(parent._meta.names)
                #new_class._meta.urls.update(parent._meta.urls)
        
        for name, value in filter(lambda nv: isinstance(nv[1], ArgumentSink), attrs.items()):
            #name = value.name
            namespaced_name = new_class._meta.namespaced_name(name)
            new_class.add_to_class(name, value)
            new_class._meta.names[name] = namespaced_name
            new_class._meta.urls.append(
                (name, attrs.pop(name)),
            )
        
        # sort by creation_counter
        new_class._meta.urls.sort(key=lambda item: item[1].creation_counter)
        
        # Add all attributes to the class.
        for name, value in attrs.items():
            new_class.add_to_class(name, value)
        
        return new_class
    
    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

class Namespace(ArgumentSink):
    __metaclass__ = Namespacer
    
    def __init__(self, **kwargs):
        pass
    
    @property
    def ordered_urls(self):
        return [getattr(self, uu[0]) for uu in self._meta.urls]
    
    @property
    def ordered_names(self):
        return [uu[0] for uu in self._meta.urls]
    
    def __dir__(self):
        return self.ordered_names
    
    @property
    def __members__(self):
        return self.__dir__()
    
    def evaluate(self):
        from django.conf.urls.defaults import patterns
        view_prefix = self._meta.options.get('view_prefix', '')
        urls_out = []
        for url_out in self.ordered_urls:
            urls_out.append(url_out.evaluate())
        '''
        return (
            patterns(view_prefix, *urls_out),
            self._meta.options.get('app_name'),
            self._meta.options.get('namespace'))
        '''
        return patterns(view_prefix, *urls_out)



if __name__ == "__main__":

    class MyURLs(Namespace):
    
        class Meta:
            namespace = 'blog' # optional
            app_name = 'blog' # optional
            view_prefix = 'ost2.twemoir' # optional
    
        grafs_option = View(
            r'^grafs/(?P<option>[\w\-]+)/?$',
                'views.paragraphs')
    
        grafs_option_args = View(
            r'^grafs/(?P<option>[\w\-]+)/?$',
                'views.paragraphs',
                arg='yo', other_arg='dogg')
    
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
    
    ns = MyURLs()
    out = ns.evaluate()
    
    from pprint import pprint
    pprint(out)

