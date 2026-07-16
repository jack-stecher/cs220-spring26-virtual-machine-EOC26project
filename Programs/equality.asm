.ORIG x0000

GET R1          ;get r1 say 5
GET R2          ;get r2 say 5
NOT R3 R2       ;not r2 0000 0000 0000 0101 --> 1111 1111 1111 1010 which would be stored in r3 as -6
ADD R3 R3 #1    ;add -6 and 1 (-5) and store in r3
ADD R3 R1 R3    ;add -5 and 5 get 0 in r3
BR z x0008      ;since z = 0, z gets 1 and BR does trigger and moves to x0008

PUT R0          ;print
HALT

ADD R0 R0 #1 ;x0008 0 + 1 = 1
PUT R0       ; print 1
HALT

.END