/// BOUNCE Arduino program
//     Use with BOUNCE Python program

// Author: Thy Doan Mai Le
// Date created: 7/28/2018
// Last update: 7/18/2019

/////////////////////////////////////////////////////////////
volatile int currentTime = 0;
char usrInput = "";
bool start = false;
char first = true;
volatile float secondsPassed = 0;
int interruptAt = 15624;

int inputPin = 2;
int val = 0;
 

void setup() {
  // put your setup code here, to run once:
  Serial.begin(250000);
  pinMode(inputPin, INPUT);
  
  analogReference(DEFAULT);
//  attachInterrupt(digitalPinToInterrupt(2), bounce, RISING);
//  noInterrupts();
//  TCCR1A = 0;
//  TCCR1B = 0;
//  TCNT1 = 0;
//  
//  //Set timer 1 to CLEAR upon Compare Match (CTC)
//  TCCR1A |= (1 << COM1A1);
//  
//  //Set timer 1 into CTC mode
//  // WGM12 and WGM13 are on register TCCR1B 
//  TCCR1B |= (1 << WGM12);
//
//  //Set 1024 prescaler
//  TCCR1B |= (1 << CS10);
//  TCCR1B |= (1 << CS12);
//
//  TIMSK1 |= (1 << OCIE1A);
//
//  OCR1A = interruptAt;
//  interrupts();

  Serial.write("BOU");
}
void bounce(){
  if(start){
    Serial.println("Interrupt");
//
//    if(first == true){
//      currentTime = millis();
//      first = false;
//    }
//    else{
//      secondsPassed = millis() - currentTime;
//      secondsPassed = secondsPassed/1000;
//      Serial.println(secondsPassed);
//      currentTime = millis();
//      secondsPassed = 0;
//    }

  }
}

void loop() {
  // put your main code here, to run repeatedly:
  val = analogRead(A0);
  
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
  if(val >= 1000){
    Serial.println(val);
  }
}
