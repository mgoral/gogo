
# Gogo from anywhere.
function gogo
{
    dir=$(gogo.py $1)
    if [ $? -eq 0 ]; then
        cd "${dir}"
    fi
}
