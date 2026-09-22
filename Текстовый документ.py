# Мини-приложение: Калькулятор с выбором операции
# Реализует первый вариант из диалога с обработкой деления на ноль и неверного ввода

def main():
    print("=== Мини-калькулятор Python ===")
    print("Доступные операции: +, -, *, /")
    
    while True:
        try:
            # Ввод первого числа с проверкой на корректность
            number1 = float(input("\nВведите первое число: "))
            
            # Выбор операции
            operation = input("Выберите операцию (+, -, * или /): ").strip()
            
            # Ввод второго числа
            number2 = float(input("Введите второе число: "))
            
            # Логика вычислений
            if operation == "+":
                result = number1 + number2
            elif operation == "-":
                result = number1 - number2
            elif operation == "*":
                result = number1 * number2
            elif operation == "/":
                if number2 == 0:
                    result = "Ошибка: на ноль делить нельзя!"
                else:
                    result = number1 / number2
            else:
                print(f"Ошибка: операция '{operation}' не поддерживается.")
                continue
            
            # Вывод результата
            print(f"Результат: {result}")
            
        except ValueError:
            print("Ошибка: введено не число. Попробуйте еще раз.")
            continue
        
        # Вопрос о продолжении
        next_step = input("\nВыполнить еще одно вычисление? (д/н): ").lower().strip()
        if next_step not in ["д", "да", "y", "yes"]:
            print("Калькулятор завершает работу. До свидания!")
            break

if __name__ == "__main__":
    main()