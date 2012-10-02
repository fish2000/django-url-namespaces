
import re
import sys
import types
from pprint import pprint

from django.conf.urls import url
from django.conf.urls import patterns
from django.conf.urls import include as django_include
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic.simple import redirect_to
from django.utils.importlib import import_module
from django.utils.functional import memoize

CACHE = {}

class memo(object):
    def __init__(self, cache, num_args=2):
        self.cache = cache
        self.num_args = num_args
    def __call__(self, f):
        return memoize(f, self.cache, self.num_args)

class ClassIncludeError(Exception):
    pass

def modulize(ns):
    ns_modname = "__url_namespaces__.%s" % ns.namespace.replace(':', '_')
    ns_module = types.ModuleType(ns_modname, "Dynamic URLConf Module")
    ns_module.__dict__.update({
        'urlpatterns': ns._evaluate(), })
    print "ns_modname = %s" % ns_modname
    sys.modules.update({
        ns_modname: ns_module, })
    return ns_module

def include_class(path):
    path_bits = path.split('.') # Cut off the class name at the end.
    class_name = path_bits.pop()
    module_path = '.'.join(path_bits)
    module_itself = import_module(module_path)
    if not hasattr(module_itself, class_name):
        raise ClassIncludeError(
            "The Python module '%s' has no '%s' class." % (module_path, class_name))
    return getattr(module_itself, class_name)

def include(arg, namespace=None, app_name=None):
    mod = None
    if isinstance(arg, basestring):
        try:
            ns = include_class(arg)()
        except ClassIncludeError:
            mod, include_namespace, include_app_name = django_include(
                arg, namespace=namespace, app_name=app_name)
        else:
            mod = modulize(ns)
    elif isinstance(arg, types.ModuleType):
        if arg.__name__ not in sys.modules:
            sys.modules.update({ arg.__name__: arg, })
        mod = arg
    elif isinstance(arg, Namespace):
        mod = modulize(arg)
    elif isinstance(arg, types.ClassType):
        mod = modulize(arg())
    return (mod, namespace, app_name)


class ArgumentSink(object):
    creation_counter = 0
    
    def __init__(self, *args, **kwargs):
        self.creation_counter = ArgumentSink.creation_counter
        ArgumentSink.creation_counter += 1
        self._args = args
        self._kwargs = kwargs
        self._options = {}
    
    def contribute_to_class(self, cls, name):
        self.name = name
        setattr(cls, name, self)
        if hasattr(cls, '_meta'):
            if hasattr(cls._meta, 'options'):
                self.process(name=name, **cls._meta.options)
    
    def process(self, **options):
        if hasattr(self, '_options'):
            self._options.update(options)
    
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
        return url(
            self.url_pattern, self.action, self._kwargs,
            name=self.name)


class View(URLBase):
    #@memo(CACHE)
    def ____evaluate(self):
        if isinstance(self.action, basestring):
            if isinstance(self._options.get('view_prefix'), basestring):
                if len(self._options.get('view_prefix')) > 0:
                    new_action = ".".join([self._options.get('view_prefix'), self.action])
                    self.action = new_action
        return super(View, self).evaluate()


class Redirect(URLBase):
    #@memo(CACHE)
    def evaluate(self):
        if isinstance(self.action, basestring):
            redirect_url = self.action
            self.action = redirect_to
            self._kwargs = dict(url=redirect_url)
        return super(Redirect, self).evaluate()


class ReverseRedirect(URLBase):
    #@memo(CACHE)
    def evaluate(self):
        if isinstance(self.action, basestring):
            redirect_url_name = self.action
            reverse_kw = dict()
            self.action = redirect_to
            if self._options.get('app_name'):
                reverse_kw.update({ 'current_app': self._options.get('app_name'), })
            if len(self._kwargs) > 0:
                reverse_kw.update({ 'kwargs': self._kwargs, })
            elif len(self._args) > 0:
                reverse_kw.update({ 'args': self._args, })
            self._kwargs = dict(url=reverse_lazy(redirect_url_name, **reverse_kw))
        return super(ReverseRedirect, self).evaluate()


