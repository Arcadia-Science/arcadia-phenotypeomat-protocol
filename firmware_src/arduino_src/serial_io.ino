//A simple system for passing variable values to and from the arduino.
//The function serialEvent watches the serial connection for for ascii characters
//and adds those characters to a buffer.  When it recieves a semicolon it considers
//the buffer to contain a command. It can handle the commands GET and SET to allow 
//passing variables from the computer to the arduino

void serialEvent() {
  // concatinate incoming characters from the serial port  
  while (Serial.available() > 0) {
    char c = Serial.read();
    // Add any characters that aren't the end of a command (semicolon) to the input buffer.
    if (c != ';') {
      c = toupper(c);
      strncat(commandBuffer, &c, 1);
    }
    else
    {
      // Parse the command because an end of command token was encountered.
      Serial.println(commandBuffer);
      parseCommand(commandBuffer);


      // Clear the input buffer
      memset(commandBuffer, 0, sizeof(commandBuffer));
    }
  }
}


#define GET_AND_SET(variableName) \
  if (strstr(command, "GET " #variableName) != NULL) { \
    Serial.print(#variableName" "); \
    Serial.println(variableName); \
  } \
  else if (strstr(command, "SET " #variableName " ") != NULL) { \
    variableName = (typeof(variableName)) atof(command+(sizeof("SET " #variableName " ")-1)); \
    Serial.print(#variableName" "); \
    Serial.println(variableName); \
  }

void parseCommand(char* command) {
  
  GET_AND_SET(LED_460_STATUS);
  GET_AND_SET(LED_535_STATUS);
  GET_AND_SET(LED_590_STATUS);
  GET_AND_SET(LED_670_STATUS);
  GET_AND_SET(LED_TRANS_STATUS);
}
