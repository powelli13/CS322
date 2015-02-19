import threading


class Philosopher(threading.Thread):
    def __init__(self, i):
        threading.Thread.__init__(self)
        self.index = i
    

def main():
    print "main"
    
if __name__ == "__main__":
    main()
    
