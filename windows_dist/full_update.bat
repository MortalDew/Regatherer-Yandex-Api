@echo off

if exist bin/full_update.exe (

    call bin/full_update.exe SECRET_KEY

    pause

) else (

    echo not found

)
