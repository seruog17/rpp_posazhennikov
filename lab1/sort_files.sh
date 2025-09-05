#!/bin/bash

mkdir test_dir
echo "Файл 1" > test_dir/file1.txt
sleep 2
echo "Файл 2" > test_dir/file2.txt
sleep 2
echo "Файл 3" > test_dir/file3.txt


if [ ! -d "$1" ]; then
    echo "Ошибка: директория '$1' не существует."
    exit 1
fi


find "$1" -type f -exec stat -f "%m %N" {} \; | sort -nr | cut -d' ' -f2-
