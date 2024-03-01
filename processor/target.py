#!/usr/bin/python3
from operator import truediv
import os, traceback, sys, time, json, math
from signal import signal


## This is the definition for a tiny lambda function
## Which is run in response to messages processed in Doover's 'Channels' system

## In the doover_config.json file we have defined some of these subscriptions
## These are under 'processor_deployments' > 'tasks'


## You can import the pydoover module to interact with Doover based on decisions made in this function
## Just add the current directory to the path first
# sys.path.append(os.path.dirname(__file__))
import sys

## attempt to delete any loaded pydoover modules that persist across lambdas
if 'pydoover' in sys.modules:
    del sys.modules['pydoover']
try: del pydoover
except: pass
try: del pd
except: pass

import pydoover as pd


class target:

    def __init__(self, *args, **kwargs):

        self.kwargs = kwargs
        ### kwarg
        #     'agent_id' : The Doover agent id invoking the task e.g. '9843b273-6580-4520-bdb0-0afb7bfec049'
        #     'access_token' : A temporary token that can be used to interact with the Doover API .e.g 'ABCDEFGHJKLMNOPQRSTUVWXYZ123456890',
        #     'api_endpoint' : The API endpoint to interact with e.g. "https://my.doover.com",
        #     'package_config' : A dictionary object with configuration for the task - as stored in the task channel in Doover,
        #     'msg_obj' : A dictionary object of the msg that has invoked this task,
        #     'task_id' : The identifier string of the task channel used to run this processor,
        #     'log_channel' : The identifier string of the channel to publish any logs to


    ## This function is invoked after the singleton instance is created
    def execute(self):

        start_time = time.time()

        self.create_doover_client()

        self.add_to_log( "running : " + str(os.getcwd()) + " " + str(__file__) )

        self.add_to_log( "kwargs = " + str(self.kwargs) )
        self.add_to_log( str( start_time ) )

        try:
            
            ## Do any processing you would like to do here
            message_type = None
            if 'message_type' in self.kwargs['package_config'] and 'message_type' is not None:
                message_type = self.kwargs['package_config']['message_type']

            if message_type == "DEPLOY":
                self.deploy()

            if message_type == "DOWNLINK":
                self.downlink()

            if message_type == "UPLINK":
                self.uplink()

        except Exception as e:
            self.add_to_log("ERROR attempting to process message - " + str(e))
            self.add_to_log(traceback.format_exc())

        self.complete_log()



    def deploy(self):
        ## Run any deployment code here
        
        ## Get the deployment channel
        ui_state_channel = self.cli.get_channel(
            channel_name="ui_state",
            agent_id=self.kwargs['agent_id']
        )

        ui_obj = {
            "state" : {
                "type": "uiContianer",
                "displayString": "",
                "children": {
                    "significantEvent": {
                        "type": "uiAlertStream",
                        "name": "significantEvent",
                        "displayString": "Notify me of any problems"
                    },
                    "level": {
                        "type": "uiVariable",
                        "name": "level",
                        "displayString": "Level (%)",
                        "varType": "float",
                        "decPrecision": 1,
                        "form": "radialGauge",
                        "ranges": [
                            {
                                "label" : "Low",
                                "min" : 0,
                                "max" : 40,
                                "colour" : "yellow",
                                "showOnGraph" : True
                            },
                            {
                                "label" : "Half",
                                "min" : 40,
                                "max" : 80,
                                "colour" : "blue",
                                "showOnGraph" : True
                            },
                            {
                                "label" : "Full",
                                "min" : 80,
                                "max" : 100,
                                "colour" : "green",
                                "showOnGraph" : True
                            }
                        ]
                    },
                    "levelAlarmSlider":{
                        "type": "uiSlider",
                        "name": "levelAlarmSlider",
                        "displayString": "Level Alarm (%)",
                        "min": 0,
                        "max": 100,
                        "dualSlider": True,
                        "icon": "fa-regular fa-bell"
                    },
                    "batteryLevel": { 
                        "type": "uiVariable",
                        "name": "batteryLevel",
                        "displayString": "Battery (%)",
                        "varType": "float",
                        "decPrecision": 0,
                        "ranges": [
                            {
                                "label" : "Low",
                                "min" : 0,
                                "max" : 30,
                                "colour" : "yellow",
                                "showOnGraph" : True
                            },
                            {
                                "label" : "Half",
                                "min" : 30,
                                "max" : 80,
                                "colour" : "blue",
                                "showOnGraph" : True
                            },
                            {
                                "label" : "Full",
                                "min" : 80,
                                "max" : 100,
                                "colour" : "green",
                                "showOnGraph" : True
                            }
                        ]
                    },
                    # "signalStrength": {
                    #     "type": "uiVariable",
                    #     "name": "signalStrength",
                    #     "displayString": "Signal Strength (%)",
                    #     "varType": "float",
                    #     "decPrecision": 0,
                    #     "ranges": [
                    #         {
                    #             "label" : "Low",
                    #             "min" : 0,
                    #             "max" : 30,
                    #             "colour" : "yellow",
                    #             "showOnGraph" : True
                    #         },
                    #         {
                    #             "label" : "Ok",
                    #             "min" : 30,
                    #             "max" : 60,
                    #             "colour" : "blue",
                    #             "showOnGraph" : True
                    #         },
                    #         {
                    #             "label" : "Strong",
                    #             "min" : 60,
                    #             "max" : 100,
                    #             "colour" : "green",
                    #             "showOnGraph" : True
                    #         }
                    #     ]
                    # },
                    "details_submodule": {
                        "type": "uiSubmodule",
                        "name": "details_submodule",
                        "displayString": "Details",
                        "children": {
                            "inputMax": {
                                "type": "uiFloatParam",
                                "name": "inputMax",
                                "displayString": "Max Level (cm)",
                                "min": 0,
                                "max": 999
                            },
                            # "inputLowLevel": {
                            #     "type": "uiFloatParam",
                            #     "name": "inputLowLevel",
                            #     "displayString": "Low level alarm (%)",
                            #     "min": 0,
                            #     "max": 99
                            # },
                            "inputZeroCal": {
                                "type": "uiFloatParam",
                                "name": "inputZeroCal",
                                "displayString": "Zero Calibration (cm)",
                                "min": -999,
                                "max": 999
                            },
                            "inputScalingCal": {
                                "type": "uiFloatParam",
                                "name": "inputScalingCal",
                                "displayString": "Scaling Calibration (x multiply)",
                                "min": -999,
                                "max": 999
                            },
                            "battAlarmLevel": {
                                "type": "uiFloatParam",
                                "name": "battAlarmLevel",
                                "displayString": "Battery Alarm (%)",
                                "min": 0,
                                "max": 100
                            },
                            "uplinkIntervalMins": {
                                "type": "uiFloatParam",
                                "name": "uplinkIntervalMins",
                                "displayString": "Reporting Interval (mins)",
                                "min": 0.1,
                                "max": 999
                            },
                            # "burstMode": {
                            #     "type": "uiAction",
                            #     "name": "burstMode",
                            #     "displayString": "Burst Mode",
                            #     "colour": "blue",
                            #     "requiresConfirm": True
                            # },
                            "rawlevel" : {
                                "type": "uiVariable",
                                "name": "rawlevel",
                                "displayString": "Level (cm)",
                                "varType": "float",
                                "decPrecision": 2
                            },
                            "rawBattery": {
                                "type": "uiVariable",
                                "name": "rawBattery",
                                "displayString": "Battery (V)",
                                "varType": "float",
                                "decPrecision": 2
                            },
                            # "lastRSSI": {
                            #     "type": "uiVariable",
                            #     "name": "lastRSSI",
                            #     "displayString": "Last RSSI",
                            #     "varType": "float"
                            # },
                        }
                    },
                    "node_connection_info": {
                        "type": "uiConnectionInfo",
                        "name": "node_connection_info",
                        "connectionType": "periodic",
                        "connectionPeriod": 600,
                        "nextConnection": 600
                    }
                }
            }
        }

        ui_state_channel.publish(
            msg_str=json.dumps(ui_obj)
        )


    def uplink(self):
        ## Run any uplink processing code here
        
        ## Get the uplink channel
        uplink_channel = self.cli.get_channel(
            channel_name="device_uplinks",
            agent_id=self.kwargs['agent_id']
        )

        ## Get the state channel
        ui_state_channel = self.cli.get_channel(
            channel_name="ui_state",
            agent_id=self.kwargs['agent_id']
        )

        ## Get the cmds channel
        ui_cmds_channel = self.cli.get_channel(
            channel_name="ui_cmds",
            agent_id=self.kwargs['agent_id']
        )

        self.compute_output_levels(ui_cmds_channel, ui_state_channel, uplink_channel)

        ui_state_channel.update() ## Update the details stored in the state channel so that warnings are computed from current values
        self.assess_warnings(ui_cmds_channel, ui_state_channel, uplink_channel)


    def downlink(self):
        ## Run any downlink processing code here
        
        self.send_uplink_interval_if_required()
        self.send_burst_mode_if_required()


    def create_doover_client(self):
        self.cli = pd.doover_iface(
            agent_id=self.kwargs['agent_id'],
            access_token=self.kwargs['access_token'],
            endpoint=self.kwargs['api_endpoint'],
        )

    def add_to_log(self, msg):
        if not hasattr(self, '_log'):
            self._log = ""
        self._log = self._log + str(msg) + "\n"

    def complete_log(self):
        if hasattr(self, '_log') and self._log is not None:
            log_channel = self.cli.get_channel( channel_id=self.kwargs['log_channel'] )
            log_channel.publish(
                msg_str=self._log
            )

    ## Compute output values from raw values
    def compute_output_levels(self, cmds_channel, state_channel, uplink_channel):

        self.notifications_channel = pd.channel(
            api_client=self.cli.api_client,
            agent_id=self.kwargs['agent_id'],
            channel_name='significantEvent',
        )

        uplink_obj = uplink_channel.get_aggregate()
        state_obj = state_channel.get_aggregate()
        cmds_obj = cmds_channel.get_aggregate()

        uplink_interval = 30 * 60
        try:
            uplink_interval = uplink_obj['uplink_interval_secs']
        except Exception as e:
            self.add_to_log("Could not get uplink interval seconds - " + str(e))

        batt_volts = None
        batt_percent = None
        try:
            batt_volts = uplink_obj['batt_mvolts'] / 1000
            batt_percent = self.batt_volts_to_percent(batt_volts) * 100
        except Exception as e:
            self.add_to_log("Could not get battery raw volts - " + str(e))

        raw_reading_1 = None
        try:
            raw_reading_1 = uplink_obj['level_cm']
        except Exception as e:
            self.add_to_log("Could not get current raw reading - " + str(e))

        sensor_1_max = 250
        try:
            sensor_1_max = cmds_obj['cmds']['inputMax']
        except Exception as e:
            self.add_to_log("Could not get sensor max - " + str(e))

        sensor_1_zero_cal = 0
        try:
            sensor_1_zero_cal = cmds_obj['cmds']['inputZeroCal']
        except Exception as e:
            self.add_to_log("Could not get sensor zero cal - " + str(e))

        sensor_1_scaling_cal = 1
        try:
            sensor_1_scaling_cal = cmds_obj['cmds']['inputScalingCal']
        except Exception as e:
            self.add_to_log("Could not get sensor scaling cal - " + str(e))

        input1_processed = None
        input1_percentage_level = None
        if raw_reading_1 is not None and raw_reading_1 > 0:
            input1_processed = raw_reading_1#sensor_1_max - raw_reading_1
            input1_processed = (input1_processed + sensor_1_zero_cal) * sensor_1_scaling_cal
            input1_percentage_level = round((input1_processed / sensor_1_max) * 100, 1)

        # https://www.mathsisfun.com/geometry/cylinder-horizontal-volume.html
        # r = 50 ## 50 %
        # h = input1_percentage_level
        # input1_percentage_level = (math.acos((r-h)/r)*(r*r)) - ((r-h)*math.sqrt(2*r*h-(h*h)))

        msg_obj = {
            "state" : {
                "children" : {
                    "level" : {
                        "currentValue" : input1_percentage_level
                    },
                    "batteryLevel" : {
                        "currentValue" : batt_percent
                    },
                    "details_submodule" : {
                        "children" : {
                            "rawlevel" : {
                                "currentValue" : raw_reading_1
                            },
                            "rawBattery" : {
                                "currentValue" : batt_volts
                            }
                            # "rawlevel_processed" : {
                            #     "currentValue" : input1_processed
                            # }
                        }
                    },
                    "node_connection_info": {
                        "connectionPeriod": uplink_interval,
                        "nextConnection": uplink_interval
                    }
                }
            }
        }

        state_channel.publish(
            msg_str=json.dumps(msg_obj),
        )


    def batt_volts_to_percent(self, volts):
        
        out_val = 0
        if volts < 3.2:
            out_val = 0
        elif volts < 3.5:
            out_val = ((volts - 3.2) * (1/3))
        else:
            out_val = 0.1 + ((volts - 3.5) * 1.5)

        out_val = max(out_val, 0)
        out_val = min(out_val, 1)

        return out_val
        

    def assess_warnings(self, cmds_channel, state_channel, uplink_channel):
        
        uplink_obj = uplink_channel.get_aggregate()
        cmds_obj = cmds_channel.get_aggregate()

        level_alarm = None
        try: level_alarm = cmds_obj['cmds']['inputLowLevel']
        except Exception as e: self.add_to_log("Could not get level alarm")

        battery_alarm = None
        try: battery_alarm = cmds_obj['cmds']['battAlarmLevel']
        except Exception as e: self.add_to_log("Could not get battery alarm")
        
        state_obj = state_channel.get_aggregate()

        curr_level = None
        try: curr_level = state_obj['state']['children']['level']['currentValue']
        except Exception as e: self.add_to_log("Could not get current level - " + str(e))

        curr_battery_level = None
        try: curr_battery_level = state_obj['state']['children']['batteryLevel']['currentValue']
        except Exception as e: self.add_to_log("Could not get current battery level - " + str(e))

        notifications_channel = pd.channel(
            api_client=self.cli.api_client,
            agent_id=self.kwargs['agent_id'],
            channel_name='significantEvent',
        )
        activity_log_channel = pd.channel(
            api_client=self.cli.api_client,
            agent_id=self.kwargs['agent_id'],
            channel_name='activity_logs',
        )
        last_notification_age = self.get_last_notification_age()

        level_warning = None
        if level_alarm is not None and curr_level is not None and curr_level < level_alarm:
            self.add_to_log("Sensor level is low")

            level_warning = {
                "type": "uiWarningIndicator",
                "name": "levelLowWarning",
                "displayString": "Level Low"
            }
            
            prev_level = self.get_previous_level(state_channel, "level")
            if prev_level is not None and prev_level > level_alarm:
                if last_notification_age is None or last_notification_age > (12 * 60 * 60):
                    self.add_to_log("Sending low level notification")
                    notifications_channel.publish(
                        msg_str="Level is getting low"
                    )
                    activity_log_channel.publish(json.dumps({
                        "activity_log" : {
                            "action_string" : "Level is getting low"
                        }
                    }))
                else:
                    self.add_to_log("Not sending low level notification as already sent notification recently")


        batt_warning = None
        if battery_alarm is not None and curr_battery_level is not None and curr_battery_level < battery_alarm:
            self.add_to_log("Battery level is low")
            
            batt_warning = {
                "type": "uiWarningIndicator",
                "name": "battLowWarning",
                "displayString": "Battery Low"
            }

            prev_level = self.get_previous_level(state_channel, "batteryLevel")
            if prev_level is not None and prev_level > battery_alarm:
                if last_notification_age is None or last_notification_age > (12 * 60 * 60):
                    self.add_to_log("Sending low battery notification")
                    notifications_channel.publish(
                        msg_str="Battery is getting low"
                    )
                    activity_log_channel.publish(json.dumps({
                        "activity_log" : {
                            "action_string" : "Battery is getting low"
                        }
                    }))
                else:
                    self.add_to_log("Not sending low battery notification as already sent notification recently")


        ## Assess status icon
        status_icon = None
        if curr_level is None:
            status_icon = "off"
        else:
            idle_icon_level = 60
            if level_alarm is not None:
                idle_icon_level = (100 + level_alarm) / 2   ## midpoint of full and alarm level
            if curr_level < idle_icon_level:
                status_icon = "idle"


        msg_obj = {
            "state" : {
                "children" : {
                    "battLowWarning": batt_warning,
                    "levelLowWarning": level_warning
                },
                "statusIcon" : status_icon
            }
        }

        state_channel.publish(
            msg_str=json.dumps(msg_obj),
            save_log=False
        )

    def get_previous_level(self, state_channel, key):
        state_messages = state_channel.get_messages()

        ## Search through the last few messages to find the last battery level
        if len(state_messages) < 3:
            self.add_to_log("Not enough data to get previous levels")
            return None

        ### The device published a new message,
        # Then we just published a message to update rssi, snr, etc
        # so we need the message one before that
        i = 2
        prev_level = None
        while prev_level is None and i < 10 and i < len(state_messages):
            try:
                prev_state_payload = json.loads( state_messages[i].get_payload() )
                prev_level = prev_state_payload['state']['children'][key]['currentValue']
                self.add_to_log("Found previous level of " + str(prev_level) + ", " + str(i) + " messages ago : " + str(state_messages[i].message_id))
            except Exception as e:
                pass
            i = i + 1

        if prev_level is None:
            self.add_to_log("Could not get previous level - " + str(e))
        
        return prev_level 

    def get_last_notification_age(self):
        notifications_channel = pd.channel(
            api_client=self.cli.api_client,
            agent_id=self.kwargs['agent_id'],
            channel_name='significantEvent',
        )
        notifications_messages = notifications_channel.get_messages()

        last_notification_age = None
        if len(notifications_messages) > 0:
            try:
                last_notif_message = notifications_messages[0].update()
                last_notification_age = last_notif_message['current_time'] - last_notif_message['timestamp']
            except Exception as e:
                self.add_to_log("Could not get age of last notification - " + str(e))
                pass  

        return last_notification_age

    
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

            device_dl_channel = pd.channel(
                api_client=self.cli.api_client,
                agent_id=self.kwargs['agent_id'],
                channel_name="device_downlinks"
            )
            device_dl_channel.publish(
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

            device_dl_channel = pd.channel(
                api_client=self.cli.api_client,
                agent_id=self.kwargs['agent_id'],
                channel_name="device_downlinks"
            )
            device_dl_channel.publish(
                msg_str=json.dumps(msg_obj),
            )