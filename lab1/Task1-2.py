import random
import simpy
import math
from impl.MMmLimitBuffer import MMm_sys
import matplotlib.pyplot as plt

mmm_config = {
    "SERVICE": 10.0,
    "ARRIVAL": 10.0/0.85,
    "TYPE1": 1,
    "SIM_TIME": 500000,
    "QUEUESIZE": 0,
    "SERNUM": 2
}

# Compare with infinite buffer size
measures = []
buffer_size =[]
for i in range(20):
    buffer_size.append((i+1)*2)


it = 0
for buffer in buffer_size:
    it +=1
    mmm_config["QUEUESIZE"] = buffer
    # random.seed(42)

    mmm_sys = MMm_sys(mmm_config)
    env = simpy.Environment()
    # start the arrival processes
    env.process(mmm_sys.arrival_process(env))
    for server in mmm_sys.BusyServer.keys():
        env.process(mmm_sys.busyMonitor(env, server))

    # simulate until SIM_TIME
    env.run(until=mmm_sys.SIM_TIME)
    measure = mmm_sys.calculate_measure(env)
    measures.append(measure)
    print("Finished iteration {}".format(it))

preProProb = []
forCloProb = []
buffOccu = []
busyRate0 = []
busyRate1 = []

queueDelay = []
waitDelay = []
for mea in measures:
    preProProb.append(mea["preProb"])
    forCloProb.append(mea["forwCloudProb"])
    buffOccu.append(mea["avgBufOccu"])  # have some problem in counting !!!!!
    busyRate0.append(mea["serBusyRate"][0])
    busyRate1.append(mea["serBusyRate"][1])
    queueDelay.append(mea["avgQueDel"])
    waitDelay.append(mea["avgWaitDel"])

plt.plot(buffer_size, preProProb, "b", label="pre-process prob")
plt.plot(buffer_size, forCloProb, "g", label="forward prob")
plt.plot(buffer_size, buffOccu, "r", label="buffer occu rate")
plt.plot(buffer_size, busyRate0, "y", label="busy rate-ser0")
plt.plot(buffer_size, busyRate1, "k", label="busy rate-ser1")


plt.xlabel("buffer size")
plt.ylabel("normalized value")
plt.legend()
plt.grid(True)
# plt.show()
plt.savefig("./figures/Task2-1")
plt.close()


plt.plot(buffer_size, queueDelay, "b", label="avg queue delay")
plt.plot(buffer_size, waitDelay, "g", label="avg wait delay")
plt.xlabel("buffer size")
plt.ylabel("delay [s]")
plt.legend()
plt.grid(True)
#plt.show()
plt.savefig("./figures/Task2-2")
plt.close()


# compare with single server
mmm_config["SERNUM"]=1
measures_single = []
for buffer in buffer_size:
    it +=1
    mmm_config["QUEUESIZE"] = buffer
    # random.seed(42)

    mmm_sys = MMm_sys(mmm_config)
    env = simpy.Environment()
    # start the arrival processes
    env.process(mmm_sys.arrival_process(env))
    for server in mmm_sys.BusyServer.keys():
        env.process(mmm_sys.busyMonitor(env, server))

    # simulate until SIM_TIME
    env.run(until=mmm_sys.SIM_TIME)
    measure = mmm_sys.calculate_measure(env)
    measures_single.append(measure)
    print("Finished iteration {}".format(it))

preProProb2 = []
buffOccu2 = []
busyRate2 = []

queueDelay2 = []
waitDelay2 = []
for mea in measures_single:
    preProProb2.append(mea["preProb"])
    buffOccu2.append(mea["avgBufOccu"])  # have some problem in counting !!!!!
    busyRate2.append(mea["serBusyRate"][0])
    queueDelay2.append(mea["avgQueDel"])
    waitDelay2.append(mea["avgWaitDel"])

plt.plot(buffer_size, preProProb, "b", label="2-server")
plt.plot(buffer_size, preProProb2, "g", label="single-server")
plt.xlabel("buffer size")
plt.ylabel("normalized value")
plt.title("Pre-process Probability")
plt.legend()
plt.grid(True)
#plt.show()
plt.savefig("./figures/Task2-3")
plt.close()

plt.plot(buffer_size, buffOccu, "r", label="2-server")
plt.plot(buffer_size, buffOccu2, "g", label="single-server")
plt.xlabel("buffer size")
plt.ylabel("normalized value")
plt.title("Buffer Occupancy Rate")
plt.legend()
plt.grid(True)
#plt.show()
plt.savefig("./figures/Task2-4")
plt.close()

plt.plot(buffer_size, busyRate2, "r", label="single-server")
plt.plot(buffer_size, busyRate0, "g", label="2-server_ser0")
plt.plot(buffer_size, busyRate1, "b", label="2-server_ser1")
plt.xlabel("buffer size")
plt.ylabel("normalized value")
plt.title("Server Busy Rate")
plt.legend()
plt.grid(True)
#plt.show()
plt.savefig("./figures/Task2-5")
plt.close()

plt.plot(buffer_size, queueDelay, "b", label="2-ser queue delay")
plt.plot(buffer_size, waitDelay, "g", label="2-ser wait delay")
plt.plot(buffer_size, queueDelay2, "r", label="single-ser queue delay")
plt.plot(buffer_size, waitDelay2, "y", label="single-ser wait delay")
plt.xlabel("buffer size")
plt.ylabel("delay [s]")
plt.title("Delay")
plt.legend()
plt.grid(True)
#plt.show()
plt.savefig("./figures/Task2-6")
plt.close()
