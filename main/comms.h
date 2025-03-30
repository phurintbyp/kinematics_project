#ifndef COMMS_H
#define COMMS_H

#include <Arduino.h>

String readSerialCommand();
void processCommand(String command);

#endif
