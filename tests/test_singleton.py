
from nepymc.utils import Singleton, EmcObject


class Single(metaclass=Singleton):
    instances_count = 0

    def __init__(self, arg1, arg2, karg1=None):
        self.arg1 = arg1
        self.arg2 = arg2
        self.karg1 = karg1
        self.instances_count += 1
        assert self.instances_count == 1


class SingleEmcObject(EmcObject, metaclass=Singleton):
    instances_count = 0

    def __init__(self, arg1, arg2, karg1=None):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2
        self.karg1 = karg1
        self.instances_count += 1
        assert self.instances_count == 1

    def delete(self):
        super().delete()


def test_singleton():
    # build the first (and only) instance
    s1 = Single('a1', 'a2', karg1='k1')
    assert type(s1) is Single
    assert s1.arg1 == 'a1'
    assert s1.arg2 == 'a2'
    assert s1.karg1 == 'k1'

    # get the instance using normal class call method. Params are ignored!
    s2 = Single(1, 2, karg1=3)
    assert type(s2) is Single
    assert s2.arg1 == 'a1'
    assert s2.arg2 == 'a2'
    assert s2.karg1 == 'k1'
    assert s2 is s1

    # get the instance using normal class call method. without params
    s3 = Single()
    assert type(s3) is Single
    assert s3.arg1 == 'a1'
    assert s3.arg2 == 'a2'
    assert s3.karg1 == 'k1'
    assert s3 is s1

    # get the instance using the instance() class method
    s4 = Single.instance()
    assert type(s4) is Single
    assert s4.arg1 == 'a1'
    assert s4.arg2 == 'a2'
    assert s4.karg1 == 'k1'
    assert s4 is s1


def test_singleton_object():
    # build the first (and only) instance
    s1 = SingleEmcObject('a1', 'a2', karg1='k1')
    assert type(s1) is SingleEmcObject
    assert s1.arg1 == 'a1'
    assert s1.arg2 == 'a2'
    assert s1.karg1 == 'k1'

    # get the instance using normal class call method. Params are ignored!
    s2 = SingleEmcObject(1, 2, karg1=3)
    assert type(s2) is SingleEmcObject
    assert s2.arg1 == 'a1'
    assert s2.arg2 == 'a2'
    assert s2.karg1 == 'k1'
    assert s2 is s1

    # get the instance using normal class call method. without params
    s3 = SingleEmcObject()
    assert type(s3) is SingleEmcObject
    assert s3.arg1 == 'a1'
    assert s3.arg2 == 'a2'
    assert s3.karg1 == 'k1'
    assert s3 is s1

    # get the instance using the instance() class method
    s4 = SingleEmcObject.instance()
    assert type(s4) is SingleEmcObject
    assert s4.arg1 == 'a1'
    assert s4.arg2 == 'a2'
    assert s4.karg1 == 'k1'
    assert s4 is s1

    s1.delete()
