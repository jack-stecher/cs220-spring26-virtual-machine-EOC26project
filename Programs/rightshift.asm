	.ORIG x0000
 
	GET R0          ; input value, Ex. r0 = 6
 
	AND R2 R2 #0    ; R2 = 0  (result)
	ADD R1 R0 #0    ; R1 = copy of R0, r1 = 6
 
LOOP	ADD R1 R1 #-1   ; R1 -= 1  (first half of -2), r1 = 5, r1 = 3, r1 = 1
	BR N DONE       ; went negative, branch to done
	ADD R1 R1 #-1   ; R1 -= 1  (second half of -2), r1 = 4, r1 = 2, r1 = 0
	BR N DONE       ; went negative branch to done 
	ADD R2 R2 #1    ; result++, r2 = 1, r2 = 2, r3 = 3
	BR Z DONE       ; R1 hit exactly 0 branch to done, branches to done after 3 loops
	JMP LOOP        ; JMP to LOOP and run again
 
DONE	PUT R2          ; result should be int/2, prints 3
	HALT
	.END