 // Thy Doan Mai Le
// Fake Data for Bounce
// 10-9-2018

volatile unsigned long initCompare = 15624; //interrupts once per second 
int ledPin = 13;
volatile unsigned long currentTime = 0;
volatile unsigned long lastTime = 0;
volatile unsigned long duration = 0;
boolean go = false;
boolean first = true;
char receivedChr;
float value;

void setup() {

  Serial.begin(115200);
  while(!Serial);
  delay(100);
  
  //interrupts();
  
  // put your setup code here, to run once:
  pinMode(ledPin, OUTPUT);
  value = 1000;

  TCCR0A = 0;
  TCCR0B = 0;
  TCNT1 = 0;
  TCNT0 = 0; 
  //resetting all registers
}

//Interrupt Service Routine
///////////////////////////
ISR(TIMER1_COMPA_vect){
  //needs to output value stored in TCNT1
  //currentTime = TCNT1;
  //duration = currentTime - lastTime;
  //Serial.println(TCNT1);
  //Serial.println(duration);
  //Serial.println(OCR0A);
  //value = 0.9*value;
  //lastTime = currentTime;
  digitalWrite(ledPin,HIGH);
  digitalWrite(ledPin, LOW);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(first){
    Serial.write("BOU");
    first = false;
  }
  if(Serial.available() > 0){
    receivedChr = Serial.read();
  }
  if(receivedChr == 'g'){
    //Serial.println("go");
    go = true;
    interrupts();
    //Serial.println("Before Init of Timer1");
    
    //init Timer 1
    OCR1A = initCompare;
    TCCR1B |= (1 << WGM12);
    TIMSK1 |= (1 << OCIE1A);
    TCCR1B |= (1 << CS12);
    TCCR1B |= (1 << CS10);
    //1024 prescaler for Timer 1
    //interrupting on Timer 1 on CTC mode
    //interrupt frequency 1Hz

    receivedChr="";
    
  }
  else if(receivedChr == 's'){
    
    receivedChr="";
    //Serial.println("stop");
    //noInterrupts();
    go = false;
    //init Timer 0
    TCCR0A = 0;
    TCCR0B = 0;
    TCNT0 = 0;
    OCR0A = 0;
    TIMSK0 = 0;
  }
  
}
