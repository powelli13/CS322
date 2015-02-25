# Isaac Powell made for Geoffrey Matthew's csci322
# implementation of a starving solution to the 
# dining philosophers problem.
# credit should be given to Tanenbaum as much
# of this is based of off his solution to the problem
# as found in The Little Book of Semaphores

import threading, Queue
import time, random

# a mutex to make changing states atomic
mutex = threading.Semaphore(1)
n = 5 # number of philosophers
# boolean arrays to record states
eating = [False for i in range(n)]
waiting = [False for i in range(n)]
# semaphores for a philosopher to wait on
philSem = [threading.Semaphore(0) for i in range(n)]
Philosophers = []
pq = Queue.Queue()

class Philosopher(threading.Thread):
    def __init__(self, i):
        threading.Thread.__init__(self)
        self.i = i # index of philosopher in larger array
        
    def get_forks(self):
        mutex.acquire()
        waiting[self.i] = True
        pq.put(self.i)
        if pq.qsize() > 0:
            t = pq.get()
            check(t)
        mutex.release()
        philSem[self.i].acquire()
        print "Philosopher "+str(self.i)+" is getting forks."

    def put_forks(self):
        mutex.acquire()
        waiting[self.i] = False
        eating[self.i] = False
        if pq.qsize() > 0:
            t = pq.get()
            check(t)
        else:
            check((self.i+1)%n)
            check((self.i-1)%n)
            
        print "Philosopher "+str(self.i)+" is releasing forks."
        mutex.release()
        
    def eat(self):
        print "Philosopher "+str(self.i)+" is eating."
        time.sleep(random.randint(3,8))
        
    def think(self):
        time.sleep(random.randint(3,8))
            
    # main execution loop
    def run(self):
        # philosophers only eat a select amount of times
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
        
    print "Main is done. Philosophers threads running."
    
if __name__ == "__main__":
    main()
        
