declare dso_local noalias align 16 i8* @malloc(i64) #2

define dso_local i8* @_malloc(i32 %0) #0 {
    %2 = sext i32 %0 to i64
    %3 = call noalias align 16 i8* @malloc(i64 %2) #4
    ret i8* %3, !dbg !265
}

