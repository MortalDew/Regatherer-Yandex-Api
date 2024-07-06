@echo off

if exist bin/getinf.exe (

    call bin/getinf.exe SECRET_KEY

    pause

) else (

    echo not found

)
