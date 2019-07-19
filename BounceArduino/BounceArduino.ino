/// BOUNCE Arduino program
//     Use with BOUNCE Python program

// Author: Thy Doan Mai Le
// Date created: 7/28/2018
// Last update: 7/18/2019

/////////////////////////////////////////////////////////////
volatile int timePassed = 0;
char usrInput = "";
bool start = false;
char first = true;
volatile int secondsPassed = 0;

int inputPin = 2;
 

void setup() {
  // put your setup code here, to run once:
  Serial.begin(250000);
  pinMode(inputPin, INPUT_PULLUP);
  
  analogReference(DEFAULT);
  attachInterrupt(digitalPinToInterrupt(2), bounce, RISING);
  Serial.write("BOU");
}

void bounce(){
  digitalWrite(13, HIGH);
  if(first == true){
    timePassed = millis();
    first = false;
  }
  else{
    timePassed = millis() - timePassed;
    secondsPassed = timePassed/1000;
    Serial.println(secondsPassed);
    secondsPassed = 0;
  }
  digitalWrite(13, LOW);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available()){
    usrInput = Serial.read();

    if(usrInput == 'g'){
       start = true;
       usrInput = "";
    }
    else if(usrInput == 's'){
      start = false;
      usrInput = "";
    }
  }
}