class KeywordReverseRedirect(ReverseRedirect):
    def __init__(self, url_pattern, action, *args, **kwargs):
        kwre = re.compile(url_pattern)
        if kwre.groups > 0:
            for kw in kwre.groupindex.keys():
                kwargs.update({ kw: "%%(%s)s" % kw })
        super(KeywordReverseRedirect, self).__init__(url_pattern, action, *args, **kwargs)


class NamespaceOptions(object):
    def __init__(self, meta):
        self.view_prefix = getattr(meta, 'view_prefix', '')
        self.namespace = getattr(meta, 'namespace', '')
        self.app_name = getattr(meta, 'app_name', '')
    
    @property
    def options(self):
        return dict(
            view_prefix=self.view_prefix,
            namespace=self.namespace,
            app_name=self.app_name)
    
    def namespaced_name(self, name):
        if name.startswith(self.namespace.lower()):
            return name
        return "%s:%s" % (self.namespace.lower(), name.lower())
    
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
        new_class = super_new(cls, name, bases, { '__module__': module, })
        attr_meta = attrs.pop('Meta', None)
        if attr_meta:
            meta = attr_meta
        else:
            attr_meta = type('Meta', (object,), {})
            meta = getattr(new_class, 'Meta', None)
        
        new_class.add_to_class('_meta', NamespaceOptions(meta))
        new_class.add_to_class('Meta', attr_meta)
        
        for name, value in filter(lambda nv: isinstance(nv[1], ArgumentSink), attrs.items()):
            namespaced_name = new_class._meta.namespaced_name(name)
            new_class.add_to_class(name, value)
            new_class._meta.names[name] = namespaced_name
            new_class._meta.urls.append(
                (name, attrs.pop(name)),)
        
        # sort by creation_counter
        new_class._meta.urls.sort(
            key=lambda item: item[1].creation_counter)
        
        # Add all attributes to the class.
        for name, value in attrs.items():
            new_class.add_to_class(name, value)
        
        return new_class
    
    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class Namespace(URLBase):
    __metaclass__ = Namespacer
    
    def __init__(self, url_pattern):
        super(Namespace, self).__init__(url_pattern, action=None)
    
    def process(self, **options):
        #if self.namespace and options.get('namespace', ''):
        if self.namespace:
            #parent_namespace = options.get('namespace', '')
            options.update({
                'namespace': self.namespace, })
            #options.update({
            #    'namespace': "%s:%s" % (
            #        parent_namespace, self.namespace), })
        if self.view_prefix and options.get('view_prefix', ''):
            parent_view_prefix = options.get('view_prefix', '')
            options.update({
                'view_prefix': "%s.%s" % (
                    parent_view_prefix, self.view_prefix), })
        self._meta.__dict__.update(options)
        super(Namespace, self).process(**options)
    
    @property
    #@memo(CACHE)
    def ordered_urls(self):
        return (getattr(self, uu[0]) for uu in self._meta.urls)
    
    @property
    #@memo(CACHE)
    def ordered_names(self):
        return (uu[0] for uu in self._meta.urls)
    
    @property
    def view_prefix(self):
        return getattr(self._meta, 'view_prefix',
            self._options.get('view_prefix', ''))
    @property
    def app_name(self):
        return getattr(self._meta, 'app_name',
            self._options.get('app_name', ''))
    @property
    def namespace(self):
        return getattr(self._meta, 'namespace',
            self._options.get('namespace', "dyn_ns_%s" % hash(self)))
    
    def _evaluate(self):
        urls_out = []
        for url_out in self.ordered_urls:
            urls_out.append(url_out.evaluate())
        return patterns(self.view_prefix, *urls_out)

    def evaluate(self):
        pprint(self.__dict__)
        #return url(self.url_pattern, (modulize(self), self._meta.namespace, self._meta.app_name), kwargs=self._kwargs)
        return url(self.url_pattern, (modulize(self), self._meta.namespace, self._meta.app_name), kwargs=self._kwargs)
    
    def connect(self, name):
        cls = self.__class__
        if hasattr(cls, '_meta'):
            if hasattr(cls._meta, 'options'):
                self.process(name=name, **cls._meta.options)
        return self.evaluate()
    
    def __dir__(self):
        return self.ordered_names
    
    @property
    def __members__(self):
        return self.__dir__()

