#define BINS 1024
int pulsepin = 5;
int capacitordump = 4;
int jctrl = 3;
int jinp = 9;
int val = 0;
int newpulse = 0;


int count[BINS];
int previous_time = 0;
int dumped = 0;
long interval_time = 1000;
long target_time;
long duration_time = 180000;

void setup()
{
  //pinMode(pulsepin, OUTPUT);
  pinMode(jctrl, OUTPUT);
  Serial.begin(9600);
  target_time = millis()+interval_time;
}

void loop()
{
  while(millis() < duration_time)
  {
    if(millis() < target_time) //2 seconds
    {
      newpulse = digitalRead(jinp);  // check for incoming pulse
      if (newpulse) {
          val = analogRead(capacitordump);
          count[val]++;
          digitalWrite(jctrl, HIGH);
          delayMicroseconds(5);
          digitalWrite(jctrl, LOW);
      }//if new pulse
    } else {
        
        target_time = millis()+interval_time;
    }//else
  }
  //while loop
  
  WriteandErase(); // put write and erase on outside to see total spectrum counts
  
}//loop

void WriteandErase(){ 
  for(int i=0; i<BINS; i++){
     Serial.println(count[i]);
     count[i] = 0;
   } 
  Serial.println("***");
}
