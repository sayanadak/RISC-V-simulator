    .section .data
    .align 2
a:
    .word 70
    .word 80
    .word 40
    .word 20
    .word 10
    .word 30
    .word 50
    .word 60
n:
    .word 8          # size of array

    .section .text
    .globl main
main:
    # Load base address of array and size
    la t0, a          # t0 = base address of array
    la t1, n          # base address for N
    lw t1, 0(t1)	  # N


    li t2, 0          # i = 0 (outer loop index)
	outer_loop:
		bge t2, t1, halt  # if i >= n, sorting done
		add t3, t2, 1     # j = i + 1 (inner loop index)
		inner_loop:
			bge t3, t1, outer_increment  # if j >= n, move to next i

			# Compute addresses of a[i] and a[j]
			slli t4, t2, 2    # t4 = i*4(offset compute i)
			slli t5, t3, 2    # t5 = j*4(offset compute for j)
			add t6, t0, t4    # t6 = &a[i]
			add a0, t0, t5    # a0 = &a[j]

			lw a1, 0(t6)      # a1 = a[i]
			lw a2, 0(a0)      # a2 = a[j]

			blt a1, a2, do_swap   # if a[i] < a[j], swap
			j inner_next

		do_swap:
			sw a2, 0(t6)      # a[i] = a[j]
			sw a1, 0(a0)      # a[j] = a[i]

		inner_next:
			addi t3, t3, 1
			j inner_loop

	outer_increment:
		addi t2, t2, 1
		j outer_loop

halt:
    j halt            
