/*initializes variables before running setup*/

const int led_pin_460 = 11; //pin that 460nm(blue) leds are connected to
const int led_pin_trans = 13; //pin that the transillumination leds are connected to
const int led_pin_535 = 9; //pin that 535nm (green) leds are connected to
const int led_pin_590 = 12; //pin that 590nm (yellow) leds are connected to
const int led_pin_670 = 10; //pin that 670nm (red) leds are connected to

const int MAX_CHRS = 30; //maximum number of characters to us during serial comms.
char commandBuffer[MAX_CHRS]; //initialize the command buffer
int LED_TRANS_STATUS = 1; //initialze a variable for trans light status
int LED_460_STATUS = 1; //initialze a variable for 460 light status
int LED_535_STATUS = 1; //initialze a variable for 535 light status
int LED_590_STATUS = 1; //initialze a variable for 590 light status
int LED_670_STATUS = 1; //initialze a variable for 670 light status


void setup() {
  // initialize serial communication
  Serial.begin(9600);
  // initialize output led pins
  pinMode(led_pin_460, OUTPUT);
  pinMode(led_pin_trans, OUTPUT);
  pinMode(led_pin_535, OUTPUT);
  pinMode(led_pin_590, OUTPUT);
  pinMode(led_pin_670, OUTPUT);
}

void loop() {
  if (LED_460_STATUS==0) {
    digitalWrite(led_pin_460, HIGH);
  }  
  if (LED_460_STATUS==1) {
    digitalWrite(led_pin_460, LOW);
  }
  
  if (LED_TRANS_STATUS==0) {
    digitalWrite(led_pin_trans, HIGH);
  }  
  if (LED_TRANS_STATUS==1) {
    digitalWrite(led_pin_trans, LOW);
  }
  
  if (LED_535_STATUS==0) {
    digitalWrite(led_pin_535, HIGH);
  }  
  if (LED_535_STATUS==1) {
    digitalWrite(led_pin_535, LOW);
  }

  if (LED_590_STATUS==0) {
    digitalWrite(led_pin_590, HIGH);
  }  
  if (LED_590_STATUS==1) {
    digitalWrite(led_pin_590, LOW);
  }

  if (LED_670_STATUS==0) {
    digitalWrite(led_pin_670, HIGH);
  }  
  if (LED_670_STATUS==1) {
    digitalWrite(led_pin_670, LOW);
  }
}
