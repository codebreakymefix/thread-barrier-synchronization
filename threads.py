import threading
import random

#Basically all the global variables used in the code, this code should be scalable meaning you can easily add more thread
basetemp = 10
numofthreads = 4
centraltemp = basetemp
externaltemp = []
threshold = 0.3

for i in range(numofthreads):
    externaltemp.append(random.randint(basetemp, basetemp + 50))
otherthread = []
stabilized = False
condition = threading.Condition()
print(externaltemp)
counter = 0

def externaltempthread(index):
    #Needed so the data is shared between threads
    global externaltemp, stabilized,condition, counter, centraltemp
    #Keeps the thread running because if the function ends it ends the thread should stop running
    while stabilized != True:
        #Basically helps synchronize with the counter. It makes sure that the external temps all of them run and then the central temp.
        with condition:
            #Will exit condition if stabalized changed in between the while and with statements.
            if stabilized:
                break
            counter = counter + 1
            print(f"Counter: {counter}")
            #Halts until central value is updated
            condition.wait()
            #Saves each temp of a thread into an array.
            externaltemp[index] = (3*externaltemp[index] + 2*centraltemp)/5
            print(f"Index: {index} \nExternal Temp: {externaltemp[index]}\n")

    print(f"Final Central Stabalized Temperature: {centraltemp}\n")


def centraltempthread():
    global centraltemp,stabilized,condition,counter, externaltemp
    while stabilized != True:
        with condition:
            #Is all other threads are waiting this runs and resets the counter
            if counter == numofthreads:
                centraltemp = (2*centraltemp+sum(externaltemp))/(2 + numofthreads)
                print(f"Central Temperature: {centraltemp}\n")
                counter = 0
                #"opens the flood" gates meaning tells all the threads waiting to run at the same time.
                #It should not matter since they are all updating their individual temperatures
                #Control temp is only the critical section of this code.
                condition.notify_all()
            #Ends the code if externaltemps are within a threshold of the central temp
            if (abs(min(externaltemp)-centraltemp) < threshold) and (abs(max(externaltemp)-centraltemp) < threshold):
                stabilized = True
                #needed to end threads that were waiting
                condition.notify_all()
    print(f"Final Central Stabalized Temperature: {centraltemp}")

#Threading notation from python library
mainthread = threading.Thread(target = centraltempthread)
mainthread.start()

for i in range(numofthreads):
    thread = threading.Thread(target = externaltempthread, args= (i,))
    otherthread.append(thread)
    thread.start()