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
#define MY_DEBUG 0
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

const char CLIENT_ID[] = "{{ client_id }}";
// const char CLIENT_ID[] = "9d1ba06a-6400-42f2-a708-39b83b32a458";

const char ENDPOINT[] = "{{ endpoint }}";
// const char ENDPOINT[] = "a1zgnxur10j8ux.iot.us-east-1.amazonaws.com";
const int ENDPOINT_PORT = {{ endpoint_port }};
// const int ENDPOINT_PORT = 8883;

const char DL_TOPIC[] = "{{ downlink_topic }}";
// const char DL_TOPIC[] = "$aws/things/MQTT-1/shadow/update/accepted";
const char UL_TOPIC[] = "{{ uplink_topic }}";
// const char UL_TOPIC[] = "$aws/things/MQTT-1/shadow/update/accepted";

// const char CA_CERT[] = R"EOF(
// {{ ca_cert }}
// )EOF";
const char CA_CERT[] = R"EOF(
-----BEGIN CERTIFICATE-----
MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6
b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL
MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv
b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj
ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM
9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw
IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6
VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L
93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm
jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC
AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA
A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI
U5PMCCjjmCXPI6T53iHTfIUJrU6adTrCC2qJeHZERxhlbI1Bjjt/msv0tadQ1wUs
N+gDS63pYaACbvXy8MWy7Vu33PqUXHeeE6V/Uq2V8viTO96LXFvKWlJbYK8U90vv
o/ufQJVtMVT8QtPHRh8jrdkPSHCa2XV4cdFyQzR1bldZwgJcJmApzyMZFo6IQ6XU
5MsI+yMRQ+hDKXJioaldXgjUkK642M4UwtBV8ob2xJNDd2ZhwLnoQdeXeGADbkpy
rqXRfboQnoZsG4q5WTP468SQvvG5
-----END CERTIFICATE-----

)EOF";

const char DEVICE_CERT[] = R"EOF(
{{ device_cert }}
)EOF";

const char PRIV_KEY[] = R"EOF(
{{ priv_key }}
)EOF";

#define BG77_POWER_KEY WB_IO1
#define BG77_GPS_ENABLE WB_IO2

#define ULTRASONIC_PWR_ON WB_IO2


/** Application function definitions */
void setup_app(void);
bool init_app(void);
void app_event_handler(void);
void ble_data_handler(void) __attribute__((weak));
void lora_data_handler(void);
// bool send_periodic_lora_frame(void);

float read_uart_sensor(void);

void send_periodic_mqtt_message(void);
void wake_modem(void);
void configure_modem(void);
void configure_modem_certs(void);
void wait_for_modem_connect(void);
String exchange_data(char* message);
void sleep_modem(void);

String bg77_at(const char *at, uint16_t timeout);


/** Application stuff */
uint32_t burst_mode_sleep_time = 90 * 1000; // 60 seconds
uint32_t burst_mode_counter = 5;

uint32_t default_sleep_time = 30 * 60 * 1000; // 30 minutes
uint32_t sleep_time = burst_mode_sleep_time;


// Battery Voltage
#define PIN_VBAT WB_A0
uint32_t batt_volts_pin = PIN_VBAT;

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

  MYLOG("APP", "Setup Doover RAK4631 Node");

#ifdef NRF52_SERIES
  // Enable BLE
    g_enable_ble = false;
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
  g_lorawan_settings.auto_join = true;             // Flag if node joins automatically after reboot
   g_lorawan_settings.otaa_enabled = true;              // Flag for OTAA or ABP
