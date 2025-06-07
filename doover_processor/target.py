import logging
import json
from datetime import datetime, timezone

from pydoover.cloud import ProcessorBase, Channel
from pydoover import ui

from ui import construct_ui


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
        self.uplink_channel = self.api.create_channel("tts_uplink_recv", self.agent_id)
        self.downlink_channel = self.api.create_channel("tts_downlink", self.agent_id)

        # Construct the UI
        self._ui_elements = construct_ui()
        self.ui_manager.set_children(self._ui_elements)
        self.ui_manager.pull()

        # Set parameters
        self.l_per_pulse = 10  # Litres per pulse
        self.min_flow_rate = 1  # Litres per minute
        self.alarm_amperage = 2  # Amps

    def process(self):
        message_type = self.package_config.get("message_type")

        if message_type == "DEPLOY":
            self.on_deploy()
        elif message_type == "DOWNLINK":
            self.on_downlink()
        elif message_type == "UPLINK":
            self.on_uplink()

    def on_deploy(self):
        # Run any deployment code here

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

    def on_uplink(self):
        # Run any uplink processing code here
        try:
            uplink_msg = self.process_uplink_message()
        except Exception as e:
            logging.error("Error processing uplink message: " + str(e))

        if uplink_msg is None:
            logging.info("No uplink message found - skipping processing")
            return

        logging.info("Received message: " + str(uplink_msg))

        # Calculate current flow rate and current amperage
        current_flow_rate = self.calc_current_flow_rate(uplink_msg.get('rawFlowCount'))
        current_amperage = self.calc_current_amperage(uplink_msg.get('rawCurrent', None))
        total_count = self.get_running_count_total(uplink_msg.get('rawFlowCount', None))

        # Update elements
        self.ui_manager.get_element("runningCountTotal").coerce(total_count)
        self.ui_manager.update_variable("currentFlowRate", current_flow_rate)
        self.ui_manager.update_variable("currentAmperage", current_amperage)
        self.ui_manager.update_variable("rawBattery", uplink_msg.get('rawBattery', None))
        self.ui_manager.update_variable("uplinkIntervalMins", uplink_msg.get('sleepTime'))
        self.ui_manager.update_variable("rawCurrent", uplink_msg.get('rawCurrent', None))
        self.ui_manager.update_variable("rawFlowCount", uplink_msg.get('rawFlowCount', None))
        self.ui_manager.update_variable("lastRSSI", uplink_msg.get('lastRSSI', None))
        self.ui_manager.update_variable("lastUsedGateway", uplink_msg.get('lastUsedGateway', None))
        self.ui_manager.update_variable("signalStrength", self.rssi_to_percentage(uplink_msg.get('lastRSSI', None)))

        # Push Updated UI
        self.ui_manager.push(should_remove=True, even_if_empty=True)

        lastNotificationSent = self.ui_manager.get_element("prevNotificationSent").current_value

        # Check and send alerts if required
        if current_flow_rate is not None and current_amperage is not None:
            if current_flow_rate < 1 and current_amperage > 2:
                if lastNotificationSent is None or lastNotificationSent is False:
                    self.ui_manager.coerce_command("prevNotificationSent", True)
                    msg = f"Flow rate is below 1 L/min, and current is above {round(current_amperage,1)} A, manual flow meter check required"
                    self.significant_event_channel.publish(msg, save_log=True)
            else:
                self.ui_manager.coerce_command("prevNotificationSent",False)


        self.ui_manager.push(should_remove=True, even_if_empty=True)

    def process_uplink_message(self):
        aggregate = self.uplink_channel.fetch_aggregate()
        res = {}
        decoded_payload = None
        if aggregate is not None:
            try:
                decoded_payload = aggregate['uplink_message']['decoded_payload']
                print("decoded_payload: ", decoded_payload)
            except Exception as e:
                logging.error("Error fetching uplink message: " + str(e))

        if decoded_payload is None:
            return None
        try:
            res['rawBattery'] = decoded_payload['batt_volts']
        except Exception as e:
            logging.error("Error fetching battery voltage: " + str(e))

        try:
            res['rawCurrent'] = decoded_payload['current_reading']
        except Exception as e:
            logging.error("Error fetching current reading: " + str(e))

        try:
            res['rawFlowCount'] = decoded_payload['total_count']
        except Exception as e:
            logging.error("Error fetching flow count: " + str(e))

        try:
            res['sleepTime'] = decoded_payload['sleep_time']
        except Exception as e:
            logging.error("Error fetching sleep time: " + str(e))

        try:
            res['lastRSSI'] = aggregate['uplink_message']['rx_metadata'][0]['rssi']
        except Exception as e:
            logging.error("Error fetching RSSI: " + str(e))

        try:
            res['lastUsedGateway'] = aggregate['uplink_message']['rx_metadata'][0]['gateway_ids']['gateway_id']
        except Exception as e:
            logging.error("Error fetching gateway ID: " + str(e))

        return res

    def calc_current_flow_rate(self, new_flow_count):
        prev_flow_count = self.get_prev_count()
        last_time_stamp = self.get_prev_timestamp()

        if prev_flow_count is None:
            prev_flow_count = new_flow_count

        if last_time_stamp is None:
            self.ui_manager.get_element("lastRecordedTime").coerce(datetime.now(timezone.utc))
            return None

        time_interval = (datetime.now(timezone.utc).timestamp() - last_time_stamp)

        res = ((new_flow_count - prev_flow_count) * self.l_per_pulse) / (time_interval / 60)

        self.ui_manager.get_element("lastRecordedTime").coerce(datetime.now(timezone.utc))
        return res

    def calc_current_amperage(self, current_reading):
        if current_reading is None:
            logging.error("No current reading found")
            return None
        elif current_reading < 3.8:
            logging.error("Current sensor error")
            return None

        max_current = 300
        min_current = 0

        return (((current_reading - 4) / 16) * (max_current - min_current)) + min_current
    
    def get_running_count_total(self, new_count):
        total = self.ui_manager.get_element("runningCountTotal").current_value 
        last_count = self.ui_manager.get_element("rawFlowCount").current_value

        if last_count is None or new_count < last_count:
            last_count = 0
        
        if total is None:
            total = 0

        if new_count is None:
            logging.error("No count recorded")
            return None
        
        total += new_count - last_count

    def get_prev_count(self):
        try:
            ui_state = self.ui_state_channel.fetch_aggregate()
            count = ui_state['state']['children']['detailsSubmodule']['children']['rawFlowCount']['currentValue']
            return count
        except Exception as e:
            logging.error("Error fetching UI state: " + str(e))
            return None

    def get_prev_timestamp(self):
        try:
            res = self.ui_manager.get_command("lastRecordedTime").current_value
            return res
        except Exception as e:
            logging.error("Error fetching last recorded time: " + str(e))
            return None

    # Helpers to assess whether alerts required
    def alert_required(self, current_status=True):
        state_messages = self.uplink_channel.fetch_messages()

        # Search through the last few messages to find the last battery level
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

    def rssi_to_percentage(self, rssi):
        min_rssi = -140
        max_rssi = -40
        signal_strength_percent = int(((rssi - max_rssi) / (max_rssi - min_rssi) + 1) * 100)
        signal_strength_percent = max(signal_strength_percent, 0)
        signal_strength_percent = min(signal_strength_percent, 100)

        return signal_strength_percent

    def send_uplink_interval_if_required(self):
        if self.message is not None:
            trigger_payload = self.message.fetch_payload()
        else:
            trigger_payload = None

        uplink_interval_mins = None
        try:
            uplink_interval_mins = trigger_payload['cmds']['uplinkIntervalMins']
        except Exception as e:
            self.add_to_log("Could not find 'uplinkIntervalMins' in cmds object")
            return

        self.add_to_log(uplink_interval_mins)

        if uplink_interval_mins is not None:
            uplink_interval_secs = round(uplink_interval_mins * 60)

            msg_obj = {
                "uplink_interval_secs": uplink_interval_secs
            }

            self.add_to_log(msg_obj)

            self.downlink_channel.publish(
                msg_str=json.dumps(msg_obj),
            )

    def send_burst_mode_if_required(self):
        trigger_payload = None
        if 'msg_obj' in self.kwargs and self.kwargs['msg_obj'] is not None:
            trigger_payload = self.kwargs['msg_obj']['payload']

        start_burst_mode = None
        try:
            start_burst_mode = trigger_payload['cmds']['burstMode']
        except Exception as e:
            self.add_to_log("Could not find 'burstMode' in cmds object")
            return

        if start_burst_mode is True:
            msg_obj = {
                "burst_mode": True
            }

            self.downlink_channel.publish(
                msg_str=json.dumps(msg_obj),
            )