#!/bin/bash
if [ $# -ne 3 ]; then
    echo "Использование: $0 число оператор число"
    echo "Пример: $0 5 + 3"
    exit 1
fi


num1=$1
op=$2
num2=$3


if [ "$op" = "/" ] && [ "$num2" -eq 0 ]; then
    echo "Ошибка: деление на ноль!"
    exit 1
fi


if [ "$op" = "+" ]; then
    result=$(( num1 + num2 ))
elif [ "$op" = "-" ]; then
    result=$(( num1 - num2 ))
elif [ "$op" = "*" ]; then
    result=$(( num1 * num2 ))
elif [ "$op" = "/" ]; then
    result=$(( num1 / num2 ))
else
    echo "Ошибка: неизвестный оператор '$op'"
    exit 1
fi

echo "Результат: $result"
