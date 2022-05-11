#!/usr/bin/env bash

#This is to setup your pthon run environment.
#  Need internet connectivity for packages download
#  It is interactive Program to confirm the installation and pyats virtual environment.

PYTHON_MIN_VER_MAJOR=3
PYTHON_MIN_VER_MINOR=4

PYTHON3_REF=$(which python3 | grep "/python3" 2>/dev/null)
PYTHON_REF=$(which python | grep "/python" 2>/dev/null)
GIT_ROOT=$(git rev-parse --show-toplevel)

DEFAULT_VENV="./pyatsenv"

get_local_python() {
    err_msg="Requires minimum Python version ${PYTHON_MIN_VER_MAJOR}.${PYTHON_MIN_VER_MINOR}+"
    for pyref in "${PYTHON3_REF}" "${PYTHON_REF}"; do
        if [[ ! -z ${pyref} ]]; then
            local version=($(
                ${pyref} -c 'import platform; a, b, _ = platform.python_version_tuple(); print(a); print(b);'
            ))
            local major=${version[0]}
            local minor=${version[1]}
            if ! [[ ${major} -ge ${PYTHON_MIN_VER_MAJOR} && ${minor} -ge ${PYTHON_MIN_VER_MINOR} ]]; then
                echo ${err_msg} >&2
                return 1
            fi
            echo ${pyref}
            return 0
        fi
    done
    echo ${err_msg} >&2
    return 1
}
confirm() {
    prompt="${1:-Continue?}"
    allow_blank=$2
    while true; do
        read -p "${prompt} [Y/N]: " -n 1 yesno
        echo
        case $yesno in
            [Yy]*) break;;
            [Nn]*) return 1;;
            *)
                if [ ${allow_blank} ]; then
                    break
                else
                    echo "Please answer 'yes' or 'no'"
                fi
                ;;
        esac
    done
    return 0
}

# Get local python reference
python=$(get_local_python)
if [ ! $? ]; then
    # Terminate if this fails
    exit 1
fi

# Fail if in a virtual env
if [[ ! -z "${VIRTUAL_ENV}" ]]; then
    echo "You must deactivate any current virtual envs before running." >&2
    echo "Run 'deactivate' in your current shell to do so." >&2
    exit 1
fi

# Check prerequisites
missing=0
if ! which ${python}-config &>/dev/null; then
    echo
    echo "Requires Python development headers package.  Please install it first." >&2
    echo '  RHEL/CEL: `yum install -y python3-devel`'
    echo '  Ubuntu:   `apt-get install -y python3-dev`'
    echo '  OSX:      `brew install python3`'
    missing=1
fi
if [ ${missing} -ne 0 ]; then
    exit 1
fi

# Prompt installation
echo "Starting pyats virtual environment setup script!"
echo "This script will create a PyATS virtual environment and install all required packages."
echo
echo "Use 'CTRL+C' to terminate this script at any time."
echo
echo "Please answer the following prompts."
echo "(Blank responses will use the default values)"
echo
# Prompt for PyATS venv
while true; do
    echo "Please specifiy where the PyATS virtual environment will be installed:"
    read -p "(default: './pyatsenv') > " opt_install
    opt_install=${opt_install:-${DEFAULT_VENV}}     # Set default
    opt_install=${opt_install/#\~/${HOME}}          # Expand '~' if at front
    if [[ -d "${opt_install}" ]]; then
        if ! confirm "This directory already exists and will be replaced.  Are you sure?"; then
            continue
        fi
    fi
    break
done

# Confirm settings
echo "Starting with the following settings:"
echo "  PyATS venv dir:    ${opt_install}"
# Create venv
cd ${GIT_ROOT} &>/dev/null
if [[ -d "${opt_install}" ]]; then
    echo "Replacing pre-existing virtual env \"${opt_install}\""
    rm -Rf ${opt_install}
else
    echo "Creating virtual env \"${opt_install}\""
fi
${python} -m venv "${opt_install}"
if [[ ! -d "${opt_install}" ]]; then
    echo "Failed to create virtual env! Terminating!" >&2
    exit 1
fi
# Activate venv
echo 'export PYTHONPATH=.' >> "${opt_install}/bin/activate"
source "${opt_install}/bin/activate"
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "Failed to source virtual env!" >&2
    exit 1
fi
# Install packages
echo "Installing packages"
pip3 install --upgrade pip
pip3 install -r requirements.txt

# TODO: pre-commit install
if [ $? -eq 0 ]; then
    echo "Setup complete!"
    echo "You can now source your new pyats environment with ${opt_install}/bin/activate"
else
    echo "Encountered error during installation!" >&2
    exit 1
fi