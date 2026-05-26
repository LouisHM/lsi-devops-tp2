#!/bin/bash

PYTHON_REQUIREMENTS_FILE=requirements.txt

download_galaxy () {
  ansible-galaxy install -r ${CUR_MOL_VENV_DIR}/roles/requirements.yml -p ${CUR_MOL_VENV_DIR}/roles/ --force
  ansible-galaxy collection install -r ${CUR_MOL_VENV_DIR}/collections/requirements.yml -p ${CUR_MOL_VENV_DIR}/.ansible/collections/ --force
}

setup_env () {
  dir=$(basename ${CUR_MOL_VENV_DIR})
  if [[ -d "${CUR_MOL_VENV_DIR}/.virtualenv" ]]
  then
    source ${CUR_MOL_VENV_DIR}/.virtualenv/${dir}/bin/activate
  else
    virtualenv -p `which python3` ${CUR_MOL_VENV_DIR}/.virtualenv/${dir} && source ${CUR_MOL_VENV_DIR}/.virtualenv/${dir}/bin/activate || { echo "[ERROR] venv creation failed"; return 1; }
    python -m pip install --upgrade pip || { echo "[ERROR] pip upgrade failed"; return 1; }
    python -m pip install -r ${CUR_MOL_VENV_DIR}/${PYTHON_REQUIREMENTS_FILE} || { echo "[ERROR] pip install failed"; return 1; }
  fi
  # Force zsh/bash to rehash the command cache after activation
  hash -r 2>/dev/null || rehash 2>/dev/null || true
  echo "Python: $(python --version) | $(which python)"
}

update_requirements () {
  _python_requirements_file=$PYTHON_REQUIREMENTS_FILE
  PYTHON_REQUIREMENTS_FILE=requirements.update.txt
  rebuild_env
  PYTHON_REQUIREMENTS_FILE=$_python_requirements_file
  python -m pip freeze > ${CUR_MOL_VENV_DIR}/$PYTHON_REQUIREMENTS_FILE
}

rebuild_env () {
  deactivate
  rm -rf ${CUR_MOL_VENV_DIR}/.virtualenv
  setup_env
}

if [[ ! -f "venv.sh" ]]; then
  echo "Sourcing must be done in the base directory"
  return 1
fi

CUR_MOL_VENV_DIR=`pwd`
setup_env

echo "############################################################"
echo "Type 'deactivate' to quit venv"
echo "Type 'download_galaxy' to download ansible roles"
echo "Type 'rebuild_env' to update your virtualenv"
echo "############################################################"
