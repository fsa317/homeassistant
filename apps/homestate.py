import appdaemon.appapi as appapi

# input_select.house_status
# binary_sensor.front_door
# sensor.last_motion
# device_tracker.frank_samsung
# device_tracker.samsunggalaxys7edgehome
# device_tracker.tiffanys_iphone
# device_tracker.tiffanysiphonehome

class HomeState(appapi.AppDaemon):

  def initialize(self):
      self.log("[HOMESTATE] init HomeState")
      self.listen_state(self.sensorChange, "device_tracker.frank_samsung")
      self.listen_state(self.sensorChange, "device_tracker.galaxys9home")
      self.listen_state(self.sensorChange, "device_tracker.tiffanys_iphone")
      self.listen_state(self.sensorChange, "device_tracker.tiffanysiphonehome")
      self.listen_state(self.frontDoorOpened, "binary_sensor.front_door",old="off",new="on")
      self.listen_state(self.frontDoorClosed, "binary_sensor.front_door",old="on",new="off")
      self.listen_state(self.motion,"sensor.last_motion",new="0")
      self.listen_state(self.doArriving,"input_select.house_status",new="Arriving")
      self.saidWelcomeMsg = False;
      self.log("[HOMESTATE] init HomeState complete")


  def doArriving(self, entity, attribute, old, new, kwargs):
      self.log("[HOMESTATE] doArriving")
      self.log("[HOMESTATE] Setting Nest to Home")
      self.call_service("nest/set_mode",home_mode="home")
      self.run_in(self.arrivingCallback,60*2)

  def motion(self, entity, attribute, old, new, kwargs):
      #self.log("[HOMESTATE] motion")
      current_house_state = self.get_state("input_select.house_status")
      #self.log("[HOMESTATE] motion-Current house status : {}".format(current_house_state))
      if ((current_house_state == 'Away') or (current_house_state == 'Extended Away')):
          self.log("[HOMESTATE] motion")
          self.log("[HOMESTATE] Setting to Arriving")
          self.set_state("input_select.house_status",state="Arriving")

  def frontDoorOpened(self, entity, attribute, old, new, kwargs):
      self.log("[HOMESTATE] frontDoorOpened {} {}".format(old,new))
      current_house_state = self.get_state("input_select.house_status")
      self.log("[HOMESTATE] FDO-Current house status : {}".format(current_house_state))
      if ((current_house_state == 'Away') or (current_house_state == 'Extended Away')):
          self.log("[HOMESTATE] Setting to Arriving")
          self.set_state("input_select.house_status",state="Arriving")



  def frontDoorClosed(self, entity, attribute, old, new, kwargs):
      self.log("[HOMESTATE] frontDoorClosed {} {}".format(old,new))
      current_house_state = self.get_state("input_select.house_status")
      self.log("[HOMESTATE] FDC-Current house status : {}".format(current_house_state))
      #self.call_service("script/tts_say",msg="Welcome Home Apaps")
      if ((current_house_state == 'Arriving')):
          self.log("[HOMESTATE] Door closed after arriving, say something")
          if (self.saidWelcomeMsg == False):
              self.call_service("script/tts_say",msg="Welcome Home A paps, I have missed you.")
          else:
              self.log("Already said something, skipping.")
          self.saidWelcomeMsg = True

      welcome_name = self.get_state("input_text.welcome_name_tts")
      if (welcome_name):
          self.log("[HOMESTATE] Saying welcome to {}".format(welcome_name))
          self.set_state("input_text.welcome_name_tts",state="")
          self.call_service("script/tts_say",msg="Welcome {}, I am Jarvis at your service.".format(welcome_name))

  def sensorChange(self, entity, attribute, old, new, kwargs):
      self.log("[HOMESTATE] Sensor Change {} : {} to {} ".format(entity,old,new))
      #Nothing changed, exit
      if (new==old):
          return
      current_house_state = self.get_state("input_select.house_status")
      self.log("[HOMESTATE] Current house status : {}".format(current_house_state))
      if (current_house_state == 'Home'):
          if (new == 'not_home'):
              # were currently home, but a device just left check to see if any device is still home
              anyDTHome = self.anyDeviceTrackerHome()
              self.log("[HOMESTATE] 1.0 Any Device Tracker Home {}".format(anyDTHome))
              if (anyDTHome is False):
                  self.run_in(self.checkMotionForAway,60*3)
      if (current_house_state == 'Away'):
          if (new == 'home'):
              self.log("[HOMESTATE] Setting to Arriving")
              self.set_state("input_select.house_status",state="Arriving")

  def arrivingCallback(self,kwargs):
      #called a few minutes after arriving
      self.log("[HOMESTATE] arrivingCallback")
      self.log("[HOMESTATE] Setting to Home")
      #reset this
      self.saidWelcomeMsg = False
      self.set_state("input_select.house_status",state="Home")

  def checkMotionForAway(self,kwargs):
      last_motion = self.get_state("sensor.last_motion")
      self.log("[HOMESTATE] checkMotionForAway last motion {}".format(last_motion))
      # check again that noone appears home
      anyDTHome = self.anyDeviceTrackerHome()
      if (anyDTHome is False and (int(last_motion)>1)):
          self.log("[HOMESTATE] Setting to Away")
          self.set_state("input_select.house_status",state="Away")

  def anyDeviceTrackerHome(self):
      dt1 = self.get_state("device_tracker.frank_samsung")
      dt2 = self.get_state("device_tracker.galaxys9home")
      dt3 = self.get_state("device_tracker.tiffanys_iphone")
      dt4 = self.get_state("device_tracker.tiffanysiphonehome")
      if (dt1 == 'home'):
        return True
      if (dt2 == 'home'):
       return True
      if (dt3 == 'home'):
        return True
      if (dt4 == 'home'):
       return True
      return False
