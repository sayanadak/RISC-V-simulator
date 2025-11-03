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
	#first create count to track array number of iterations
		la t0, l          # t0 = base address
		#lw a0, 0(n)       # a0 = size of array(willl work as count) .....wrong method
		la t2, n   #load address
		lw a0, 0(t2)
		addi x10, x0, 0   # result counter = 0

	loop:
		beq a0, x0, halt  # break condition (a0 == x0)

		lw t1, 0(t0)      # load element into t1

		# check positive
		blt t1, x0, skip  # if <0, skip

		# check even
		andi t2, t1, 1
		bne  t2, x0, skip # if odd, skip

		addi x10, x10, 1  # if both true, increment counter

	skip:
		addi t0, t0, 4    # next element
		addi a0, a0, -1   # decrement loop counter
		jal x0, loop

halt:
    j halt


