#define motorPwm 2
#define forward 3
#define backward 4
#define encA 5

#define T 10000
#define t_sh 10000

long t00 = 0,
     t01 = 0;

char buff = 0;

bool df = false;

bool SH = true;

int curEnc = 0;
bool curA = false,
     oldA = false;

void setup() {
  Serial.begin(2000000);
  pinMode(motorPwm, OUTPUT);
  pinMode(forward, OUTPUT);
  pinMode(backward, OUTPUT);
  pinMode(encA, INPUT);
}

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

void movel(char dir)
{
  switch(dir)
  {
    case '1':
      digitalWrite(backward, HIGH);
      digitalWrite(forward, LOW);
      break;
    
    case '2':
      digitalWrite(backward, LOW);
      digitalWrite(forward, HIGH);
      break;

    default:
      digitalWrite(backward, LOW);
      digitalWrite(forward, LOW);
      break;
  }
}

int eA, eB = 0;

void loop() {
  movel(buff);
  SH = true;
  digitalWrite(motorPwm, HIGH);
  t00 = micros();
  do
  {
    t01 = micros();
    if(SH && ((t01-t00) > t_sh))
    {
      SH = false;
      digitalWrite(motorPwm, LOW);
    }
    if(Serial.available() > 0)
    {
      buff = Serial.read();
    }
    if(digitalRead(encA) == HIGH)
    {
      curA = true;
    }
    else
    {
      curA = false;
    }
    if(curA != oldA)
    {
      oldA = curA;
      if(buff == '1')
      {
        curEnc++;
        //Serial.println(curEnc);
      }
      else if(buff == '2')
      {
        curEnc--;
        //Serial.println(curEnc);
      }
      eA = digitalRead(5);
      eB = digitalRead(6);
      Serial.print("encA - ");
      Serial.print(eA);
      Serial.println();
      Serial.print("encB - ");
      Serial.print(eB);
      Serial.println();
    }
  }while(t01 - t00 < T);
  /*curA = digitalRead(encA);
  Serial.println(curA);
  if(curA != oldA)
  {
    oldA = curA;
    if(!df)
    {
      curEnc++;
    }
    else
    {
      curEnc--;
    }
    Serial.println(curEnc);
  }
  if(Serial.available() > 0)
  {
    buff = Serial.read();
    if(buff == '1' && !df)
    {
      openDoor();
    }
    else if(buff == '2' && df)
    {
      closeDoor();
    }
  }*/
  
}
