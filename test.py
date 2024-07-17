def something(a,b):
    print(a*b)



def main_func(a,func):
    for i in a:
        func(i,2)

a=[1,2,3,4,6]

main_func(a,something)