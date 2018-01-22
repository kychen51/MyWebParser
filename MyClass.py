__author__ = 'kenneche'


class MyClass:

    def __init__(self):
        self.a = 1
        self.b = 2

    def main(self):
        print("a = {0}, b = {1}".format(self.a, self.b))

    def indexList(self, myList):
        try:
            if myList.index('4') == None:
                print("4 == None")
            else:
                print("??")
        except ValueError:
            print("ValueError")

if __name__ == '__main__':
    m = MyClass()
#    m.main()
    myList = [1, 2, 3]
    m.indexList(myList)

