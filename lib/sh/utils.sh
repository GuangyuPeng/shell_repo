#!/bin/bash
#
# Author: Danfeng Shan
#         Guangyu Peng

#######################################
# Print error message
#######################################
err() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >&2
}

###############################################
# Get the NIC device name to reach a given host
# Arguments:
#   Host name
# Outputs:
#   NIC name
###############################################
get_out_dev() {
  local USAGE="Usage: ${FUNCNAME[0]} HOST_NAME"
  if (($# < 1)); then
    echo "${USAGE}" >&2
    exit 1
  fi
  local host="$1"
  local py_script="import socket; print(socket.gethostbyname('${host}'))"
  local ip
  ip="$(python3 -c "${py_script}")"
  ip route get "${ip}" | grep -o "dev.*" | cut -d ' ' -f 2
}

########################################################
# Get the physical NIC device name to reach a given host
# Arguments:
#   Host name
# Outputs:
#   NIC name
########################################################
get_phy_out_dev() {
  local USAGE="Usage: ${FUNCNAME[0]} HOST_NAME"
  if (($# < 1)); then
    echo "$USAGE" >&2
    exit 1
  fi
  local host="$1"
  local py_script="import socket; print(socket.gethostbyname('${host}'))"
  local ip
  ip="$(python3 -c "${py_script}")"
  local dev
  dev="$(ip route get "${ip}" | grep -o "dev.*" | cut -d ' ' -f 2)"
  if [[ "$dev" == "lo" ]]; then
    echo "${dev}"
    return
  fi
  while [[ ! -e "/sys/class/net/${dev}/device" ]]; do
    local drv
    drv="$(ethtool -i "${dev}" | grep driver | cut -d' ' -f2)"
    if [[ "$drv" == 'bridge' ]]; then
      ping -c 1 -i 0.2 "${ip}" > /dev/null || err "ping $ip exits with error"
      local dmac
      dmac="$(ip neigh show "$ip" | grep -o "lladdr.*" | cut -d ' ' -f 2)"
      if [[ -z "${dmac}" ]]; then
          err "Cannot resolve the mac address of ${ip}"
          exit 1
      fi
      dev="$(bridge fdb get "${dmac}" br "${dev}" \
            | grep -o "dev.*" \
            | cut -d ' ' -f 2)"
    else
      err "Unknown device type: ${drv}"
      exit 1
    fi
  done
  echo "${dev}"
}

#######################################
# Get Operating System name
# Outputs:
#   OS name (macos/ubuntu)
#######################################
get_os_name() {
  case "$(uname -s)" in
    Darwin)
      echo "macos"
      ;;
    Linux)
      grep -i '^id=' /etc/os-release | awk -F= '{print $2}'
      ;;
  esac
}

#######################################
# Get CPU architecture
# Outputs:
#   CPU architecture (amd64/arm64)
#######################################
get_cpu_arch() {
  case "$(uname -m)" in
    i386)
      echo "386"
      ;;
    i686)
      echo "386"
      ;;
    x86_64)
      echo "amd64"
      ;;
    aarch64)
      echo "arm64"
      ;;
  esac
}

#######################################
# Quietly install package with homebrew
# Arguments:
#   Package names
#######################################
brew_install_quiet() {
  for formula in "$@"; do
    brew list "${formula}" &> /dev/null || brew install "${formula}"
  done
}

