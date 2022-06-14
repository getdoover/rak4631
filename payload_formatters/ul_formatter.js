// For more information visit the TTS Documentation
// https://www.thethingsindustries.com/docs/integrations/payload-formatters/javascript/uplink-decoder/

// This function takes the raw bytes from the device's uplink message
// And converts it to JSON

function decodeUplink(input) {

    // Input object has the following structure :
    // {
    //     "bytes": [1, 2, 3],
    //     "fPort": 1
    // }

    var data = {};

    data.current_reading = (input.bytes[0] << 8 | input.bytes[1]) / 1000;
    // data.current_reading_2 = (input.bytes[2] << 8 | input.bytes[3]) / 1000;
    data.batt_mvolts = input.bytes[4] * 20
    data.sleep_time = (input.bytes[5] << 8 | input.bytes[6]);
    data.fast_rate_counter = input.bytes[7];
    data.batt_percent = input.bytes[3]

    data.batt_volts = data.batt_mvolts / 1000

    var fast_rate_warning = null;
    var fast_rate_reset_command = null;

    if (data.fast_rate_counter > 0){

        // If fast rate is detected, then reset any action that triggered it
        fast_rate_reset_command = {
            "cmds" : {
                "burstMode" : null
            }
        }

        let secs_remaining = data.sleep_time * data.fast_rate_counter;

        let message = "Message burst will finish in " + secs_remaining + " secs"

        let mins_remaining = Math.floor(secs_remaining / 60);
        let secs_modulus = (secs_remaining % 60);
        if (mins_remaining > 1){
            if (secs_modulus > 0){
                message = "Message burst will finish in " + mins_remaining + " mins, " + (secs_remaining % 60) + " secs"
            } else {
                message = "Message burst will finish in " + mins_remaining + " mins"
            }
        } else if (mins_remaining == 1){
            if (secs_modulus > 0){
                message = "Message burst will finish in " + mins_remaining + " min, " + (secs_remaining % 60) + " secs"
            } else {
                message = "Message burst will finish in " + mins_remaining + " min"
            }
        }
        
        fast_rate_warning = {
            type: "uiWarningIndicator",
            name: "highRateWarning",
            displayString: message
        }
    }

    data.doover_channels = {
        ui_state : {
            state : {
                children : {
                    // batteryLevel : {
                    //     currentValue : data.batt_percent
                    // },
                    details_submodule : {
                        children : {
                            rawlevel : {
                                currentValue : data.current_reading
                            },
                            rawBattery : {
                                currentValue : data.batt_volts
                            }
                        }
                    },
                    node_connection_info: {
                        connectionPeriod: data.sleep_time,
                        nextConnection: data.sleep_time
                    },
                    highRateWarning: fast_rate_warning
                }
            }
        }
    }

    if (fast_rate_reset_command !== null){
        data.doover_channels.ui_cmds = fast_rate_reset_command
    }

    return {
        data: data
    };

}