import random
import simpy
from impl.MM1LimitBuffer import MM1_sys
import matplotlib.pyplot as plt

class Client:
    def __init__(self, TypeBFraction, ArrivalT):
        self.typeBFraction = TypeBFraction
        self.Tarr = ArrivalT
        self.TarrCloud = None
        self.servType = "None"
        self.packet_type = "A"
        """service type:
        None: pre-process in local micro date center
        simple: pre-proccess in Cloud
        complex: complex computational tasks in Cloud;
        full: pre-proccess + complex computation in Cloud"""

    def package_generate(self):
        indicator = random.uniform(0, 1)
        if indicator <= self.typeBFraction:
            self.packet_type = "B"
            return "B"  # package of type B has been generated
        else:
            self.packet_type = "A"
            return "A"  # package of type A has been generated

    def assign_cloud_arrive_time(self, tarr):
        self.TarrCloud = tarr


class Micro_Data_Center(MM1_sys):
    def __init__(self, config, CloudDC):
        super().__init__(config)
        self.cloud_data_center = CloudDC

    def arrival_process(self, environment):
        queue = self.MM1
        queueSize = self.queueSize
        while True:
            # print("Arrival no. ",data.arr+1," at time ",environment.now," with ",users," users" )

            # cumulate statistics
            self.data.arr += 1
            self.data.ut += self.users * (environment.now - self.data.oldT)
            self.data.bufferCount += len(queue) * (environment.now - self.data.oldT)
            self.data.oldT = environment.now

            # sample the time until the next event
            inter_arrival = random.expovariate(1.0 / self.ARRIVAL)

            # update state variable and put the client in the queue
            # Implementation of controlling queueing size
            cl = Client(self.config["TYPE_B_FRACTION"], environment.now)
            pack_type = cl.package_generate()
            if len(queue) < (queueSize + 1):
                queue.append(cl)
                self.users += 1
            else:
                if pack_type == "A":
                    cl.servType = "simple"
                else:
                    cl.servType = "full"
                self.send_packet_to_cloud(environment, cl)
                yield environment.timeout(inter_arrival)
                continue

            if self.users == 1:
                self.BusyServer = True
                service_time = self.calculate_service_time(self.config)
                environment.process(self.departure_process(environment, service_time, queue))

            # yield an event to the simulator
            yield environment.timeout(inter_arrival)

    def departure_process(self, environment, service_time, queue):
        # measure the waiting time
        self.data.waitingDelay += (environment.now - queue[0].Tarr)

        yield environment.timeout(service_time)
        # print("Departure no. ",data.dep+1," at time ",environment.now," with ",users," users" )

        # cumulate statistics
        self.data.dep += 1
        self.data.ut += self.users * (environment.now - self.data.oldT)
        self.data.bufferCount += len(queue) * (environment.now - self.data.oldT)
        self.data.oldT = environment.now

        # update state variable and extract the client in the queue
        self.users -= 1

        user = queue.pop(0)
        self.data.delay += (environment.now - user.Tarr)
        if user.packet_type == "B":
            user.servType = "complex"
            self.send_packet_to_cloud(environment, user)

        if self.users == 0:
            self.BusyServer = False
        else:
            service_time = self.calculate_service_time(self.config)
            environment.process(self.departure_process(environment, service_time, queue))

    def send_packet_to_cloud(self, environment, client):
        self.data.forwardToCould += 1
        self.cloud_data_center.receive_a_packet(environment, client)


class Cloud_Data_Center(MM1_sys):
    def __init__(self, config):
        super().__init__(config)
        self.cloudDorp = 0

    def receive_a_packet(self, environment, client):
        queue = self.MM1
        queueSize = self.queueSize

        self.data.arr += 1
        self.data.ut += self.users * (environment.now - self.data.oldT)
        self.data.bufferCount += len(queue) * (environment.now - self.data.oldT)
        self.data.oldT = environment.now

        client.assign_cloud_arrive_time(environment.now)
        if len(queue) < (queueSize + 1):
            queue.append(client)
            self.users += 1
            if self.users == 1:
                self.BusyServer = True
                service_time = self.calculate_service_time(queue[0],self.config)
                environment.process(self.departure_process(environment, service_time, queue))
        else:
            self.cloudDorp += 1

    def departure_process(self, environment, service_time, queue):
        # measure the waiting time
        self.data.waitingDelay += (environment.now - queue[0].TarrCloud)

        yield environment.timeout(service_time)
        # print("Departure no. ",data.dep+1," at time ",environment.now," with ",users," users" )

        # cumulate statistics
        self.data.dep += 1
        self.data.ut += self.users * (environment.now - self.data.oldT)
        self.data.bufferCount += len(queue) * (environment.now - self.data.oldT)
        self.data.oldT = environment.now

        # update state variable and extract the client in the queue
        self.users -= 1

        user = queue.pop(0)
        self.data.delay += (environment.now - user.Tarr)

        if self.users == 0:
            self.BusyServer = False
        else:
            service_time = self.calculate_service_time(queue[0],self.config)
            environment.process(self.departure_process(environment, service_time, queue))

    def calculate_service_time(self, client, conf):
        serType = client.servType
        param = 1 / conf["SERVICE"][serType]
        return random.expovariate(param)

    def calculate_drop_prob(self):
        if self.data.arr ==0:
            return 0
        else:
            return (self.data.arr-self.data.dep)/self.data.arr



if __name__ == "__main__":
    micro_config = {
        "SERVICE": 10.0,
        "ARRIVAL": 10 / 2,  # need to be set!!
        "SIM_TIME": 500000,
        "TYPE_B_FRACTION": 0.4,
        "DELAY_MICRO2CLOUD": 1,
        "QUEUESIZE": 3,
        "SERVICE_CONF": {}
    }

    cloud_config = {
        "LOAD": 0.85,
        "SERVICE": {"simple": 4.0, "complex": 6.0, "full": 10.0},
        "ARRIVAL": 10 / 0.85,  # need to be set!!
        "SIM_TIME": 500000,
        "DELAY_CLOUD2ACTUATOR": 0.8,
        "QUEUESIZE": 3,
        "SERVICE_CONF": {}
    }



    sim_time = []
    drop_prob =[]
    for i in range(100):
        random.seed(42)
        sim = 1+i*500
        cloud_data_center = Cloud_Data_Center(cloud_config)
        micro_data_center = Micro_Data_Center(micro_config,cloud_data_center)
        env = simpy.Environment()
        env.process(micro_data_center.arrival_process(env))
        env.process(micro_data_center.busyMonitor(env))
        env.process(micro_data_center.cloud_data_center.busyMonitor(env))
        env.run(until=sim)
        # micro_measure = micro_data_center.calculate_measure(env)
        # cloud_measure = cloud_data_center.calculate_measure(env)



        sim_time.append(sim)
        drop_prob.append(cloud_data_center.calculate_drop_prob())

    plt.plot(sim_time, drop_prob, "b", label="2-ser queuing delay")
    plt.xlabel("simulation time [s]")
    plt.ylabel("drop probability")
    plt.legend()
    plt.grid(True)
    plt.show()
