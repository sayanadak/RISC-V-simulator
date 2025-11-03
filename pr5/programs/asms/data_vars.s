.section .data
	.align 2
myvar1: 
	.word 0xc001          # Define word with value 0xc001

myvar2: 
	.word 0xc0de          # Define word with value 0xc0de

	.size myarr, 16       # Size of myarr is 16 bytes
myarr:  
	.word 0xfeed          # Array element 1
	.word 0xdeed          # Array element 2
	.word 0xdeaf          # Array element 3
	.word 0xd00d          # Array element 4

.section .text
	.globl main
main:
	la x1, myvar1         # Load address of myvar1 into x1
	lw x11, 0(x1)         # Load word from address in x1 into x11

	la x2, myvar2         # Load address of myvar2 into x2
	lw x12, 0(x2)         # Load word from address in x2 into x12

	la x3, myarr          # Load address of myarr into x3
	lw x13, 0(x3)         # Load first element of myarr into x13
	lw x14, 4(x3)         # Load second element of myarr into x14

halt:
	j halt                # Infinite loop to halt the program
