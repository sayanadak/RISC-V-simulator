.section .data
	.align 2
count:
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
marks:
	.word 2
	.word 3
	.word 0
	.word 5
	.word 10
	.word 7
	.word 1
	.word 10
	.word 10
	.word 8
	.word 9
	.word 6
	.word 7
	.word 8
	.word 2
	.word 4
	.word 5
	.word 0
	.word 9
	.word 1
n:
	.word 20

.section .text
.globl main
main:
	# Check list
	# index i to traverse through array and get it's value a[i]
	# get value at index i and store it in count[a[i]]

	la t0, n 
	lw t0,0(t0) 			#N 
	addi t1, x0 , 0 			#i
	la a0, marks			#base address of marks
	la a1, count	        #base address of count
	
	loop: 
		beq t1, t0, halt   #break condition

		slli t2, t1, 2 		#t2 = i*4
		add t3, t2, a0 		#t3 address of marks[i]
		lw t4, 0(t3) 		#t4 = marks[i]

		slli t5, t4, 2 		#t5 = marks[i]*4
		add t5, t5, a1 		#t5 address of count[marks[i]]
		lw t6, 0(t5) 		#t6 = count[marks[i]]
		addi t6, t6, 1 		#t6 = count[marks[i]] + 1
		sw t6, 0(t5) 		#count[marks[i]] = t6
		
		#loop continues
		addi t1, t1, 1
		j loop




	


halt:
	j halt
