/**
   @file api-test.ino
   @author Bernd Giesecke (bernd.giesecke@rakwireless.com)
   @brief Simple example how to use the SX126x-API
   @version 0.1
   @date 2021-09-10
   @copyright Copyright (c) 2021
*/
#include <Arduino.h>
/** Add you required includes after Arduino.h */
#include <Wire.h>

// Debug output set to 0 to disable app debug output
#ifndef MY_DEBUG
#define MY_DEBUG 1
#endif

#ifdef NRF52_SERIES
#if MY_DEBUG > 0
#define MYLOG(tag, ...)                     \
	do                                      \
	{                                       \
		if (tag)                            \
			PRINTF("[%s] ", tag);           \
		PRINTF(__VA_ARGS__);                \
		PRINTF("\n");                       \
		if (g_ble_uart_is_connected)        \
		{                                   \
			g_ble_uart.printf(__VA_ARGS__); \
			g_ble_uart.printf("\n");        \
		}                                   \
	} while (0)
#else
#define MYLOG(...)
#endif
#endif
#ifdef ARDUINO_ARCH_RP2040
#if MY_DEBUG > 0
#define MYLOG(tag, ...)                  \
	do                                   \
	{                                    \
		if (tag)                         \
			Serial.printf("[%s] ", tag); \
		Serial.printf(__VA_ARGS__);      \
		Serial.printf("\n");             \
	} while (0)
#else
#define MYLOG(...)
#endif
#endif

/** Include the WisBlock-API */
#include <WisBlock-API.h> // Click to install library: http://librarymanager/All#WisBlock-API

/** Define the version of your SW */
#define SW_VERSION_1 1 // major version increase on API change / not backwards compatible
#define SW_VERSION_2 0 // minor version increase on API change / backward compatible
#define SW_VERSION_3 0 // patch version increase on bugfix, no affect on API

/**
   Optional hard-coded LoRaWAN credentials for OTAA and ABP.
   It is strongly recommended to avoid duplicated node credentials
   Options to setup credentials are
   - over USB with AT commands
   - over BLE with My nRF52 Toolbox
*/

uint8_t node_device_eui[8] = { {{ dev_eui_msb_array }} };
// uint8_t node_device_eui[8] = {0x00, 0x0D, 0x75, 0xE6, 0x56, 0x4D, 0xC1, 0xF3};

uint8_t node_app_eui[8] = { {{ join_eui_msb_array }} };
// uint8_t node_app_eui[8] = {0x70, 0xB3, 0xD5, 0x7E, 0xD0, 0x02, 0x01, 0xE1};

uint8_t node_app_key[16] = { {{ app_key_msb_array }} };
// uint8_t node_app_key[16] = {0x2B, 0x84, 0xE0, 0xB0, 0x9B, 0x68, 0xE5, 0xCB, 0x42, 0x17, 0x6F, 0xE7, 0x53, 0xDC, 0xEE, 0x79};

// uint8_t node_nws_key[16] = {0x32, 0x3D, 0x15, 0x5A, 0x00, 0x0D, 0xF3, 0x35, 0x30, 0x7A, 0x16, 0xDA, 0x0C, 0x9D, 0xF5, 0x3F};
// uint8_t node_apps_key[16] = {0x3F, 0x6A, 0x66, 0x45, 0x9D, 0x5E, 0xDC, 0xA6, 0x3C, 0xBC, 0x46, 0x19, 0xCD, 0x61, 0xA1, 0x1E};

/** Application function definitions */
void setup_app(void);
bool init_app(void);
void app_event_handler(void);
void ble_data_handler(void) __attribute__((weak));
void lora_data_handler(void);
bool send_periodic_lora_frame(void);


/** Application stuff */
uint32_t burst_mode_sleep_time = 30 * 1000; // 30 seconds
uint32_t burst_mode_counter = 20;

uint32_t default_sleep_time = 10 * 60 * 1000; // 10 minutes
uint32_t sleep_time = burst_mode_sleep_time;


// Battery Voltage
#define PIN_VBAT WB_A0
uint32_t vbat_pin = PIN_VBAT;

#define VBAT_MV_PER_LSB (0.73242188F) // 3.0V ADC range and 12 - bit ADC resolution = 3000mV / 4096
#define VBAT_DIVIDER_COMP (1.73)      // Compensation factor for the VBAT divider, depend on the board

