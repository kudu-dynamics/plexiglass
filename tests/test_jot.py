from collections import Counter, defaultdict
import json

import pytest

from plexiglass.jot import Jot


def test_jot_basic():
    j = Jot()
    j.apple.x = 20

    k = {"apple": {"x": 20}}
    assert str(j) == json.dumps(k)

    k["apple"]["y"] = [1, 2, 3]
    j.apple.y = [1, 2, 3]
    assert str(j) == json.dumps(k)

    j.apple.z = {}
    j.apple.z.test = "Hello!"
    k["apple"]["z"] = {"test": "Hello!"}
    assert str(j) == json.dumps(k)


def test_jot_merge():
    j_1 = Jot({"a": 10})
    j_2 = Jot({"a": 20})
    d_1 = {"a": 20}
    assert str(j_1(j_2)) == json.dumps(d_1)

    j_3 = Jot({"b": {"c": "Hi"}})
    d_1["b"] = {"c": "Hi"}
    assert str(j_1(j_2)(j_3)) == json.dumps(d_1)

    j_4 = Jot("""{"a": 10}""")
    d_2 = {"a": 10}
    assert str(j_4) == json.dumps(d_2)


def test_jot_getitem():
    j_5 = Jot()
    j_5["a"]
    j_5["a"] = 10
    d_2 = {"a": 10}
    assert str(j_5) == json.dumps(d_2)

    j_5["b"] = {"a": 2}
    j_5["b"]["c"] = 12
    d_2["b"] = {"a": 2, "c": 12}
    assert str(j_5) == json.dumps(d_2)


def test_jot_main():
    a = Jot()
    a.example = 10
    a.nested.example = 20
    a["nest-ed"].example = 30
    a.array = [1, 2, Jot()]
    a.assign_now = {}
    a.assign_now.test = "WHOA!"
    a["assign-now"] = {}
    a["assign-now"].test = "WHOA AGAIN!"
    b = Jot(a)
    b = Jot(str(a))
    b = Jot(str(b))
    d = {
        "example": 10,
        "nested": {"example": 20},
        "nest-ed": {"example": 30},
        "array": [1, 2, {}],
        "assign_now": {"test": "WHOA!"},
        "assign-now": {"test": "WHOA AGAIN!"},
    }
    assert str(b) == json.dumps(d)


def test_jot_prefix():
    a = Jot(prefix="test.")
    a.example = 1
    assert str(a) == json.dumps({"test.example": 1})

    with pytest.raises(ValueError):
        b = Jot(data={"hi": 1}, prefix="happy.")
        assert str(b) == json.dumps({"happy.hi": 1})


def test_jot_contains():
    a = Jot()
    assert "nonexistent-key" not in a
    a.hi = 1
    assert "hi" in a


def test_jot_dict_proxy():
    """
    Dict methods should be proxied to the underlying __dict__ in the Jot object.
    """
    a = Jot({"hi": 1})
    assert "hi" in a
    a.clear()
    assert "hi" not in a
    assert not a


def test_jot_pop():
    """
    Make sure removal of keys is possible from Jot objects.
    """
    a = Jot({"hi": 1, "helper": 2})
    a.pop("hi")
    del a.helper
    assert not a


def test_jot_copy():
    """
    Make sure instantiating a Jot creates a new one.
    """
    a = Jot({"hello": "world"})
    b = a()
    b.hello = "town"
    c = a({"hello": "galaxy"})
    assert a.hello != "galaxy"
    assert b.hello == "town"
    assert c.hello == "galaxy"


def test_jot_copy_list():
    """
    Test copy semantics for reference data types.
    """
    a = Jot({"test": []})

    b = a()
    b.test.append("HI")

    c = a()
    assert len(c.test) == 0


def test_jot_copy_complex():
    """
    Test to make sure that calling a Jot object creates a good copy.
    """
    a = Jot({"test": Jot({"inner": [Jot({"a": 10})]})})

    print("CREATE B")
    b = a()
    b.test.inner[0].a = 20
    assert a.test.inner[0].a == 10
    print(id(a.test))
    print(id(b.test))
    print(id(a.test.inner))
    print(id(b.test.inner))

    print("CREATE C")
    c = a()
    print(c)
    print(c.test)
    print(c.test.inner)
    assert len(c.test.inner) == 1
    assert c.test.inner[0].a == 10


def test_jot_auto():
    """
    Test to make sure that Jots can be created in a non-automatic default-adding mode.
    """
    a = Jot({"test": 10}, auto=False)
    assert "test" in a
    assert "nope" not in a
    assert a.test == 10
    assert a["test"] == 10
    assert getattr(a, "b", 20) == 20
    assert a.get("b", 20) == 20
    with pytest.raises(AttributeError):
        a.b
    with pytest.raises(KeyError):
        a["b"]


def test_jot_dict_subclass():
    """
    Test to make sure that Jots don't override values that are dict subclasses
    with a Jot.
    """
    a = Jot()
    a.b = Counter()
    a.c = defaultdict(list)
    assert type(a.b) == Counter
    assert type(a.c) == defaultdict
