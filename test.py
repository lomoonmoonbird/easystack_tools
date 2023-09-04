class Test():
    def __call__(self, *args, **kwargs):
        print(11111)

    def __init__(self, a):
        print(22222)

Test(11)()

def de1(fn):
    # def wrapper():
    def inner(*args, **kwargs):
        print(1)
        fn(*args, **kwargs)
    return inner
    # return wrapper

def de2(fn):
    # def wrapper():
    def inner(*args, **kwargs):
        print(2)
        fn(*args, **kwargs)
    return inner
    # return wrapper
@de2
@de1
def hello():
    print('hello')

hello()