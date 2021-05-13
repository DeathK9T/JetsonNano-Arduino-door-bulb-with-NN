#define motorPwm 3
#define forward 2
#define backward 4
#define encA 5
#define encB 6
#define bulb 7

/*int curEnc = 0;
bool curA = false,
     curB = false,
     oldA = false;*/

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
  //pinMode(encA, INPUT);
  //pinMode(encB, INPUT);
}

void loop() {
  /*if(digitalRead(encA) == HIGH)
    curA = true;
  else
    curA = false;
  if(digitalRead(encB) == HIGH)
    curB = true;
  else
    curB = false;
  if(curA != oldA)
  {
    oldA = curA;
    if(curA != curB)
    {
      curEnc++;
    }
    if(curA == curB)
    {
      curEnc--;
    }
  }*/
  if(Serial.available() > 0)
  {
    buff = Serial.read();
    if(buff & 1 && !df)
    {
      blinkLed();
      //openDoor()
    }
    else if(!(buff & 1) && df)
    {
      blinkLed();
      //closeDoor()
    }
    if(buff & 2 && !bf)
    {
      turnOn();
    }
    else if(!(buff & 2) && bf)
    {
      turnOff();
    }
    Serial.print(buff, BIN);
  }
}
