import threading

# the baton, a mutex to make changing states atomic
# TODO maybe need to make these global
baton = threading.Semaphore(1)
n = 5 # number of philosophers
eating = [False for i in range(n)]
waiting = [False for i in range(n)]
philSem = [threading.Semaphore(0) for i in range(n)]

class Philosopher(threading.Thread):
    def __init__(self, i):
        threading.Thread.__init__(self)
        self.i = i # index of philosopher in larger array
        
    def get_forks(self):
        baton.acquire()
        waiting[self.index] = True
        check(self.i)
        baton.release()
        philSem[self.i].acquire()

    def put_forks(self):
        baton.acquire()
        waiting[self.i] = False
        eating[self.i] = False
        check((self.i+1)%n)
        check((self.i-1)%n)
        baton.release()
        
def check(i):
    if waiting[i] and not eating[(i+1)%n] and not eating[(i-1)%n]:
        eating[i] = True
        philSem[i].release()

def main():
    print "main"
    
if __name__ == "__main__":
    main()
    
