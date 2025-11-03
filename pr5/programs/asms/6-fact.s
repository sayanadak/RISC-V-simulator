.section .data

n: 
	.word 7

.section .text
.globl main
main:
	la t1, n 
	lw a0, 0(t1)

	jal ra, fact
halt:
	j halt

fact:
	#can do recursion or go iterative 

	#iterative approch 
	# li t1, 1 
	# li t2, 1
	# loop : 
	# 	bgt t1, a0, return_result
	# 	mul t2, t2, t1 
	# 	addi t1, t1 ,1 
	# 	j loop
	# return_result: 
	# 	mv a0, t2 
	# 	ret


	#recursive approch
    addi sp, sp, -8      # make stack space for ra and n
    sw ra, 4(sp)         # save return address
    sw a0, 0(sp)         # save n

    li t0, 1
    ble a0, t0, base_case   # if n <= 1, jump to base_case

    addi a0, a0, -1      # a0 = n - 1
    jal ra, fact         # recursive call fact(n-1)
    lw t1, 0(sp)         # restore n
    mul a0, t1, a0       # a0 = n * fact(n-1)
    j end_fact

	base_case:
		li a0, 1             # return 1

	end_fact:
		lw ra, 4(sp)         # restore return address
		addi sp, sp, 8       # free stack space
		ret                  # return to caller
