# This is based on [bash_ini_parser](https://github.com/rudimeier/bash_ini_parser)
# Read variables from a configure file
# For example, we have a `test.conf` file whose contents are
#   foo = hello world
#   bar = "world hello"
#
# Then after `readconf test.conf`, we can get variables
# __conf_foo="hello world"
# __conf_bar-"world hello"


CONF_VAR_PREFIX=__conf_


#######################################
# Read variables from a conf file
# Arguments:
#   file path and name
# Returns:
#   1: encounters error
#######################################
readconf () {
    local USAGE="Usage: ${FUNCNAME[0]} FILE"

    if (($# < 1)); then
        echo "$USAGE" >&2
        return 1
    fi

    local varprefix=$CONF_VAR_PREFIX
    local conffile="$1"
    local fnname="${FUNCNAME[0]}"
    local switch_shopt=""

    check_prefix() {
        if [ -z "${varprefix}" ]; then
            return 0
        fi
        if ! [[ "${varprefix}" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]] ;then
            echo "${fnname}: invalid prefix '${varprefix}'" >&2
            return 1
        fi
    }

    check_conf_file() {
        if [ ! -r "$conffile" ]; then
            echo "${fnname}: cannot find file '${conffile}'" >&2
            return 1
        fi
    }

    # enable some optional shell behavior (shopt)
    pollute_bash() {
        if ! shopt -q extglob; then
            switch_shopt="${switch_shopt} extglob"
        fi
        if ! shopt -q nocasematch; then
            switch_shopt="${switch_shopt} nocasematch"
        fi
        shopt -q -s ${switch_shopt}
    }

    cleanup_bash() {
        shopt -q -u ${switch_shopt}
        unset -f check_prefix check_conf_file
    }

    if ! check_prefix; then
        cleanup_bash
        return 1
    fi

    if ! check_conf_file; then
        cleanup_bash
        return 1
    fi

    local line_num=0
    # IFS is used in "read" and we want to switch it within the loop
    local IFS=$' \t\n'
    local IFS_OLD="${IFS}"
    while read -r line; do
        # delete leading and tailing spaces
        line="${line##+([[:space:]])}"
        line="${line%%+([[:space:]])}"

        ((line_num++)) || :
        # skip blank lines and comments
        if [ -z "$line" ] || [ "${line:0:1}" = ";" ] || [ "${line:0:1}" = "#" ]
        then
            continue
        fi

        # valid var/value line? (check for variable name and then '=')
        if ! [[ "${line}" =~ ^[a-zA-Z0-9._]{1,}[[:space:]]*= ]]; then
            echo "${fnname}: Invalid line:" >&2
            echo " ${line_num}: $line" >&2
            cleanup_bash
            return 1
        fi

        local confvar=
        local confval=
        # split line at "=" sign
        IFS="="
        read -r confvar confval <<< "${line}"
        IFS="${IFS_OLD}"

        shopt -q -s extglob
        # delete spaces around the equal sign (using extglob)
        confvar="${confvar%%+([[:space:]])}"
        confval="${confval##+([[:space:]])}"
        confvar=$(echo $confvar)

        if [[ "${confval}" =~ ^\".*\"$  ]]; then
            # remove existing double quotes
            confval="${confval##\"}"
            confval="${confval%%\"}"
        elif [[ "${confval}" =~ ^\'.*\'$  ]]; then
            # remove existing single quotes
            confval="${confval##\'}"
            confval="${confval%%\'}"
        fi
        # enclose the value in single quotes and escape any
        # single quotes and backslashes that may be in the value
        confval="${confval//\\/\\\\}"
        # the leading $ causes escape sequences to be interpreted
        confval="\$'${confval//\'/\'}'"
        local fullvarname=${varprefix}${confvar//./_}
        eval "$fullvarname=$confval"
    done < "$conffile"
    cleanup_bash
}
