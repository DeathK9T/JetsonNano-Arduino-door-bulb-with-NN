#define motorPwm 2
#define forward 3
#define backward 4
#define bulb 7

byte buff = 0;

bool df = false,
     bf = false;

void openDoor()
{
  digitalWrite(motorPwm, HIGH);
  digitalWrite(forward, LOW);
  digitalWrite(backward, HIGH);
  delay(4550);
  digitalWrite(motorPwm, LOW);
  digitalWrite(forward, LOW);
  digitalWrite(backward, LOW);
  df = true;
}

void closeDoor()
{
  digitalWrite(motorPwm, HIGH);
  digitalWrite(forward, HIGH);
  digitalWrite(backward, LOW);
  delay(4750);
  digitalWrite(motorPwm, LOW);
  digitalWrite(forward, LOW);
  digitalWrite(backward, LOW);
  df = false;
}

void turnOn()
{
  digitalWrite(bulb, HIGH);
  bf = true;
}

void turnOff()
{
  digitalWrite(bulb, LOW);
  bf = false;
}

void blinkLed()
{
  digitalWrite(13, HIGH);
  delay(100);
  digitalWrite(13, LOW);
  delay(100);
  digitalWrite(13, HIGH);
}

void setup() {
  pinMode(13, OUTPUT);

  Serial.begin(2000000);
  pinMode(bulb, OUTPUT);
  pinMode(motorPwm, OUTPUT);
  pinMode(forward, OUTPUT);
  pinMode(backward, OUTPUT);
}

void loop() {
  if(Serial.available() > 0)
  {
    buff = Serial.read();
    if(buff & 128)
    {
      if((buff & 1) && !df)
      {
        blinkLed();
        //openDoor();
      }
      else if(!(buff & 1) && df)
      {
        blinkLed();
        //closeDoor();
      }
    }
    else
    {
      if((buff & 1) && !bf)
      {
        turnOn();
      }
      else if(!(buff & 1) && bf)
      {
        turnOff();
      }
    }
    Serial.print(buff, BIN);
  }
}