//   memcpy(g_lorawan_settings.node_device_eui, node_device_eui, 8); // OTAA Device EUI MSB
//   memcpy(g_lorawan_settings.node_app_eui, node_app_eui, 8);    // OTAA Application EUI MSB
//   memcpy(g_lorawan_settings.node_app_key, node_app_key, 16);   // OTAA Application Key MSB
   // memcpy(g_lorawan_settings.node_nws_key, node_nws_key, 16);    // ABP Network Session Key MSB
   // memcpy(g_lorawan_settings.node_apps_key, node_apps_key, 16);  // ABP Application Session key MSB
   // g_lorawan_settings.node_dev_addr = 0x26021FB4;          // ABP Device Address MSB
   g_lorawan_settings.send_repeat_time = default_sleep_time;          // Send repeat time in milliseconds: 2 * 60 * 1000 => 2 minutes
   g_lorawan_settings.adr_enabled = true;             // Flag for ADR on or off
   g_lorawan_settings.public_network = true;            // Flag for public or private network
   g_lorawan_settings.duty_cycle_enabled = false;         // Flag to enable duty cycle (validity depends on Region)
//   g_lorawan_settings.join_trials = 5;                // Number of join retries
   g_lorawan_settings.join_trials = 0;                // Number of join retries
   g_lorawan_settings.tx_power = 22;                // TX power 0 .. 15 (validity depends on Region)
   g_lorawan_settings.data_rate = 3;                // Data rate 0 .. 15 (validity depends on Region)
   g_lorawan_settings.lora_class = 0;               // LoRaWAN class 0: A, 2: C, 1: B is not supported
   g_lorawan_settings.subband_channels = 2;           // Subband channel selection 1 .. 9
   // g_lorawan_settings.app_port = 2;                // Data port to send data
   g_lorawan_settings.confirmed_msg_enabled = LMH_UNCONFIRMED_MSG; // Flag to enable confirmed messages
   g_lorawan_settings.resetRequest = true;              // Command from BLE to reset device
   g_lorawan_settings.lora_region = LORAMAC_REGION_AU915;   // LoRa region
   // Save LoRaWAN settings
  api_set_credentials();


  pinMode(BG77_POWER_KEY, OUTPUT);
  pinMode(ULTRASONIC_PWR_ON, OUTPUT);
  digitalWrite(ULTRASONIC_PWR_ON, LOW); // Turn Power to sensor off

}

/**
   @brief Application specific initializations
   @return true Initialization success
   @return false Initialization failure
*/
bool init_app(void)
{
  MYLOG("APP", "init_app");
  api_timer_init();
  api_timer_restart(sleep_time);
  send_periodic_mqtt_message();
  MYLOG("APP", "init_app complete");
  return true;
}

/**
   @brief Application specific event handler
          Requires as minimum the handling of STATUS event
          Here you handle as well your application specific events
*/
void app_event_handler(void)
{
  MYLOG("APP", "app_event_handler called");
  
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
    // if (lora_busy)
    // {
    //  MYLOG("APP", "LoRaWAN TX cycle not finished, skip this event");
    // }
    // else
    // {
    //  send_periodic_lora_frame();
    // }
    send_periodic_mqtt_message();
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
  MYLOG("APP", "lora_data_handler called");
}
// void lora_data_handler(void)
// {
//  // LoRa Join finished handling
//  if ((g_task_event_type & LORA_JOIN_FIN) == LORA_JOIN_FIN)
//  {
//    g_task_event_type &= N_LORA_JOIN_FIN;
//    if (g_join_result)
//    {
//      MYLOG("APP", "Successfully joined network");
//      send_periodic_lora_frame();
//      api_timer_restart(sleep_time);
//    }
//    else
//    {
//      MYLOG("APP", "Join network failed");
//      /// \todo here join could be restarted.
//      lmh_join();
//    }
//  }

//  // LoRa data handling
//  if ((g_task_event_type & LORA_DATA) == LORA_DATA)
//  {
//    /**************************************************************/
//    /**************************************************************/
//    /// \todo LoRa data arrived
//    /// \todo parse them here
//    /**************************************************************/
//    /**************************************************************/
//    g_task_event_type &= N_LORA_DATA;
//    MYLOG("APP", "Received package over LoRa");
    
//    char log_buff[g_rx_data_len * 3] = {0};
//    uint8_t log_idx = 0;
//    for (int idx = 0; idx < g_rx_data_len; idx++)
//    {
//      sprintf(&log_buff[log_idx], "%02X ", g_rx_lora_data[idx]);
//      log_idx += 3;
//    }
//    MYLOG("APP", "Message : %s", log_buff);
//    lora_busy = false;
    
