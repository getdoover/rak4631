#!/usr/bin/python3
import os, sys, time, json, math
from signal import signal


## This is the definition for a tiny lambda function
## Which is run in response to messages processed in Doover's 'Channels' system

## In the doover_config.json file we have defined some of these subscriptions
## These are under 'processor_deployments' > 'tasks'


## You can import the pydoover module to interact with Doover based on decisions made in this function
## Just add the current directory to the path first
sys.path.append(os.path.dirname(__file__))
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

        self.complete_log()



    def deploy(self):
        ## Run any deployment code here
        
        ## Get the deployment channel
        ui_state_channel = pd.channel(
            api_client=self.cli.api_client,
            channel_name="ui_state",
            agent_id=self.kwargs['agent_id'],
        )

        ui_obj = {
            "state" : {
                "type": "uiContianer",
                "displayString": "",
                "children": {
                    "significantEvent": {
                        "type": "uiAlertStream",
                        "name": "significantEvent",
                        "displayString": "SMS after rain event"
                    },
                    "rainfallEvent": {
                        "type": "uiVariable",
                        "name": "rainfallEvent",
                        "displayString": "Rainfall (mm)",
                        "varType": "float",
                        "decPrecision": 1,
                    },
                    "resetRainEvent": {
                        "type": "uiAction",
                        "name": "resetRainEvent",
                        "displayString": "Reset Event",
                        "colour": "blue",
                        "requiresConfirm": True
                    },
                    "lastTimeNonZeroUpdate": {
                        "type": "uiHiddenValue",
                        "name": "lastTimeNonZeroUpdate"
                    },
                    "eventZeroCounts": {
                        "type": "uiHiddenValue",
                        "name": "eventZeroCounts"
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
                    "signalStrength": {
                        "type": "uiVariable",
                        "name": "signalStrength",
                        "displayString": "Signal Strength (%)",
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
                                "label" : "Ok",
                                "min" : 30,
                                "max" : 60,
                                "colour" : "blue",
                                "showOnGraph" : True
                            },
                            {
                                "label" : "Strong",
                                "min" : 60,
                                "max" : 100,
                                "colour" : "green",
                                "showOnGraph" : True
                            }
                        ]
                    },
                    "details_submodule": {
                        "type": "uiSubmodule",
                        "name": "details_submodule",
                        "displayString": "Details",
                        "children": {
                            "resetAfter": {
                                "type": "uiFloatParam",
                                "name": "resetAfter",
                                "displayString": "Clear event after (hours)",
                                "min": 0,
                                "max": 999
                            },
                            "mmPerCount": {
                                "type": "uiFloatParam",
                                "name": "mmPerCount",
                                "displayString": "mm per tip (mm)",
                                "min": 0.001,
                                "max": 10
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
                            "burstMode": {
                                "type": "uiAction",
                                "name": "burstMode",
                                "displayString": "Burst Mode",
                                "colour": "blue",
                                "requiresConfirm": True
                            },
                            "totalCounts": {
                                "type": "uiVariable",
                                "name": "totalCounts",
                                "displayString": "Raw Counts",
                                "varType": "float",
                                "decPrecision": 0
                            },
                            "lastCounts": {
                                "type": "uiVariable",
                                "name": "lastCounts",
                                "displayString": "Last Counts",
                                "varType": "float",
                                "decPrecision": 0
                            },
                            "lastRain": {
                                "type": "uiVariable",
                                "name": "lastRain",
                                "displayString": "Last mm (mm)",
                                "varType": "float",
                                "decPrecision": 1
                            },
                            "rawBattery": {
                                "type": "uiVariable",
                                "name": "rawBattery",
                                "displayString": "Battery (V)",
                                "varType": "float",
                                "decPrecision": 2
                            },
                            "lastRSSI": {
                                "type": "uiVariable",
                                "name": "lastRSSI",
                                "displayString": "Last RSSI",
                                "varType": "float"
                            },
                            "lastSNR": {
                                "type": "uiVariable",
                                "name": "lastSNR",
                                "displayString": "Last SNR",
                                "varType": "float"
                            },
                            "lastUsedGateway": {
                                "type": "uiVariable",
                                "name": "lastUsedGateway",
                                "displayString": "Lora Gateway",
                                "varType": "text"
                            }
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
        
        ## Get the deployment channel
        ui_state_channel = pd.channel(
            api_client=self.cli.api_client,
            channel_name="ui_state",
            agent_id=self.kwargs['agent_id'],
        )

        ## Get the deployment channel
        ui_cmds_channel = pd.channel(
            api_client=self.cli.api_client,
            channel_name="ui_cmds",
            agent_id=self.kwargs['agent_id'],
        )

        self.compute_output_levels(ui_cmds_channel, ui_state_channel)
        self.update_reported_signal_strengths(ui_cmds_channel, ui_state_channel)

        ui_state_channel.update() ## Update the details stored in the state channel so that warnings are computed from current values
        ui_cmds_channel.update() ## Update the details stored in the state channel so that warnings are computed from current values
        self.assess_warnings(ui_cmds_channel, ui_state_channel)


    def downlink(self):
        ## Run any downlink processing code here
        
        self.send_uplink_interval_if_required()
        self.send_burst_mode_if_required()
        self.reset_rainfall_event_if_required()


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

    def get_current_time(self):
        msg_obj = self.kwargs['msg_obj']
        if msg_obj is not None and 'timestamp' in msg_obj:
            return msg_obj['timestamp']
        return None

    ## Compute output values from raw values
    def compute_output_levels(self, cmds_channel, state_channel):

        state_obj = state_channel.get_aggregate()
        cmds_obj = cmds_channel.get_aggregate()


        ## Accumulate all of the data
        batt_percent = None
        try:
            batt_volts = state_obj['state']['children']['details_submodule']['children']['rawBattery']['currentValue']
            batt_percent = self.batt_volts_to_percent(batt_volts) * 100
        except Exception as e:
            self.add_to_log("Could not get battery raw volts - " + str(e))

        mm_per_count = 0.2
        try:
            mm_per_count = cmds_obj['cmds']['mmPerCount']
        except Exception as e:
            self.add_to_log("Could not get mm per count override - " + str(e))

        total_counts = 0
        try:
            total_counts = state_obj['state']['children']['details_submodule']['children']['totalCounts']['currentValue']
        except Exception as e:
            self.add_to_log("Could not get total raw counts - " + str(e))

        last_counts = 0
        try:
            last_counts = state_obj['state']['children']['details_submodule']['children']['lastCounts']['currentValue']
        except Exception as e:
            self.add_to_log("Could not get last raw counts - " + str(e))

        last_event_total = None
        try:
            last_event_total = state_obj['state']['children']['rainfallEvent']['currentValue']
        except Exception as e:
            self.add_to_log("Could not get last event total - " + str(e))

        event_zero_counts = 0
        try:
            event_zero_counts = cmds_obj['cmds']['eventZeroCounts']
        except Exception as e:
            self.add_to_log("Could not get event counter zero - " + str(e))

        last_non_zero_update = self.get_current_time()
        try:
            last_non_zero_update = cmds_obj['cmds']['lastTimeNonZeroUpdate']
        except Exception as e:
            self.add_to_log("Could not get last non-zero update time - " + str(e))

        reset_event_after = 24
        try:
            reset_event_after = cmds_obj['cmds']['resetAfter']
        except Exception as e:
            self.add_to_log("Could not get reset event after x hours - " + str(e))


        ####  Do the calculations
        last_rain = None
        if last_counts is not None:
            last_rain = last_counts * mm_per_count

        new_last_non_zero_update = last_non_zero_update
        current_time = self.get_current_time()
        if last_counts > 0:
            new_last_non_zero_update = current_time            


        ## Calculate the new event counter zero
        new_event_zero_counts = total_counts
        if event_zero_counts < total_counts: ## The device has restarted - reset the total
            new_event_zero_counts = 0
            if last_event_total is not None and last_event_total != 0:
                last_event_counts = last_event_total / mm_per_count
                new_event_zero_counts = -last_event_counts

        event_rainfall = (total_counts - new_event_zero_counts) * mm_per_count

        notification_msg = None
        if ((new_event_zero_counts < total_counts) and 
            (current_time - new_last_non_zero_update > (reset_event_after * 60 * 60))):
            ## Reset the counter
            new_event_zero_counts = total_counts

            notification_msg = "You've had " + str( round(event_rainfall, 1) ) + "mm"


        ## Assess status icon
        status_icon = None
        if event_rainfall == 0:
            status_icon = "idle"


        ## Make the publications
        cmds_obj = {
            "cmds" : {
                "eventZeroCounts" : new_event_zero_counts,
                "lastTimeNonZeroUpdate" : new_last_non_zero_update
            }
        }
        cmds_channel.publish(
            msg_str=json.dumps(cmds_obj),
        )

        msg_obj = {
            "state" : {
                "statusIcon" : status_icon,
                "children" : {
                    "rainfallEvent" : {
                        "currentValue" : event_rainfall
                    },
                    "batteryLevel" : {
                        "currentValue" : batt_percent
                    },
                    "details_submodule" : {
                        "children" : {
                            "lastRain" : {
                                "currentValue" : last_rain
                            },
                        }
                    }
                }
            }
        }
        state_channel.publish(
            msg_str=json.dumps(msg_obj),
        )

        if notification_msg is not None:
            self.add_to_log("Sending rainfall event complete")
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
            notifications_channel.publish(
                msg_str=notification_msg
            )
            activity_log_channel.publish(json.dumps({
                "activity_log" : {
                    "action_string" : notification_msg
                }
            }))

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
        

    def assess_warnings(self, cmds_channel, state_channel):
        cmds_obj = cmds_channel.get_aggregate()

        battery_alarm = None
        try: battery_alarm = cmds_obj['cmds']['battAlarmLevel']
        except Exception as e: self.add_to_log("Could not get battery alarm")
        
        state_obj = state_channel.get_aggregate()

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

        msg_obj = {
            "state" : {
                "children" : {
                    "battLowWarning": batt_warning,
                }
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


    def update_reported_signal_strengths(self, cmds_channel, state_channel):

        msg_id = channel_id = payload = None
        if 'msg_obj' in self.kwargs and self.kwargs['msg_obj'] is not None:
            msg_id = self.kwargs['msg_obj']['message']
            channel_id = self.kwargs['msg_obj']['channel']
            payload = self.kwargs['msg_obj']['payload']

        if not msg_id:
            self.add_to_log( "No trigger message passed - skipping processing" )
        else:
            
            # trigger_msg = pd.message_log(
            #     api_client=self.cli.api_client,
            #     message_id=msg_id,
            #     channel_id=channel_id,
            # )
            # trigger_msg.update()

            # payload = json.loads( trigger_msg.get_payload() )

            rssi = snr = gateway_id = None
            try:
                rssi = payload['uplink_message']['rx_metadata'][0]['rssi']
                snr = payload['uplink_message']['rx_metadata'][0]['snr']
                gateway_id = payload['uplink_message']['rx_metadata'][0]['gateway_ids']['gateway_id']
            except Exception as e:
                self.add_to_log("Could not extract rssi and snr data")
                pass

            if rssi and snr and gateway_id:
                
                min_rssi = -130
                max_rssi = -50
                signal_strength_percent = int(((rssi - max_rssi) / (max_rssi - min_rssi) + 1) * 100)
                signal_strength_percent = max(signal_strength_percent, 0)
                signal_strength_percent = min(signal_strength_percent, 100)

                msg_obj = {
                    "state" : {
                        "children" : {
                            "signalStrength" : {
                                "currentValue" : signal_strength_percent
                            },
                            "details_submodule" : {
                                "children" : {
                                    "lastRSSI" : {
                                        "currentValue" : rssi
                                    },
                                    "lastSNR" : {
                                        "currentValue" : snr
                                    },
                                    "lastUsedGateway" : {
                                        "currentValue" : gateway_id
                                    }
                                }
                            }
                        }
                    }
                }
                state_channel.publish(
                    msg_str=json.dumps(msg_obj),
                    save_log=False
                )

    
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

            tts_dl_channel = pd.channel(
                api_client=self.cli.api_client,
                agent_id=self.kwargs['agent_id'],
                channel_name="tts_downlinks"
            )
            tts_dl_channel.publish(
                msg_str=json.dumps(msg_obj),
            )


    def reset_rainfall_event_if_required(self):

        trigger_payload = None
        if 'msg_obj' in self.kwargs and self.kwargs['msg_obj'] is not None:
            trigger_payload = self.kwargs['msg_obj']['payload']
        
        clear_rainfall_event = None
        try:
            # start_burst_mode = cmds_obj['cmds']['shouldReboot']
            clear_rainfall_event = trigger_payload['cmds']['resetRainEvent']
        except Exception as e:
            self.add_to_log("Could not get 'resetRainEvent' in cmds object")
            return

        if clear_rainfall_event == True:
            
            ui_state_channel = pd.channel(
                api_client=self.cli.api_client,
                channel_name="ui_state",
                agent_id=self.kwargs['agent_id'],
            )
            state_obj = ui_state_channel.get_aggregate()

            total_counts = 0
            try:
                total_counts = state_obj['state']['children']['details_submodule']['children']['totalCounts']['currentValue']
            except Exception as e:
                self.add_to_log("Could not get total raw counts - " + str(e))


            msg_obj = {
                'cmds' : {
                    'resetRainEvent' : None,
                    'eventZeroCounts' : total_counts
                }
            }

            ui_cmds_channel = self.cli.get_channel(
                channel_name="ui_cmds",
                agent_id=self.kwargs['agent_id']
            )
            ui_cmds_channel.publish(
                msg_str=json.dumps(msg_obj),
            )

            msg_obj = {
                "state" : {
                    "children" : {
                        "rainfallEvent" : {
                            "currentValue" : 0
                        }
                    }
                }
            }
            ui_state_channel.publish(
                msg_str=json.dumps(msg_obj),
            )