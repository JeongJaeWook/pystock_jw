import platform
#print(platform.architecture()) #('32bit', 'WindowsPE')

def math():
    name = "재욱"
    return name

who = math()
#print(who)


def multi():
    return "a","b"

b,a = multi()
# print(a) #b
returlt = multi()
# print(returlt)

class B_school():
    def __init__(self):
        self.school_name = "b학교"


class A_school():
    def __init__(self):
        print("초기화")
        self.student1_name = None
        self.student2_name = None

        b = self.math()
        print("수학과 학생 %s" % b)

        b_school = B_school()
        print(b_school.school_name)

    def math(self):
        self.student1_name = "영수"
        name = self.student1_name

        return name


        #print(dir(self))
A_school()