//    if (g_rx_data_len == 2){
//      // This is a burst mode message
//      MYLOG("APP", "Recieved a new burst mode message");

//      uint32_t new_counter = g_rx_lora_data[0] << 8;
//      new_counter |= g_rx_lora_data[1];

//      burst_mode_counter = new_counter;
//      sleep_time = burst_mode_sleep_time;

//      // After setting a new burst mode counter time, send a new packet to update the reported sleep interval  
//      send_periodic_lora_frame();
//      api_timer_restart(sleep_time);
//    }
//    else {

//      // Assuming the new time is encoded as 3 bytes. e.g. 30=> 0x00, 0x00, 0x1F
//      // Downlink must be sent on Port2
//      // Downlink is in seconds
//      uint32_t new_time = g_rx_lora_data[0] << 16;
//      new_time |= g_rx_lora_data[1] << 8;
//      new_time |= g_rx_lora_data[2];
      
//      sleep_time = new_time * 1000;
//      default_sleep_time = sleep_time; // Set the default long sleep time to this as well, so it will revert to this again after burst mode
      
//      MYLOG("APP", "New uplink time set %i", new_time);
  
//      // If a new sleep time is set manually, then forget about the init fast counter
//      burst_mode_counter = 0;
  
//      // After setting a new sleep time, send a new packet to update the reported sleep interval
//      send_periodic_lora_frame();
//      api_timer_restart(sleep_time);
//    }

//  }

//  // LoRa TX finished handling
//  if ((g_task_event_type & LORA_TX_FIN) == LORA_TX_FIN)
//  {
//    g_task_event_type &= N_LORA_TX_FIN;

//    MYLOG("APP", "LPWAN TX cycle %s", g_rx_fin_result ? "finished ACK" : "failed NAK");

//    if (!g_rx_fin_result)
//    {
//      // Increase fail send counter
//      send_fail++;

//      if (send_fail == 10)
//      {
//        // Too many failed sendings, reset node and try to rejoin
//        delay(100);
//        api_reset();
//      }
//    }

//    // Clear the LoRa TX flag
//    lora_busy = false;
//  }
// }


