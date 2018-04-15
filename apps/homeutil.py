import appdaemon.appapi as appapi

#
#
# Args:
#

class DoorLock(appapi.AppDaemon):

  def initialize(self):
     self.log("[AUTODOORLOCK] Starting Door Lock")
     self.listen_state(self.doorstate, "binary_sensor.front_door")
     self.handle = None

  def doorstate(self, entity, attribute, old, new, kwargs):
     #self.log("New door state {}".format(new))
     #self.log("Old door state {}".format(old))
     lockstate = self.get_state("lock.schlage_be469nxcen_touchscreen_deadbolt_locked")
     isAutoLockEnabled = self.get_state("input_boolean.enable_front_door_autolock")
     #self.log("[AUTODOORLOCK] Lock State: {}".format(lockstate))
     #self.log("[AUTODOORLOCK] isAutoLockEnabled State: {}".format(isAutoLockEnabled))
     if (lockstate != "locked" and isAutoLockEnabled == "on" and new == "off" and self.handle is None):
       self.log("[AUTODOORLOCK] Scheduling lock")
       self.handle = self.run_in(self.lockdoor,60)
     if (new!="off" and self.handle is not None):
       self.log("[AUTODOORLOCK] Door is opened, cancel timer")
       self.cancel_timer(self.handle)
       self.handle = None

  def lockdoor(self,kwargs):
    self.log("locking door")
    self.call_service("lock/lock",entity_id="lock.schlage_be469nxcen_touchscreen_deadbolt_locked")
    self.handle = None

################### LIGHTS ###########
class OutsideLights(appapi.AppDaemon):

  def initialize(self):
    self.run_at_sunrise(self.sunrise_cb)
    self.run_at_sunset(self.before_sunset_cb, offset=-1500)

  def sunrise_cb(self, kwargs):
    self.log("Sunrise CB")
    self.turn_off("switch.leviton_vrs151lz_binary_scene_switch_switch")

  def before_sunset_cb(self, kwargs):
    self.log("Sunset CB")
    self.turn_on("switch.leviton_vrs151lz_binary_scene_switch_switch")
