#!/bin/bash
if [ ! -f "$1" ]; then
    echo "Ошибка: файл '$1' не существует."
    exit 1
fi


lines=$(wc -l < "$1")
words=$(wc -w < "$1")
chars=$(wc -m < "$1")


echo "Файл: $1"
echo "Количество строк: $lines"
echo "Количество слов: $words"
echo "Количество символов: $chars"
