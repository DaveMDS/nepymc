
from nepymc.utils import EmcObject


class Parent(EmcObject):
    def __init__(self):
        super().__init__()

    def delete(self):
        super().delete()


class Child(EmcObject):
    def __init__(self, parent):
        super().__init__(parent)

    def delete(self):
        super().delete()


callbacks_counter = 0


def on_delete_cb(o):
    global callbacks_counter
    callbacks_counter += 1

    assert type(o) is Child
    assert type(o.parent) is Parent


def on_delete_cb_with_args(o, k1, k2):
    global callbacks_counter
    callbacks_counter += 1

    assert type(o) is Child
    assert type(o.parent) is Parent
    assert k1 == 'k1'
    assert k2 == 'k2'


def test_object():

    p = Parent()
    assert type(p) == Parent
    assert len(p.children) == 0

    # a "normal" child, will be automatically deleted with parent
    c1 = Child(parent=p)
    c1.on_delete(on_delete_cb)
    c1.on_delete(on_delete_cb_with_args, k1='k1', k2='k2')
    assert type(c1) == Child
    assert c1.parent is p
    assert len(p.children) == 1
    assert c1 in p.children

    # this child will be deleted manually before the parent
    c2 = Child(parent=p)
    c2.on_delete(on_delete_cb)
    assert type(c2) == Child
    assert c2.parent is p
    assert len(p.children) == 2
    assert c2 in p.children

    # a child without a ref
    tmp = Child(parent=p)
    tmp.on_delete(on_delete_cb)
    del tmp  # remove our ref, obj should still stay alive
    assert len(p.children) == 3

    # manually delete c2
    c2.delete()
    assert c2.deleted is True
    assert len(p.children) == 2
    assert c2 not in p.children
    del c2

    # delete the parent, that will delete remaining childs (c1 and tmp)
    p.delete()
    assert p.deleted is True
    assert len(p.children) == 0
    assert c1.deleted is True

    # make sure all the del callback has been called
    assert callbacks_counter == 4
