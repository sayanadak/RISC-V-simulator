.section .data
	.align 2
a:
	.word 10

.section .text

.globl main
main:

	la t0, a 
	lw a0, 0(t0) 				#N
	#blt t1, 2, halt 			#directly terminating program as can't be prime anymore only regsiseter comparision
	addi x1, x0 , 2
	beq a0, x1, prime

	addi t0, x0, 2 				#starting loop from 2 (i)
	addi t1, a0, -1 			#for loop end check 
	blt a0,x1, not_prime


	loop: 
		beq t0, t1, prime  		#loop over prime confirmed
		rem t3, a0, t0 		 	#check remainder of N%i
		beq t3, x0, not_prime   #remainder zero jump to not_prime
		addi t0, t0, 1 			#increment i by 1
		#jal x0, loop			#continue loop
		j loop					#same as above
	
	prime: 
		addi x10, x0 , 1
		j halt
	not_prime: 
		addi x10, x0, -1
		j halt

halt:
	j halt
