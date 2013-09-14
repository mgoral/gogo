
# Gogo from anywhere.
function gogo
{
    if [[ "$1" == "-e" ]] || [[ "$1" == "--editor" ]]; then
        gogo.py $1
        return
    fi

    dir=$(gogo.py $1)
    if [[ $? -eq 0 ]]; then
        cd "${dir}"
    fi
}
