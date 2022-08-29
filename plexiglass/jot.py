import json


def resolve(obj):
    """
    Make a clean non-referential copy of the original object.
    """
    if isinstance(obj, dict):
        return {k: v for k, v in obj.items()}
    elif type(obj).__name__ == "Jot":
        return obj()
    elif isinstance(obj, list):
        return [resolve(x) for x in obj]
    else:
        return obj


# https://stackoverflow.com/questions/20656135/python-deep-merge-dictionary-data
def merge(source, destination, auto=True):
    """
    run me with nosetests --with-doctest file.py

    >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True
    """
    for key, value in source.items():
        if auto and isinstance(value, dict):
            # get node or create one
            # all nested dictionaries are turned into Jots.
            node = destination.setdefault(key, eval("Jot()"))
            merge(resolve(value), node, auto=auto)
        elif type(value).__name__ == "Jot":
            # get node or create one
            node = destination.setdefault(key, type(value)())
            merge(resolve(value), node, auto=auto)
        elif isinstance(value, list):
            # copy the list, making sure to resolve any nested Jots
            destination[key] = resolve(value)
        else:
            destination[key] = resolve(value)

    return destination


def unpack(o):
    if isinstance(o, Jot):
        return {k: unpack(v) for k, v in o.__dict__.items()}
    elif isinstance(o, dict):
        return {k: unpack(v) for k, v in o.items()}
    # XXX: Support arbitrary iterables? Out of scope for now with simple json.
    elif isinstance(o, (tuple, list)):
        return [unpack(v) for v in o]
    return o


class Jot:
    __slots__ = ["_prefix_", "_auto_", "__dict__"]

    def __init__(self, data=None, auto=True, prefix=None):
        self.__dict__ = dict()
        self._auto_ = auto
        self._prefix_ = prefix or ""
        if prefix and data:
            raise ValueError("Jots must be assigned a prefix before loading data")
        if data:
            self.merge(data)

    def merge(self, other):
        if isinstance(other, str):
            merge(json.loads(other), self.__dict__, auto=self._auto_)
        if isinstance(other, dict):
            merge(other, self.__dict__, auto=self._auto_)
        elif isinstance(other, Jot):
            merge(other.__dict__, self.__dict__, auto=self._auto_)

    def __bool__(self):
        return bool(self.__dict__)

    def __contains__(self, key):
        """Necessary as proxying __contains__ to the underlying __dict__ recurses infinitely."""
        return key in self.__dict__

    def __getattr__(self, name, *args, **kwargs):
        # Attempt to get the raw attribute on the Jot object.
        try:
            return super().__getattribute__(name)
        except AttributeError:
            pass

        # Attempt to get the raw attribute on the Jot's dictionary.
        try:
            return self.__dict__.__getattribute__(name)
        except AttributeError:
            # If _auto_ is not set, do not dynamically create a new attribute.
            if not self._auto_:
                raise

        # Force creation of a new attribute if it does not exist.
        result = Jot()
        setattr(self, name, result)
        return result

    def __setattr__(self, name, value):
        if name not in self.__slots__:
            name = "".join((self._prefix_, name))
            # If _auto_ is not set, do not automatically coerce nested dicts.
            if self._auto_ and type(value) == dict:
                value = Jot(value)
        super().__setattr__(name, value)

    def __getitem__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            # If _auto_ is not set, do not dynamically add new keys.
            if not self._auto_:
                raise

        # Force creation of a new key-value pair if it does not exist.
        result = Jot()
        self.__dict__[key] = result
        return result

    def __setitem__(self, key, value):
        if type(value) == dict:
            value = Jot(value)
        self.__dict__[key] = value

    def __repr__(self):
        return json.dumps(unpack(self))

    def __call__(self, other={}):
        new_jot = Jot(auto=self._auto_)
        new_jot.merge(self)
        new_jot.merge(other)
        return new_jot