#define REAL_VBAT_MV_PER_LSB (VBAT_DIVIDER_COMP * VBAT_MV_PER_LSB)


/** Set the device name, max length is 10 characters */
char g_ble_dev_name[10] = "RAK-TEST";

/** Flag showing if TX cycle is ongoing */
bool lora_busy = false;

/** Send Fail counter **/
uint8_t send_fail = 0;

/**
   @brief Application specific setup functions
*/
void setup_app(void)
{
	Serial.begin(115200);
	time_t serial_timeout = millis();
	// On nRF52840 the USB serial is not available immediately
	while (!Serial)
	{
		if ((millis() - serial_timeout) < 5000)
		{
			delay(100);
			digitalWrite(LED_GREEN, !digitalRead(LED_GREEN));
		}
		else
		{
			break;
		}
	}
	digitalWrite(LED_GREEN, LOW);

	MYLOG("APP", "Setup WisBlock API Example");

#ifdef NRF52_SERIES
	// Enable BLE
	g_enable_ble = true;
#endif

	// Set firmware version
	api_set_version(SW_VERSION_1, SW_VERSION_2, SW_VERSION_3);

	// Optional
	// Setup LoRaWAN credentials hard coded
	// It is strongly recommended to avoid duplicated node credentials
	// Options to setup credentials are
	// -over USB with AT commands
	// -over BLE with My nRF52 Toolbox

	// Read LoRaWAN settings from flash
	api_read_credentials();
	// Change LoRaWAN settings
	g_lorawan_settings.auto_join = true;							// Flag if node joins automatically after reboot
	g_lorawan_settings.otaa_enabled = true;							// Flag for OTAA or ABP
	memcpy(g_lorawan_settings.node_device_eui, node_device_eui, 8); // OTAA Device EUI MSB
	memcpy(g_lorawan_settings.node_app_eui, node_app_eui, 8);		// OTAA Application EUI MSB
	memcpy(g_lorawan_settings.node_app_key, node_app_key, 16);		// OTAA Application Key MSB
	// memcpy(g_lorawan_settings.node_nws_key, node_nws_key, 16);		// ABP Network Session Key MSB
	// memcpy(g_lorawan_settings.node_apps_key, node_apps_key, 16);	// ABP Application Session key MSB
	g_lorawan_settings.node_dev_addr = 0x26021FB4;					// ABP Device Address MSB
	g_lorawan_settings.send_repeat_time = 120000;					// Send repeat time in milliseconds: 2 * 60 * 1000 => 2 minutes
	g_lorawan_settings.adr_enabled = false;							// Flag for ADR on or off
	g_lorawan_settings.public_network = true;						// Flag for public or private network
	g_lorawan_settings.duty_cycle_enabled = false;					// Flag to enable duty cycle (validity depends on Region)
	g_lorawan_settings.join_trials = 5;								// Number of join retries
	g_lorawan_settings.tx_power = 0;								// TX power 0 .. 15 (validity depends on Region)
	g_lorawan_settings.data_rate = 3;								// Data rate 0 .. 15 (validity depends on Region)
	g_lorawan_settings.lora_class = 0;								// LoRaWAN class 0: A, 2: C, 1: B is not supported
	g_lorawan_settings.subband_channels = 1;						// Subband channel selection 1 .. 9
	g_lorawan_settings.app_port = 2;								// Data port to send data
	g_lorawan_settings.confirmed_msg_enabled = LMH_UNCONFIRMED_MSG; // Flag to enable confirmed messages
	g_lorawan_settings.resetRequest = true;							// Command from BLE to reset device
	g_lorawan_settings.lora_region = LORAMAC_REGION_AS923_3;		// LoRa region
	// Save LoRaWAN settings
	api_set_credentials();
}

/**
   @brief Application specific initializations
   @return true Initialization success
   @return false Initialization failure
*/
bool init_app(void)
{
	MYLOG("APP", "init_app");
	return true;
}

