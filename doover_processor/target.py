import logging, json
from datetime import datetime, timezone

from pydoover.cloud import ProcessorBase, Channel
from pydoover import ui

from ui import construct_ui

test = 123

class target(ProcessorBase):

    ui_state_channel: Channel
    # ui_cmds_channel: Channel

    def setup(self):

        self.include_vocs = False

        # Get the required channels        
        self.ui_state_channel = self.api.create_channel("ui_state", self.agent_id)
        self.ui_cmds_channel = self.api.create_channel("ui_cmds", self.agent_id)
        self.location_channel = self.api.create_channel("location", self.agent_id)
        self.significant_event_channel = self.api.create_channel("significantEvent", self.agent_id)

        # self.uplink_channel = self.api.create_channel("farmo_uplink_recv", self.agent_id)
        self.downlink_channel = self.api.create_channel("tts_downlink", self.agent_id)

        ## Construct the UI
        self._ui_elements = construct_ui()
        self.ui_manager.set_children(self._ui_elements)
        self.ui_manager.pull()
    

    def process(self):
        message_type = self.package_config.get("message_type")

        if message_type == "DEPLOY":
            self.on_deploy()
        elif message_type == "DOWNLINK":
            self.on_downlink()
        elif message_type == "UPLINK":
            self.on_uplink()


    def on_deploy(self):
        ## Run any deployment code here

        # Construct the UI
        self.ui_manager.push(should_remove=True)

        # Publish a dummy message to uplink to trigger a new process of data
        last_uplink_packet = self.uplink_channel.fetch_aggregate()
        if last_uplink_packet is not None:
            self.uplink_channel.publish(last_uplink_packet)

    def on_downlink(self):
        # Run any downlink processing code here

        self.send_uplink_interval_if_required()
        self.send_burst_mode_if_required()

        # ## An updates of deployment start time processed in setup
        # ## Just need to push any changes here
        # self.ui_manager.push(should_remove=False)


    def on_uplink(self):
        # Run any uplink processing code here
        # if not (self.message and self.message.id):
        #     logging.info("No trigger message passed - fetching last message")
        #     self.message = self.uplink_channel.last_message
        #     if self.message is None:
        #         logging.info("No message found - skipping processing")
        #         return

        uplink_msg = self.uplink_channel.fetch_messages()

        if uplink_msg is None:
            logging.info("No uplink message found - skipping processing")
            return

        logging.info("Received message: " + str(uplink_msg))
        
        print("uplink_msg: ", uplink_msg)
    
        # self.ui_manager.update_variable("lastUplink", datetime.now(timezone.utc).isoformat())
        # self.ui_manager.update_variable("rawCurrent", rawCurrent)
        # self.ui_manager.update_variable("rawFlowCount", rawFlowCount)
        # self.ui_manager.update_variable("currentFlowRate", currentFlowRate )


        

        # msg_inner = raw_message.get("message", None)
        # if msg_inner is None:
        #     logging.info("No message field in message - skipping processing")
        #     return
        


        ## TODO - Publish the location
        # if "gps_lat" in msg_inner and msg_inner["gps_lat"] != 0 and "gps_lng" in msg_inner and msg_inner["gps_lng"] != 0:
        #     position = {
        #         'lat': msg_inner["gps_lat"],
        #         'long': msg_inner["gps_lng"],
        #     }
        #     self.location_channel.publish(position)

        # if "status" in msg_inner:
        #     status = msg_inner["status"]
        #     if status > 0:
        #         self.ui_manager.update_variable("waterRatStatus", True)
        #         self.ui_manager.update_variable("waterRatElement", 0)
        #     else:
        #         self.ui_manager.update_variable("waterRatStatus", False)
        #         self.ui_manager.update_variable("waterRatElement", 75)
        #         self.ui_manager.add_children(
        #             ui.WarningIndicator("waterRatProblem", "Problem Here")
        #         )

        #         try:
        #             if self.alert_required():
        #                 msg = "Water Rat has detected a problem"
        #                 self.significant_event_channel.publish(msg, save_log=True)
        #         except Exception as e:
        #             logging.error("Error in alert_required: " + str(e))

        

        # if "batv" in msg_inner:
        #     self.ui_manager.update_variable("batteryVoltage", msg_inner["batv"])

        # if "rsrp" in msg_inner:
        #     rsrp = msg_inner["rsrp"]
        #     signal_strength_percent = self.rsrp_to_percentage(rsrp)
        #     self.ui_manager.update_variable("signalStrength", signal_strength_percent)


        self.ui_manager.push(should_remove=True, even_if_empty=True)


    ## Helpers to assess wether alerts required
    def alert_required(self, current_status=True):
        state_messages = self.uplink_channel.fetch_messages()

        ## Search through the last few messages to find the last battery level
        if len(state_messages) < 2:
            logging.info("Not enough data to get previous levels")
            return current_status
        
        last_message = state_messages[1].fetch_payload()
        second_last_message = state_messages[2].fetch_payload()

        if self.alarm_in_message(last_message) and not self.alarm_in_message(second_last_message):
            return True
        return False

    def alarm_in_message(self, message):
        if "message" in message:
            message = message["message"]
        if "status" in message:
            return message["status"] > 0
        return False

    def rsrp_to_percentage(self, rsrp):
        
        min_rsrp = -100
        max_rsrp = -75
        signal_strength_percent = int(((rsrp - max_rsrp) / (max_rsrp - min_rsrp) + 1) * 100)
        signal_strength_percent = max(signal_strength_percent, 0)
        signal_strength_percent = min(signal_strength_percent, 100)

        return signal_strength_percent
    

    def send_uplink_interval_if_required(self):

        trigger_payload = None
        if 'msg_obj' in self.kwargs and self.kwargs['msg_obj'] is not None:
            trigger_payload = self.kwargs['msg_obj']['payload']
        
        uplink_interval_mins = None
        try:
            # should_reboot = cmds_obj['cmds']['shouldReboot']
            uplink_interval_mins = trigger_payload['cmds']['uplinkIntervalMins']
        except Exception as e:
            self.add_to_log("Could not find 'uplinkIntervalMins' in cmds object")
            return

        self.add_to_log(uplink_interval_mins)

        if uplink_interval_mins is not None:

            uplink_interval_secs = round( uplink_interval_mins * 60 )

            msg_obj = {
                "uplink_interval_secs" : uplink_interval_secs
            }

            self.add_to_log(msg_obj)

            tts_dl_channel = pd.channel(
                api_client=self.cli.api_client,
                agent_id=self.kwargs['agent_id'],
                channel_name="tts_downlinks"
            )
            tts_dl_channel.publish(
                msg_str=json.dumps(msg_obj),
            )

    def send_burst_mode_if_required(self):

        trigger_payload = None
        if 'msg_obj' in self.kwargs and self.kwargs['msg_obj'] is not None:
            trigger_payload = self.kwargs['msg_obj']['payload']
        
        start_burst_mode = None
        try:
            # start_burst_mode = cmds_obj['cmds']['shouldReboot']
            start_burst_mode = trigger_payload['cmds']['burstMode']
        except Exception as e:
            self.add_to_log("Could not find 'burstMode' in cmds object")
            return

        if start_burst_mode == True:
            msg_obj = {
                "burst_mode" : True
            }

            self.downlink_channel.publish(
                msg_str=json.dumps(msg_obj),
            )