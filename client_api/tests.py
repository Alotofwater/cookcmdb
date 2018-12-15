from django.test import TestCase

# Create your tests here.


from types import MethodType, FunctionType



class Mxd(object):
    dd1 = 'wo shi dd1'
    @classmethod
    def func1(cls,c1):
        print("func1",c1)
        cls.dd1 = cls.dd1 + 'func1'
        print("func1",)
        # pass

    def func2(self):
        print("func2",self.dd1)
        # pass
    @staticmethod
    def func3(self):
        print("func3",self.dd1)

    @staticmethod
    def func4(self,c):
        print(c)
        print(self.dd1)

Mxd.func1("sdd")
Mxd.func2(Mxd)
Mxd.func3(Mxd)

# def check(arg):
#     """
# 	判断arg是函数则打印1，arg是方法则打印2
# 	:param arg:
# 	:return:
# 	"""
#     if isinstance(arg, MethodType):  # MethodType方法
#         print(2, "方法")
#     elif isinstance(arg, FunctionType):  # FunctionType函数
#         print(1, "函数")
#     else:
#         print('不认识')
#
# check(Mxd.func3)
#
# Mxd.func4()

# import copy
#
#
# class Mxd(object):
#     def __init__(self):
#         self.mm = ["d",[1,'c',[],]]
#
#     def func1(self,ch1):
#         self.mm[1].append(ch1)
#         self.mm[1][2].append(ch1)
#
#
# s = Mxd()
# s.func1("cf11")
# # c = copy.deepcopy(s)
# c = s
# c.func1("mdmsd")
# print(s.mm)
# print(c.mm)

#
# import re
# #ret变成了一个对象
# ret = re.search('yu', 'eva egon yuan')
# print(ret.group())