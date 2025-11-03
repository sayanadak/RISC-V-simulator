.section .data

a : .word 10
	.word 20 
	.word 30
	.word 40
	.word 50
	.word 60
	.word 70
	.word 80
	.word 90


b : .word 1
	.word 2
	.word 3
	.word 4
	.word 5
	.word 6
	.word 7		
	.word 8
	.word 9

	
c : .word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0




.section .text


.globl main
main:
	# your code here
	# remove these two line comments when done

	#storing arguments in a0,a1,a2; 
	la a0, a 				#pointer to a
	la a1, b				#pointer to b
	la a2, c 				#pointer to c 

	#call to the function
	jal ra, matmul 
	mv x10, a0         		#return address stored into x10

	halt:
	j halt









matmul: 

#for(int i = 0 ;i<3 ;i++){
#	for(int j = 0 ;j<3;j++){
#		for(int k = 0 ;k<3;k++){
#			c[i][j] += a[i][k]*b[k][j]
#		}
#	}
#}

addi t0, x0, 0 					#i 
addi t1, x0, 0 					#j
addi t2, x0, 0 					#k 
addi t3, x0, 3					#3
addi t6, x0, 0 					#sum 




i_loop : 
	bge t0, t3, return_1 				# return 1 as no element c[i][j] = 0 nott  found 
	li t1, 0							# j = 0 
	j_loop :
		bge t1,t3, next_i 
		li t2, 0 						#reset k = 0
		li s0, 0 						#reset sum = 0 

		k_loop : 
			bge t2, t3, store   		#k iterations completed store the sum 

			#get value at a[i][k]
			mul t4, t0, t3 				#t4= i*3
			add t4, t4, t2 				#t4= i*3 + k
			slli t4, t4, 2				#t4=4(i*3 + k)
			add t5, t4, a0 				#addres of a[i][k]
			lw t5, 0(t5)				#t5 = a[i][k]

			#get value at b[k][j]
			mul  t4,t2,t3				#t4= k*3
			add  t4, t4, t1				#t4= k*3 + j
			slli t4, t4, 2				#t4= 4(k*4 + j)
			add  t6, t4, a1				#address of b[k][j]
			lw 	 t6, 0(t6)				#t6 = b[k][j]

			mul s1, t5, t6 
			add s0, s0, s1

			#increment the k and jump to k_loop
			addi t2, t2, 1
			j k_loop
store : 
	#store value at c[i][j] and if c[i][j] == 0 return value
	mul s2, t0, t3
	add s2, s2, t1
	slli s2, s2, 2  
	add s2, s2, a2
	sw  s0, 0(s2)

	beq s0, x0, return_0
	
	addi t1, t1, 1 
	j j_loop 

next_i :
	addi t0, t0 , 1 
	j i_loop

			




return_0 :
	li a0, 0 
	ret

return_1 : 
	li a0, 1
	ret



