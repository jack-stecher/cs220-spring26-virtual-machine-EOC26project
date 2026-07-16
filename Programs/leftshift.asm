; Left Shift

    .ORIG x0000

    GET R0          ; This will be shifted. Ex. 5
    ADD R0 R0 R0    ; R0 gets R0 + R0 (left shift by 1). ro gets 5+5 (10)
    PUT R0          ; value printed should be double input (R0 * 2) (10)
    HALT

.END    