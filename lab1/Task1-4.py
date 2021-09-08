import random
import simpy
from impl.MM1LimitBuffer import MM1_sys
import math
import matplotlib.pyplot as plt
import numpy as np


class MG1_sys_gamma(MM1_sys):

    def __init__(self, config):
        super().__init__(config)

    def calculate_service_time(self, conf):
        service_config = conf["SERVICE_CONF"]
        return random.gammavariate(service_config["alpha"], service_config["beta"])


class MG1_sys_uniform(MM1_sys):

    def __init__(self, config):
        super().__init__(config)

    def calculate_service_time(self, conf):
        service_config = conf["SERVICE_CONF"]
        return random.uniform(service_config["a"], service_config["b"])


class MG1_sys_gauss(MM1_sys):

    def __init__(self, config):
        super().__init__(config)

    def calculate_service_time(self, conf):
        service_config = conf["SERVICE_CONF"]
        time = random.gauss(service_config["mu"], service_config["sigma"])
        if time<0:
            return 0
        else:
            return time


if __name__ == "__main__":
    random.seed(42)

    mg1_config = {
        "SERVICE": 10.0,
        "ARRIVAL": 10 / 0.85,
        "TYPE1": 1,
        "SIM_TIME": 500000,
        "QUEUESIZE": math.inf,
        "SERVICE_CONF": {}
    }

    # E[X]=10 Var[X]=100
    avg_queue = [[], [], [], []]
    avg_wait = [[], [], [], []]
    buff_occu = [[], [], [], []]
    busy_rate = [[], [], [], []]
    service_exp = []
    Load = 0.0
    for i in range(20):
        Load = 0.00001+0.05*i
        mg1_config["ARRIVAL"] = mg1_config["SERVICE"] / Load
        service_exp.append(Load)
        # mm1
        mm1_sys = MM1_sys(mg1_config)
        env = simpy.Environment()
        env.process(mm1_sys.arrival_process(env))
        env.process(mm1_sys.busyMonitor(env))
        env.run(until=mm1_sys.SIM_TIME)
        measure_mm1 = mm1_sys.calculate_measure(env)
        avg_queue[0].append(measure_mm1["avgQueDel"])
        avg_wait[0].append(measure_mm1["avgWaitDel"])
        buff_occu[0].append(measure_mm1["avgBufOccu"])
        busy_rate[0].append(measure_mm1["serBusyRate"])

        # MG1 gaussian
        mg1_config["SERVICE_CONF"] = {"mu": mg1_config["SERVICE"], "sigma": 3}
        mg1_sys_gauss = MG1_sys_gauss(mg1_config)
        env2 = simpy.Environment()
        env2.process(mg1_sys_gauss.arrival_process(env2))
        env2.process(mg1_sys_gauss.busyMonitor(env2))
        env2.run(until=mg1_sys_gauss.SIM_TIME)
        measure_gauss = mg1_sys_gauss.calculate_measure(env2)
        avg_queue[1].append(measure_gauss["avgQueDel"])
        avg_wait[1].append(measure_gauss["avgWaitDel"])
        buff_occu[1].append(measure_gauss["avgBufOccu"])
        busy_rate[1].append(measure_gauss["serBusyRate"])

        # MG1 uniform
        mg1_config["SERVICE_CONF"] = {"a": 0, "b": mg1_config["SERVICE"] * 2}
        mg1_sys_uni = MG1_sys_uniform(mg1_config)
        env3 = simpy.Environment()
        env3.process(mg1_sys_uni.arrival_process(env3))
        env3.process(mg1_sys_uni.busyMonitor(env3))
        env3.run(until=mg1_sys_uni.SIM_TIME)
        measure_uni = mg1_sys_uni.calculate_measure(env3)
        avg_queue[2].append(measure_uni["avgQueDel"])
        avg_wait[2].append(measure_uni["avgWaitDel"])
        buff_occu[2].append(measure_uni["avgBufOccu"])
        busy_rate[2].append(measure_uni["serBusyRate"])
        # MG1 gamma
        mg1_config["SERVICE_CONF"] = {"alpha": 2, "beta": mg1_config["SERVICE"] / 2}
        mg1_sys_gamma = MG1_sys_gamma(mg1_config)
        env4 = simpy.Environment()
        env4.process(mg1_sys_gamma.arrival_process(env4))
        env4.process(mg1_sys_gamma.busyMonitor(env4))
        env4.run(until=mg1_sys_gamma.SIM_TIME)
        measure_gamma = mg1_sys_gamma.calculate_measure(env4)
        avg_queue[3].append(measure_gamma["avgQueDel"])
        avg_wait[3].append(measure_gamma["avgWaitDel"])
        buff_occu[3].append(measure_gamma["avgBufOccu"])
        busy_rate[3].append(measure_gamma["serBusyRate"])

        print("Finished iteration: ",i)

    plt.figure()
    plt.plot(service_exp,avg_queue[0],"r",label = "exp dist")
    plt.plot(service_exp,avg_queue[1],"g",label = "gauss dist")
    plt.plot(service_exp,avg_queue[2],"b",label = "uniform dist")
    plt.plot(service_exp,avg_queue[3],"y",label = "gamma dist")
    plt.xlabel("Load")
    plt.ylabel("Avg queuing delay [s]")
    plt.grid(True)
    plt.legend()
    plt.show()

    plt.figure()
    plt.plot(service_exp,avg_wait[0],"r",label = "exp dist")
    plt.plot(service_exp,avg_wait[1],"g",label = "gauss dist")
    plt.plot(service_exp,avg_wait[2],"b",label = "uniform dist")
    plt.plot(service_exp,avg_wait[3],"y",label = "gamma dist")
    plt.xlabel("Load")
    plt.ylabel("Avg waiting delay [s]")
    plt.grid(True)
    plt.legend()
    plt.show()

    plt.figure()
    plt.plot(service_exp,buff_occu[0],"r",label = "exp dist")
    plt.plot(service_exp,buff_occu[1],"g",label = "gauss dist")
    plt.plot(service_exp,buff_occu[2],"b",label = "uniform dist")
    plt.plot(service_exp,buff_occu[3],"y",label = "gamma dist")
    plt.xlabel("Load")
    plt.ylabel("Avg buffer occupancy")
    plt.grid(True)
    plt.legend()
    plt.show()

    plt.figure()
    plt.plot(service_exp,busy_rate[0],"r",label = "exp dist")
    plt.plot(service_exp,busy_rate[1],"g",label = "gauss dist")
    plt.plot(service_exp,busy_rate[2],"b",label = "uniform dist")
    plt.plot(service_exp,busy_rate[3],"y",label = "gamma dist")
    plt.xlabel("Load")
    plt.ylabel("Avg server busy rate")
    plt.grid(True)
    plt.legend()
    plt.show()
