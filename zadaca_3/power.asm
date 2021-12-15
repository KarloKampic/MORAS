    @R2
    M=0  
    @1
    D=M 
    @EXIT
    D;JEQ
    @POWER
    D;JGT

(EXIT) 
    @R1
    D=A
    @2  
    M=D  
    @R0
    M=D  
    @END  
    0;JMP
    
(POWER)
    @R0
    D=M
    @R2  
    M=D  
    @END  
    D-1;JEQ
    
    

(LOOP)
    @R0
    D=M  
    @R3
    M=D-1 
    
    @R2
    D=M 
    @R4
    M=D  
    
    @R1
    M=M-1   
    D=M
    @MULT 
    D;JLT
    @END  
    D;JEQ

(MULT)
    @R4
    D=M 
    @R2
    M=D+M    
    
    @R3
    M=M-1 
    D=M
    @MULT           
    D;JGT
    @LOOP  
    D;JEQ
    
    
(END)
    0;JMP
    