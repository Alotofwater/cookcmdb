# from django.test import TestCase
#
# # Create your tests here.
#
#
# from types import MethodType, FunctionType





def wrapper_detete_view_flag(timeout=0):
    def decorator(func):
        def wrapper(request,*args, **kwargs):
            import time
            start = time.time()
            ret = func(request,*args, **kwargs)
            stop = time.time()
            print('run time is %s ' % (stop - start))
            print(timeout)
            return ret
        return wrapper
    return decorator

# @wrapper_detete_view_flag(2)

def timer(func):
    def inner(request,*args, **kwargs):
        print('简单版本装饰器', 222222222222 + 2213123123)
        start = 999999
        func(request,*args, **kwargs)
        print('简单版本装饰器', 222222222222 - start)
    return inner



def newfunc(request):
    print('aaaaaa/ %s' %(request))


newfunc1 = wrapper_detete_view_flag(timeout='2')

newfunc1 = newfunc1(newfunc)

ssss = timer(newfunc1)
ssss(request='request')



