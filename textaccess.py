ids = set()

def access_init():
    f = open('allowed.txt', 'r')
    for line in f:
        ids.add(int(line))
    f.close()

def is_cleared(number):
    return number in ids
