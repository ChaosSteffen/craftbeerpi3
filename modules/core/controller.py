from modules import cbpi

class ActorController(object):
    @cbpi.try_catch(None)
    def actor_on(self, power=100, id=None):
        id = id or self.heater
        self.api.switch_actor_on(int(id), power=power)

    @cbpi.try_catch(None)
    def actor_off(self, id=None):
        id = id or self.heater
        self.api.switch_actor_off(int(id))

    @cbpi.try_catch(None)
    def actor_power(self, power, id=None):
        id = id or self.heater
        self.api.actor_power(int(id), power)

class SensorController(object):
    @cbpi.try_catch(None)
    def get_sensor_value(self, id=None):
        id = id or self.sensor
        return cbpi.get_sensor_value(id)

class ControllerBase(object):
    __dirty = False
    __running = False

    @staticmethod
    def init_global():
        print "GLOBAL CONTROLLER INIT"

    def notify(self, headline, message, type="success", timeout=5000):
        self.api.notify(headline, message, type, timeout)

    def is_running(self):
        return self.__running

    def init(self):
        self.__running = True

    def sleep(self, seconds):
        self.api.socketio.sleep(seconds)

    def stop(self):
        self.__running = False

    def __init__(self, *args, **kwds):
        for a in kwds:
            super(ControllerBase, self).__setattr__(a, kwds.get(a))
        self.api = kwds.get("api")
        self.heater = kwds.get("heater")
        self.sensor = kwds.get("sensor")

    def run(self):
        pass

class KettleController(ControllerBase, ActorController, SensorController):

    @staticmethod
    def chart(kettle):
        result = []
        result.append({"name": "Temp", "data_type": "sensor", "data_id": kettle.sensor})
        result.append({"name": "Target Temp", "data_type": "kettle", "data_id": kettle.id})

        return result

    def __init__(self, *args, **kwds):
        ControllerBase.__init__(self, *args, **kwds)
        self.kettle_id = kwds.get("kettle_id")

    def heater_on(self, power=100):
        if self.__kettle().heater:
            self.actor_on(power, int(self.__kettle().heater))

    def heater_off(self):
        if self.__kettle().heater:
            self.actor_off(int(self.__kettle().heater))

    def get_temp(self, id=None):
        return self.get_sensor_value(int(self.__kettle(id).sensor))

    @cbpi.try_catch(None)
    def get_target_temp(self, id=None):
        return self.__kettle(id).target_temp

    def __kettle(self, id=None):
        id = id or self.kettle_id
        return self.api.cache.get("kettle").get(id)

class FermenterController(ControllerBase, ActorController, SensorController):

    @staticmethod
    def chart(fermenter):
        result = []
        result.append({"name": "Temp", "data_type": "sensor", "data_id": fermenter.sensor})
        result.append({"name": "Target Temp", "data_type": "fermenter", "data_id": fermenter.id})
        return result

    def __init__(self, *args, **kwds):
        ControllerBase.__init__(self, *args, **kwds)
        self.fermenter_id = kwds.get("fermenter_id")
        self.cooler = kwds.get("cooler")
        self.heater = kwds.get("heater")

    def get_target_temp(self, id=None):
        return self.__fermenter(id).target_temp

    def heater_on(self, power=100):
        if self.__heater():
            self.actor_on(power, int(self.__heater()))

    def heater_off(self):
        if self.__heater():
            self.actor_off(int(self.__heater()))

    def cooler_on(self, power=100):
        if self.__cooler():
            self.actor_on(power, int(self.__cooler()))

    def cooler_off(self):
        if self.__cooler():
            self.actor_off(int(self.__cooler()))

    def get_temp(self, id=None):
        return self.get_sensor_value(int(self.__fermenter(id).sensor))

    def __heater(self):
        if self.__fermenter() is None: return None

        return self.__fermenter().heater

    def __cooler(self):
        if self.__fermenter() is None: return None

        return self.__fermenter().cooler

    def __fermenter(self, id=None):
        id = id or self.fermenter_id
        return self.api.cache.get("fermenter").get(id)
