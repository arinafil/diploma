#!/bin/bash
# setup.sh — Автоустановка проекта diploma
# Запуск: bash setup.sh

set -e  # Остановка при ошибке

echo "Запуск автоустановки проекта 'diploma'..."

# 1. Проверка Miniconda
if [ ! -d "miniconda" ]; then
    echo "Установка Miniconda..."
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    bash miniconda.sh -b -p $PWD/miniconda
    rm miniconda.sh
else
    echo "Miniconda уже установлен"
fi

# 2. Добавление в PATH
export PATH="$PWD/miniconda/bin:$PATH"

# 3. Инициализация conda
source miniconda/etc/profile.d/conda.sh
conda init zsh
conda init bash

# 4. Создание окружения base_env
if ! conda env list | grep -q "base_env"; then
    echo "Создание окружения base_env..."
    conda create -n base_env python=3.11 -y
else
    echo "Окружение base_env уже существует"
fi

# 5. Активация и установка пакетов
echo "Активация base_env и установка зависимостей..."
conda activate base_env

# Установи нужные пакеты (добавь свои!)
pip install biopython pandas snakemake tqdm

# 6. Проверка
echo "Проверка установки..."
python -c "import sys, Bio; print('Python:', sys.version.split()[0]); print('Biopython OK')"

echo ""
echo "УСПЕХ! Проект готов."
echo "Запуск: conda activate base_env && python parsing/parse_pipe/main.py"
echo "Или используй VS Code + Remote-SSH"
