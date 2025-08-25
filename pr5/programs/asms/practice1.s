.section .data

num1: .word 25        
num2: .word 42      
num3: .word 17        

.section .text
.globl main
main:
    
    la t1, num1        
    lw x1, 0(t1)       

    la t2, num2      
    lw x2, 0(t2)       

    la t3, num3        
    lw x3, 0(t3)      

   
    bge x1, x2, L1    
    mv t0, x2          
    j L2

L1:
    mv t0, x1         

L2:
   
    bge t0, x3, L3     
    mv x10, x3         
    j END

L3:
    mv x10, t0        

END:
halt:
	j halt

