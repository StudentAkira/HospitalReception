def outer(func):
    def inner(role):
        print("Befor func ")
        func()
        print(f"Role ::{role}")
        print("After func ")
    return inner


@outer
def hi():
    print('hi')


hi('role')
