import threading
import time, random

# the baton, a mutex to make changing states atomic
# TODO maybe need to make these global
baton = threading.Semaphore(1)
n = 5 # number of philosophers
eating = [False for i in range(n)]
waiting = [False for i in range(n)]
philSem = [threading.Semaphore(0) for i in range(n)]
Philosophers = []


class Philosopher(threading.Thread):
    def __init__(self, i):
        threading.Thread.__init__(self)
        self.i = i # index of philosopher in larger array
        
    def get_forks(self):
        baton.acquire()
        waiting[self.i] = True
        check(self.i)
        baton.release()
        philSem[self.i].acquire()
        print "Philosopher "+str(self.i)+" is getting forks."

    def put_forks(self):
        baton.acquire()
        waiting[self.i] = False
        eating[self.i] = False
        check((self.i+1)%n)
        check((self.i-1)%n)
        print "Philosopher "+str(self.i)+" is releasing forks."
        baton.release()
        
    def eat(self):
        print "Philosopher "+str(self.i)+" is eating."
        time.sleep(random.randint(3,7))
        
    def think(self):
        time.sleep(random.randint(3,8))
            
    # main execution loop
    def run(self):
        t = 5
        i = 0
        while i < t:
            self.think()
            self.get_forks()
            self.eat()
            # assert global invariant after eating
            # before releasing forks ensure that no one next to you is eating
            assert eating[(self.i+1)%n] == False, "Fatal error in fork use."
            self.put_forks()
            i = i + 1
        print "Philosopher "+str(self.i)+" is finished."
        
def check(i):
    if waiting[i] and not eating[(i+1)%n] and not eating[(i-1)%n]:
        eating[i] = True
        philSem[i].release()

def main():
    # create threads
    for i in range(0,n):
        Philosophers.append(Philosopher(i))
        
    # begin threads
    for i in range(0,n):
        Philosophers[i].start()
        
    print "Main is done."
    
if __name__ == "__main__":
    main()
        