#################################################
# Install packages in different Operating systems
# Arguments:
#   Package names
#################################################
install_pkg() {
  if (($# == 0)); then
      return
  fi
  local os_name
  os_name="$(get_os_name)"
  if echo "${os_name}" | grep -q 'centos'; then
    sudo -E yum install -y "$@"
  elif echo "${os_name}" | grep -q 'ubuntu'; then
    sudo -E apt install -y "$@"
  elif echo "${os_name}" | grep -q 'arch'; then
    sudo -E pacman -Su --noconfirm --needed "$@"
  elif echo "${os_name}" | grep -q 'macos'; then
    brew_install_quiet "$@"
  else
    echo "Unknown OS: ${os_name}"
    exit 1
  fi
}

#################################################
# Get package downloadurl from github
# Arguments:
#   Github repository path
#################################################
get_github_downloadurl() {
  local USAGE="USAGE: ${FUNCNAME[0]} REPOSITORY_PATH"
  if (($# < 1)); then
    echo "$USAGE" >&2
    exit 1
  fi
  local repo_path="$1"
  local urls
  urls=$(curl https://api.github.com/repos/"${repo_path}"/releases/latest)
  if [[ -z "${urls}" ]]; then
    echo "Network Error" >&2
    exit 1
  fi
  local downloadurls
  downloadurls=$(echo "${urls}" | grep "browser_download_url")
  if [[ -z "$downloadurls" ]]; then
    echo "Fail to get the download url:"
    echo "$urls"
    exit 1
  fi
  echo "$downloadurls" | tr -d \" | cut -d : -f 2,3
}

####################################################################
# Backup directory by moving this directory to the archive directory
# Arguments:
#  Directory path to backup
#  Archive directory name
####################################################################
backup_dir() {
  local USAGE="Usage: ${FUNCNAME[0]} DIRECTORY [ARCHIVE_DIRECTORY]"
  if (($# < 1)); then
    echo "${USAGE}"
    exit 1
  fi
  local dirname="$1"
  local archivedir
  archivedir="$(dirname "${dirname}")/archives"
  if (($# >= 2)); then
    archivedir="$2"
  fi
  if [[ -e "${dirname}" ]] && [[ -n "$(ls "${dirname}")" ]]; then
    local postfix
    postfix="$(date +'%Y%m%d%H%M%S')"
    mkdir -p "${archivedir}"
    mv "${dirname}" "${archivedir}/$(basename "${dirname}")-${postfix}"
  fi
}

##############################################
# Bind the rx irq of a network device of a cpu
# Args:
#   Network interface name
#   CPU ID to bind the rx irq to
##############################################
bind_rxirq_to_cpu() {
  local USAGE="Usage: ${FUNCNAME[0]} DEVNAME CPU_ID"
  if (($# < 2)); then
    echo "${USAGE}"
    exit 1
  fi
  local devname="$1"
  local cpuid="$2"
  # `irqbalance` tries to automatically balance IRQs to CPUs
  # and it may overwrite the CPU affinity settings.
  pgrep irqbalance && sudo systemctl stop irqbalance.service
  local irqnums
  irqnums=$(grep "${devname}" /proc/interrupts | awk -F':' '{print $1}')
  for irqnum in "${irqnums[@]}"; do
    sudo bash -c "echo ${cpuid} > /proc/irq/${irqnum}/smp_affinity_list"
  done
}

#######################################
# Remove a qdisc from all devices
# Args:
#   qdisc name
#######################################
remove_qdisc() {
  local USAGE="${FUNCNAME[0]} QDISC"
  if (($# < 1)); then
    echo "${USAGE}"
    exit 1
  fi
  local qdisc="$1"
  for dev in $(ip link show | grep '^[0-9]\+' | cut -d':' -f2); do
    local tmp
    tmp="$(tc qdisc show dev "${dev}" | cut -d' ' -f2 | grep "^${qdisc}$")"
    if [[ -n "${tmp}" ]]; then
      sudo tc qdisc del dev "${dev}" root
    fi
  done
}

##########################################
# Remove a packet scheduling kernel module
# Args:
#   kernel module name
#   qdisc name of this kernel module
##########################################
remove_sch_mod() {
  local USAGE="${FUNCNAME[0]} MODULE_NAME QDISC_NAME"
  if (($# < 2)); then
    echo "${USAGE}"
    exit 1
  fi
  local modname="$1"
  local qdisc="$2"
  local n_used
  n_used=$(lsmod | grep "^${modname}\\s" | awk '{print $3}')
  if [[ -n "${n_used}" ]]; then
    if ((n_used > 0)); then
      remove_qdisc "${qdisc}"
    fi
    sudo rmmod "${modname}"
  fi
}
