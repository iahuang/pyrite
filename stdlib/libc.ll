; The following is a header that defines libc methods, and should be placed
; at the top of the final LLVM output.

declare dso_local noalias align 16 i8* @malloc(i64) #2