/**
   @brief Application specific event handler
          Requires as minimum the handling of STATUS event
          Here you handle as well your application specific events
*/
void app_event_handler(void)
{
	// Timer triggered event
	if ((g_task_event_type & STATUS) == STATUS)
	{
		g_task_event_type &= N_STATUS;
		MYLOG("APP", "Timer wakeup");

#ifdef NRF52_SERIES
		// If BLE is enabled, restart Advertising
		if (g_enable_ble)
		{
			restart_advertising(15);
		}
#endif
		if (lora_busy)
		{
			MYLOG("APP", "LoRaWAN TX cycle not finished, skip this event");
		}
		else
		{

			// Dummy packet

			uint8_t dummy_packet[] = {0x10, 0x00, 0x00};

			lmh_error_status result = send_lora_packet(dummy_packet, 3);
			switch (result)
			{
			case LMH_SUCCESS:
				MYLOG("APP", "Packet enqueued");
				// Set a flag that TX cycle is running
				lora_busy = true;
				break;
			case LMH_BUSY:
				MYLOG("APP", "LoRa transceiver is busy");
				break;
			case LMH_ERROR:
				MYLOG("APP", "Packet error, too big to send with current DR");
				break;
			}
		}
	}
}

#ifdef NRF52_SERIES
/**
   @brief Handle BLE UART data
*/
void ble_data_handler(void)
{
	if (g_enable_ble)
	{
		/**************************************************************/
		/**************************************************************/
		/// \todo BLE UART data arrived
		/// \todo or forward them to the AT command interpreter
		/// \todo parse them here
		/**************************************************************/
		/**************************************************************/
		if ((g_task_event_type & BLE_DATA) == BLE_DATA)
		{
			MYLOG("AT", "RECEIVED BLE");
			// BLE UART data arrived
			// in this example we forward it to the AT command interpreter
			g_task_event_type &= N_BLE_DATA;

			while (g_ble_uart.available() > 0)
			{
				at_serial_input(uint8_t(g_ble_uart.read()));
				delay(5);
			}
			at_serial_input(uint8_t('\n'));
		}
	}
}
#endif

/**
   @brief Handle received LoRa Data
*/
void lora_data_handler(void)
{
	// LoRa Join finished handling
	if ((g_task_event_type & LORA_JOIN_FIN) == LORA_JOIN_FIN)
	{
		g_task_event_type &= N_LORA_JOIN_FIN;
		if (g_join_result)
		{
			MYLOG("APP", "Successfully joined network");
			send_periodic_lora_frame();
			api_timer_restart(sleep_time);
		}
		else
		{
			MYLOG("APP", "Join network failed");
			/// \todo here join could be restarted.
			lmh_join();
		}
	}

	// LoRa data handling
	if ((g_task_event_type & LORA_DATA) == LORA_DATA)
	{
		/**************************************************************/
		/**************************************************************/
		/// \todo LoRa data arrived
		/// \todo parse them here
		/**************************************************************/
		/**************************************************************/
		g_task_event_type &= N_LORA_DATA;
		MYLOG("APP", "Received package over LoRa");
		char log_buff[g_rx_data_len * 3] = {0};
		uint8_t log_idx = 0;
		for (int idx = 0; idx < g_rx_data_len; idx++)
		{
			sprintf(&log_buff[log_idx], "%02X ", g_rx_lora_data[idx]);
			log_idx += 3;
		}
		lora_busy = false;
		MYLOG("APP", "%s", log_buff);
	}

	// LoRa TX finished handling
	if ((g_task_event_type & LORA_TX_FIN) == LORA_TX_FIN)
	{
		g_task_event_type &= N_LORA_TX_FIN;

		MYLOG("APP", "LPWAN TX cycle %s", g_rx_fin_result ? "finished ACK" : "failed NAK");

		if (!g_rx_fin_result)
		{
			// Increase fail send counter
			send_fail++;

			if (send_fail == 10)
			{
				// Too many failed sendings, reset node and try to rejoin
				delay(100);
				api_reset();
			}
		}

		// Clear the LoRa TX flag
		lora_busy = false;
	}
}


float readVBAT(void)
{
	float raw;

	// Get the raw 12-bit, 0..3000mV ADC value
	analogReadResolution(12);
	raw = analogRead(vbat_pin);
	delay(50);
	analogReadResolution(10);

	return raw * REAL_VBAT_MV_PER_LSB;
}
uint8_t mvToPercent(float mvolts)
{
	if (mvolts < 3300)
		return 0;
	if (mvolts < 3600)
	{
		mvolts -= 3300;
		return mvolts / 30;
	}
	mvolts -= 3600;
	return 10 + (mvolts * 0.15F); // thats mvolts /6.66666666
}


