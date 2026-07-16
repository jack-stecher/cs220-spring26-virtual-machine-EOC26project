	.ORIG x0000     ; XOR AB' + A'B
 
	GET R0          ; input A
	GET R1          ; input B
 
	NOT R4 R1       ; R4 = B'
	AND R3 R0 R4    ; R3 = AB'
 
	NOT R4 R0       ; R4 = A'
	AND R5 R4 R1    ; R5 = A'B
 
	NOT R3 R3       ; R3 = NOT(AB')
	NOT R5 R5       ; R5 = NOT(A'B)
	AND R2 R3 R5    ; R2 = NOT(AB') AND NOT(A'B)
	NOT R2 R2       ; R2 = XOR
 
	PUT R2
	HALT
	.END