float readVBAT(void)
{
  float raw;

  // Get the raw 12-bit, 0..3000mV ADC value
  analogReadResolution(12);
  raw = analogRead(batt_volts_pin);
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


void send_periodic_mqtt_message(void)
{
    // Assess the sleep time situation; If the initial startup time has elapsed, then change to long term sleep time
  if (burst_mode_counter == 1){

    sleep_time = default_sleep_time;
    MYLOG("APP", "Switching to long sleep time %i", default_sleep_time);
    api_timer_restart(sleep_time);
  }
  if (burst_mode_counter > 0){
    burst_mode_counter = burst_mode_counter - 1;
    MYLOG("APP", "%i more messages in burst mode", burst_mode_counter);
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
    float sensor_reading = read_uart_sensor();

  // Report data to serial
  MYLOG("APP", "-------Level Sensor (cm)------ =  %f", sensor_reading);
  MYLOG("APP", "-----Batt Voltage (mV)----- =  %d", vbat_mv);
  MYLOG("APP", "------Batt Level (Percent)------- =  %d", vbat_per);
  
  // Compile the mqtt packet
  char msg_buf[60];
  sprintf(msg_buf, "{\"level_cm\": %f, \"batt_mvolts\": %d, \"uplink_interval_secs\": %d}", sensor_reading, vbat_mv, (sleep_time/1000));
//   char test_message[] = "{\"is_working\": true}";

  // Send data
  wake_modem();
  configure_modem();
  configure_modem_certs();
  wait_for_modem_connect();
  String recv_data = exchange_data(msg_buf);
  sleep_modem();

  MYLOG("APP", "Packet Sent");
}



void wake_modem()
{

  //BG77 init , Check if the modem is already awake
  time_t timeout = millis();
  bool moduleSleeps = true;
  
  Serial1.flush();
  // Serial Used for NBIoT Comms
  Serial1.begin(115200);
  delay(100);
  while (Serial1.available()) Serial1.read();
  
  Serial1.println("ATI");
  //BG77 init
  while ((millis() - timeout) < 1000)
  {
    if (Serial1.available())
    {
    String result = Serial1.readString();
//    Serial.println();
    MYLOG("APP", "Modem already awake");
//    Serial.println(result);
    moduleSleeps = false;
    }
  }
  if (moduleSleeps)
  {
    // Module slept, wake it up
    MYLOG("APP", "Waking Modem Up");
//    pinMode(BG77_POWER_KEY, OUTPUT);
    digitalWrite(BG77_POWER_KEY, 0);
    delay(100);
    digitalWrite(BG77_POWER_KEY, 1);
    delay(1000);
    digitalWrite(BG77_POWER_KEY, 0);
    delay(100);
  }
  MYLOG("APP", "BG77 power up");

  // Wait for modem 'RDY'
  delay(1500);

  //active and join to the net, this part may depend on some information of your operator.
  bg77_at("AT+CFUN=1,0", 100);
  
  bg77_at("AT+CGDCONT=1,\"IP\",\"telstra.iph\",\"0.0.0.0\",0,0", 100);
  bg77_at("AT+QIACT=1", 100);

}

void wait_for_modem_connect(){
  
  // Wait for modem to connect, or maximum of 15 seconds
  String resp = "";
  bool is_connected = false;
  
  time_t lte_connect_timeout = millis();
  while ((!is_connected) && ((millis() - lte_connect_timeout) < 15000))
  {
    resp = bg77_at("AT+CSQ", 100);
    // If resp contains Ok, but does not contain 99,99, then connected
    // if ((resp.indexOf("99,99") == -1) && (resp.indexOf("OK") != -1)){
    if ((resp.length() > 5) && (resp.indexOf("99,99") == -1)){
    is_connected = true;
//    Serial.println("Connected");
    MYLOG("APP", "Modem connected to internet");
    }
    delay(250);
  }
  
//  bg77_at("AT+CGDCONT=1,\"IP\",\"telstra.iph\",\"0.0.0.0\",0,0", 100);
//  bg77_at("AT+QIACT=1", 3000);

}

void sleep_modem()
{
  bool moduleSleeps = true;

  //  Serial1.flush();
  while (Serial1.available()) Serial1.read();
  
  Serial1.println("ATI");
  //BG77 init
  time_t timeout = millis();
  while ((millis() - timeout) < 1000)
  {
    if (Serial1.available())
    {
    String result = Serial1.readString();
    MYLOG("APP", "Modem awake");
    moduleSleeps = false;
    }
  }

  Serial1.end();
  if (!moduleSleeps)
  {
    MYLOG("APP", "Putting modem to sleep");
    // Module slept, wake it up
//    pinMode(BG77_POWER_KEY, OUTPUT);
    digitalWrite(BG77_POWER_KEY, 0);
    delay(100);
    digitalWrite(BG77_POWER_KEY, 1);
    delay(1000);
    digitalWrite(BG77_POWER_KEY, 0);
    delay(100);
  }
  MYLOG("APP", "BG77 powered down");
}


//void parse_gps()
//{
//  int index1 = gps_data.indexOf(',');
//
//  if (strstr(gps_data.c_str(), "E") != NULL)
//  {
//    int index2 = gps_data.indexOf('E');
//    gps_data = gps_data.substring(index1 + 1, index2 + 1);
//  }
//  if (strstr(gps_data.c_str(), "W") != NULL)
//  {
//    int index3 = gps_data.indexOf('W');
//    gps_data = gps_data.substring(index1 + 1, index3 + 1);
//  }
//
//}
//
//
//void get_gps()
//{
//  int gps_count = 300;
//  int timeout = 1000;
//  while (gps_count--)
//  {
//    Serial1.write("AT+QGPSLOC?\r");
//    timeout = 1000;
//    while (timeout--)
//    {
//      if (Serial1.available())
//      {
//        gps_data += char(Serial1.read());
//      }
//      delay(1);
//    }
//    if (strstr(gps_data.c_str(), "CME ERROR") != NULL)
//    {
//      gps_data = "";
//      continue;
//    }
//    if (strstr(gps_data.c_str(), "E") != NULL || strstr(gps_data.c_str(), "W") != NULL)
//    {
//      Serial.println(gps_data);
//      parse_gps();
//      break;
//    }
//  }
//}


//this function is suitable for most AT commands of bg96. e.g. bg96_at("ATI")
String bg77_at(const char *at, uint16_t timeout)
{
  String bg77_rsp = "";
  char tmp[2048] = {0};
  int len = strlen(at);
  strncpy(tmp, at, len);
  uint16_t t = timeout;
  tmp[len] = '\r';

//  Serial.write(tmp);
//  Serial.write("\n");

  Serial1.write(tmp);
  delay(25);
  while (t--)
  {
    if (Serial1.available())
    {
    bg77_rsp += char(Serial1.read());
    }
    delay(1);
  }
  bg77_rsp.trim(); // Remove unnecessary whitespace
//  Serial.println(bg77_rsp);
  char buf[128];
  bg77_rsp.toCharArray(buf, 128);
  MYLOG("APP", buf);

//  bg77_rsp.toCharArray(tmp, 2048);
//  MYLOG("APP", tmp);
//  delay(50);
  
  return bg77_rsp;
}


void configure_modem()
{

  //https://www.quectel.com/wp-content/uploads/2021/03/Quectel_BG95BG77BG600L_Series_MQTT_Application_Note_V1.1-1.pdf

//  // DNS Config
//  bg77_at("AT+QIDNSCFG=1,\"8.8.8.8\",\"8.8.4.4\"", 100); //Set DNS Server.

  // MQTT Config
  bg77_at("AT+QMTCFG=\"pdpcid\",1", 100); //Set MQTT client to use PDP context 1.
  bg77_at("AT+QMTCFG=\"ssl\",0,1,2", 100); //Set SSL context ID as 1.
//  bg77_at("AT+QMTCFG=\"ssl\",0,1,1", 100); //Set SSL context ID as 1.
  bg77_at("AT+QSSLCFG=\"seclevel\",2,2", 100); //SSL authentication mode: server and client authentication
  bg77_at("AT+QSSLCFG=\"sslversion\",2,4", 100); //Set SSL version
  //  bg77_at("AT+QSSLCFG=\"ciphersuite\",2,0XFFFF", 100); //Set SSL cipher suite
  bg77_at("AT+QSSLCFG=\"ignorelocaltime\",2,1", 100); //Ignore the time of authentication
}

void configure_modem_certs()
{
  char buf[50];
  
  bg77_at("AT+QFDEL=\"cacert.pem\"", 100);
  sprintf(buf, "AT+QFUPL=\"cacert.pem\",%d,100", sizeof(CA_CERT));
  bg77_at(buf, 100);
  // "CONNECT"
  bg77_at(CA_CERT, 500);
  bg77_at("AT+QSSLCFG=\"cacert\",2,\"cacert.pem\"", 100);

  // Upload Client Cert File ".pem"
  bg77_at("AT+QFDEL=\"client.pem\"", 100);
  sprintf(buf, "AT+QFUPL=\"client.pem\",%d,100", sizeof(DEVICE_CERT));
  bg77_at(buf, 100);
  // "CONNECT"
  bg77_at(DEVICE_CERT, 500);
  bg77_at("AT+QSSLCFG=\"clientcert\",2,\"client.pem\"", 100);

  // Upload Client Private Key ".pem"
  bg77_at("AT+QFDEL=\"user_key.pem\"", 100);
  sprintf(buf, "AT+QFUPL=\"user_key.pem\",%d,100", sizeof(PRIV_KEY));
  bg77_at(buf, 100);
  // "CONNECT"
  bg77_at(PRIV_KEY, 500);
  bg77_at("AT+QSSLCFG=\"clientkey\",2,\"user_key.pem\"", 100);
}

String exchange_data(char* message)
{
  // https://www.quectel.com/wp-content/uploads/2021/03/Quectel_BG95BG77BG600L_Series_MQTT_Application_Note_V1.1-1.pdf

  char buf[128];

  sprintf(buf, "AT+QMTOPEN=0,\"%s\",%d", ENDPOINT, ENDPOINT_PORT);
  bg77_at(buf, 5000);
  
  sprintf(buf, "AT+QMTCONN=0,\"%s\"", CLIENT_ID);  
  bg77_at(buf, 3000);

  // Subscribe to topic
  sprintf(buf, "AT+QMTSUB=0,1,\"%s\",1", DL_TOPIC);
  bg77_at(buf, 3000);
  // AT+QMTSUB=<client_idx>,<msgID>,<topic1>,<qos1>[,<topic2>,<qos2>…]

  //If a client subscribes to a topic named “$aws/things/MQTT-1/shadow/update/accepted” and other
  //  devices publish the same topic to the server, the module will report the following information.
  //  +QMTRECV: 0,1,"$aws/things/MQTT-1/shadow/update/accepted","This is publish data from client"

  // Publish to topic
//  sprintf(buf, "AT+QMTPUB=0,1,1,0,\"%s\",%d", UL_TOPIC, strlen(message));
  sprintf(buf, "AT+QMTPUB=0,0,0,0,\"%s\",%d", UL_TOPIC, strlen(message));
  // AT+QMTPUB=<client_idx>,<msgID>,<qos>,<retain>,<topic>,<msglen>
  bg77_at(buf, 200);
  bg77_at(message, 5000);

  // Disconnect from the MQTT Server
  bg77_at("AT+QMTDISC=0", 500);

  return "";
}

float read_uart_sensor()
{
  unsigned char data[4]={};
  float distance;
  int num_measurements = 10;

  // Reopen Serial1 on a new baud rate
  //  Serial1.end();
  Serial1.flush();
  Serial1.begin(9600);
  while (Serial1.available()) Serial1.read();

  digitalWrite(ULTRASONIC_PWR_ON, HIGH); // Turn Power to sensor on
  delay(1200);

  while (Serial1.available()) Serial1.read();

  float measurements[num_measurements] = {};
  // Serial.print("Measurements = ");
  
  for (int m=0;m<num_measurements;m++){

    delay(100);

    // Read measurement from sensor
    do{
    for(int i=0;i<4;i++)
    {
      data[i]=Serial1.read();
    }
    }while(Serial1.read()==0xff);
  
    Serial1.flush();
  
    if(data[0]==0xff)
    {
      int sum;
      sum=(data[0]+data[1]+data[2])&0x00FF;
      if(sum==data[3])
      {
      distance=(data[1]<<8)+data[2];
      if(distance>280)
        {
        measurements[m] = (distance/10);
        }else 
          {
            // Serial.println("Below the lower limit");  
            measurements[m] = 0;      
          }
      }
      else
      {
        // Serial.println("ERROR");
        measurements[m] = -1;
      }
    }
    // Serial.print(measurements[m]);
    // Serial.print(", ");
  }
  // Serial.println(";");
  
  Serial1.end();
  digitalWrite(ULTRASONIC_PWR_ON, LOW); // Turn Power to sensor off

  float sum = 0;
  int measurements_counter = 0;
  for (int i=0 ; i<num_measurements; i++) { 
    if (measurements[i] > 0)
	{
		sum += measurements[i];
		measurements_counter++;
	}
  }
  float result = 0;
  if (measurements_counter > 0)
  {
  	result = ((float) sum) / measurements_counter;  // average will be fractional, so float may be appropriate.
  }

  // Display result as string
  char sz[20] = {' '};
  int val_int = (int) result;  // compute the integer part of the float
  float val_float = (abs(result) - abs(val_int)) * 100000;
  int val_fra = (int)val_float;
  sprintf (sz, "%d.%d", val_int, val_fra); //
  MYLOG("APP", sz);
  return result;
}