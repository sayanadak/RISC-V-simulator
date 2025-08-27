.section .data
	.align 2
n:	
	.word 5
l:
	.word 2
	.word -1
	.word 7
	.word 5
	.word 3

.section .text
.globl main
main:
	
        la t0, l             
        lw t1, n             
        li t2, 0             
        li t3, 0             

loop:
    beq  t2, t1, end      

    slli t4, t2, 2       
    add  t5, t0, t4       
    lw   t6, 0(t5)         

    blt  t6, x0, skip     

    andi t4, t6, 1       
    bne  t4, x0, skip     

    addi t3, t3, 1      

skip:
    addi t2, t2, 1       
    j loop

end:
    mv x10, t3         

    li a7, 93

halt:
	j halt
