// For more information visit the TTS Documentation
// https://www.thethingsindustries.com/docs/integrations/payload-formatters/javascript/downlink-encoder/

// This function takes a JSON message that is scheduled for downlink to the device,
// And converts it to bytes to send to the device over lora

function encodeDownlink(input) {

    if (('burst_mode' in input.data) && (input.data.burst_mode == true)){
        return {
            bytes: [0, 10],
            fPort: 2
        }
    }

    if ('uplink_interval_secs' in input.data){
        var uplink_secs = input.data.uplink_interval_secs

        // we want to represent the input as a 8-bytes array
        var secsByte1 = 0
        var secsByte2 = 0
        var secsByte3 = 0
        
        secsByte1 = uplink_secs & 0xff
        uplink_secs = (uplink_secs - secsByte1) / 256

        secsByte2 = uplink_secs & 0xff
        uplink_secs = (uplink_secs - secsByte2) / 256

        secsByte3 = uplink_secs & 0xff
        uplink_secs = (uplink_secs - secsByte3) / 256

        return {
            // bytes: [1, secsByte3, secsByte2, secsByte1],
            bytes: [secsByte3, secsByte2, secsByte1],
            fPort: 2
        }
    }

}




// For more information visit the TTS Documentation
// https://www.thethingsindustries.com/docs/integrations/payload-formatters/javascript/downlink-decoder/

// This function takes the raw bytes from a downlink message
// And converts it to JSON

function decodeDownlink(input) {

    // Input object has the following structure :
    // {
    //     "bytes": [1, 2, 3],
    //     "fPort": 1
    // }
    
    var mode=(input.bytes[0]);

	switch (mode) {
	
        case 01:

            return {
                data : {
                    "uplinkIntervalSecs" : null
                }
            }
            break;
            
        case 04:
            return {
                data : {
                    "burstMode" : null
                }
            }
            break;
        
        default:
            return {
                errors: ["unknown downlink"]
            }
        }
}