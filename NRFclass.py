
class NRFSensor:
    global Sensor

    basetopic = "nrf/"
    list = {}
    
    def Spin():
        if not Sensor.mqttconnected:
            Sensor.mqttconnected = Sensor.MQTTConnect()

        try:
            for nrf in NRFSensor.list:
                if NRFSensor.list[nrf].pubneeded:
                    Sensor.Callpublish(Sensor.mqttclient, NRFSensor.basetopic, str(nrf) , [NRFSensor.list[nrf]])
        except:
            print("Error in Spin")
            Sensor.mqttconnected = False

    def update(self, state, uptime, errors, sent, battery):
        self.state = state
        self.packets += 1
        self.uptime = uptime
        self.errors = errors
        self.sent = sent
        if battery > 0 and battery < 4:
            self.battery = battery
        self.publish = [["radio" , self.radio], ["state", self.state], ["pkts",self.packets], ["uptime", self.uptime], ["errors",self.errors], ["sent",self.sent], ["battery",self.battery]]
        
        self.pubneeded = True
        
    def __init__(self, radio ): 
        
        
        self.radio = radio 
        self.state = False
        self.packets = 0
        self.errors = 0
        self.sent = 0
        self.uptime = 0
        self.battery = 0
        self.save = True
        
        self.pubneeded = False
        self.triggered = False 
        self.publish = [["radio" , self.radio], ["state", self.state], ["pkts",self.packets], ["uptime", self.uptime], ["errors",self.errors], ["sent",self.sent], ["battery",self.battery]]
        NRFSensor.list[radio] = self