bool send_periodic_lora_frame(void)
{
	if (lmh_join_status_get() != LMH_SET)
	{
		//Not joined, try again later
		MYLOG("APP", "Trying to send lora frame without being joined - try later");
		return false;
	}

  	// Assess the sleep time situation; If the initial startup time has elapsed, then change to long term sleep time
	if (burst_mode_counter == 1){

		sleep_time = default_sleep_time;
		MYLOG("APP", "Switching to long sleep time %i", default_sleep_time);
		api_timer_restart(sleep_time);
	}
	if (burst_mode_counter > 0){
		burst_mode_counter = burst_mode_counter - 1;
		MYLOG("APP", "%i More fast sleeps for startup", burst_mode_counter);
	}
  

	// Battery Voltage
	// Get a raw ADC reading
	analogReference(AR_INTERNAL_3_0);
	delay(50);
	int vbat_mv = readVBAT();
	int vbat_VOLT = (vbat_mv / 10) - 300;

	analogReference(AR_INTERNAL);   //This takes it back to default (3.6V)

	// Convert from raw mv to percentage (based on LIPO chemistry)
	uint8_t vbat_per = mvToPercent(vbat_mv);
	

	// Make a sensor reading
    int sensor_pin = A1;   // select the input pin for the potentiometer
    int mcu_ain_value = 0;  
    int average_value;  
    float voltage_ain;
    float current_sensor; // variable to store the value coming from the sensor

	/* WisBLOCK 5801 Power On*/
	pinMode(WB_IO1, OUTPUT);
	digitalWrite(WB_IO1, HIGH);
	delay(500);
	/* WisBLOCK 5801 Power On*/

	// Take 10 readings, then get the average
    int i;
	for (i = 0; i < 10; i++){ mcu_ain_value += analogRead(sensor_pin); }

    /* WisBLOCK 5801 Power Off*/
  	digitalWrite(WB_IO1, LOW);
    /* WisBLOCK 5801 Power Off*/

    average_value = mcu_ain_value / i;
    voltage_ain = average_value * 3.6 /1024;      //raef 3.6v / 10bit ADC
    current_sensor = voltage_ain / 149.9 * 1000;    //WisBlock RAK5801 I=U/149.9\*1000 (mA)
    int current_sensor_payload = current_sensor * 1000;
    
	MYLOG("APP", "-------Current Sensor------ =  %f\n", current_sensor);
	MYLOG("APP", "--Current Sensor Payload--- =  %d\n", current_sensor_payload);
	MYLOG("APP", "-----Batt Voltage (mV)----- =  %d\n", vbat_mv);
	MYLOG("APP", "------Batt Level (%)------- =  %d\n", vbat_per);
	

	// Compile the lora packet
	uint8_t m_lora_app_data_buffer[64]; // Max 64 bytes long

	uint32_t buffSize = 0;
	m_lora_app_data_buffer[buffSize++] = highByte(current_sensor_payload);
	m_lora_app_data_buffer[buffSize++] = lowByte(current_sensor_payload);
	m_lora_app_data_buffer[buffSize++] = 0; // Reserved for second sensor
	m_lora_app_data_buffer[buffSize++] = vbat_per;
	m_lora_app_data_buffer[buffSize++] = vbat_mv / 20;
	m_lora_app_data_buffer[buffSize++] = highByte(sleep_time / 1000);
	m_lora_app_data_buffer[buffSize++] = lowByte(sleep_time / 1000);
	m_lora_app_data_buffer[buffSize++] = burst_mode_counter;
	
	//  m_lora_app_data_buffer[buffSize++] = 'l';
	//  m_lora_app_data_buffer[buffSize++] = 'o';

	lmh_app_data_t m_lora_app_data = {m_lora_app_data_buffer, 0, 0, 0, 0};
	m_lora_app_data.buffsize = buffSize;

	lmh_error_status error = lmh_send(&m_lora_app_data, LMH_UNCONFIRMED_MSG);

	MYLOG("APP", "Packet Sent");
	return (error == 0);
}
