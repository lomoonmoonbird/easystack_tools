class Stack(object):

    def __init__(self,data=None):
     # 创建空列表实现栈
        if data:
            self.__list = data
        else:
            self.__list = []

    def is_empty(self):
    # 判断是否为空
        return self.__list == []
    def push(self,item):
    # 压栈，添加元素
        self.__list.append(item)

    def pop(self):
    # 弹栈，弹出最后压入栈的元素
        if self.is_empty():
            return
        else:
            return self.__list.pop()

    def top(self):
    # 取最后压入栈的元素
        if self.is_empty():
            return
        else:
            return self.__list[-1]

    def get_all(self):
        return self.__list