
# Gogo from anywhere.
function gogo
{
    CMD=`gogo.py $@`
    RET=$?
    eval "$CMD"
    return $RET
}
