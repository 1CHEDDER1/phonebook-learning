import json
from pathlib import Path

file_path = Path("storage.json").resolve()
SEARCHABLE_FIELDS = ['name', 'number']

def load_data(file_path: Path):    
    try:
        raw_data = file_path.read_text(encoding="utf-8")
        data = json.loads(raw_data)
        
        if not isinstance(data, list): 
            return []
        
        valid_contacts = []
        for entry in data:
            if isinstance(entry, dict) and {'id', 'name', 'number'} <= entry.keys():
                valid_contacts.append(entry)
        return valid_contacts

    except json.JSONDecodeError:
        return []
    except FileNotFoundError:
        return []
   
def save_data(value_contacts: list, file_path: Path):
    try:
        json_str = json.dumps(value_contacts, ensure_ascii=False, indent=4)
        file_path.write_text(json_str, encoding="utf-8")
    except PermissionError:
        print("Ошибка: Нет прав на запись в этот файл.")

def list_contacts(value_contacts: list):
    if not value_contacts:
        print("Список контактов пуст.")
        return
    print(f"{'ID':<4} | {'Имя':<20} | {'Номер':<15}")
    print("-" * 45)
    for contact in value_contacts:
        print(f"{contact['id']:<4} | {contact['name']:<20} | {contact['number']:<15}")

def add_contact_logic(value_contacts: list, file_path: Path, name, number):
    new_id = max((c["id"] for c in value_contacts), default=0) + 1    

    new_contact = {
        "id": new_id,
        "name": name, 
        "number": number
    }
    value_contacts.append(new_contact)
    save_data(value_contacts, file_path)
    print("Контакт сохранен.")

def add_contact_ui(value_contacts: list, file_path: Path):
    name = input("Введите Имя: ").strip()
    number = input("Введите Номер: ").strip()

    if not name:
        print("Ошибка: Имя не может быть пустым!")
        return

    if not number or not number.isdigit():
        print("Ошибка: Номер обязателен и должен содержать только цифры!")
        return
    add_contact_logic(value_contacts, file_path, name, number)

def find_contacts(value_contacts: list, search_arg=None): 
    if not value_contacts:
        print("Телефонная книга пуста. Искать негде.")
        return
    
    if not search_arg:
        search_arg = input("Поиск: ").strip()
    
    search = search_arg.lower()
    if not search:
        print("Пустой запрос.")
        return

    results = [
        contact for contact in value_contacts 
        if any(search in str(contact[key]).lower() for key in SEARCHABLE_FIELDS)
    ]

    if results:
        print(f"\nНайдено совпадений: {len(results)}")
        list_contacts(results)
    else:
        print("Ничего не найдено.")

def delete_contacts(value_contacts: list, file_path: Path, target_arg=None):
    if target_arg is None:
        raw_input = input("Введите index контакта для удаления: ")
    else:
        raw_input = target_arg
    
    try:
        target_id = int(raw_input)
        value_contacts[:] = [c for c in value_contacts if c['id'] != target_id]
        print("Контакт удален!")
        save_data(value_contacts, file_path)

    except ValueError:
        print("Ошибка: index должен быть числом!")

def update_contacts(value_contacts: list, file_path: Path, update_arg=None):

    try:
        uid = int(update_arg) if update_arg else int(input("ID для изменения: "))
        target_contact = next((c for c in value_contacts if c["id"] == uid), None)

        if not target_contact:
            print("Ошибка: ID не найден.")
            return
        
        print(f"Редактируем: {target_contact['name']} | {target_contact['number']}")
        new_name = input(f"Новое имя [{target_contact['name']}]: ").strip()
        new_number = input(f"Новый номер [{target_contact['number']}]: ").strip()
        
        if new_number and not new_number.isdigit():
                print("Ошибка: Номер должен содержать только цифры! Изменение отменено.")
                return
        
        target_contact['name'] = new_name or target_contact['name']
        target_contact['number'] = new_number or target_contact['number']
        save_data(value_contacts, file_path)
        print("Контакт успешно обновлен.")

    except ValueError:
        print("Ошибка: index должен быть числом!")

def main(value_contacts: list, file_path: Path):
    print("\n=== ТЕЛЕФОННАЯ КНИГА ===")
    print("Команды:\n"
          "  add           - добавить контакт\n"
          "  list          - список всех\n"
          "  find <text>   - поиск\n"
          "  delete <index>   - удалить по index\n"
          "  update <index>   - изменить по index\n"
          "  exit          - выход")
    print("===============================\n")

    while True:
        try:
            user_input = input("\n> ").strip().split(maxsplit=1)
        except (EOFError, KeyboardInterrupt):
            print("\nВыход...")
            break
        
        if not user_input: 
            continue
            
        command = user_input[0].lower()
        args = user_input[1] if len(user_input) > 1 else None

        match command:
            case "add":    add_contact_ui(value_contacts, file_path)
            case "list":   list_contacts(value_contacts)
            case "find":   find_contacts(value_contacts, args)
            case "delete": delete_contacts(value_contacts, file_path, args)
            case "update": update_contacts(value_contacts, file_path, args)
            case "exit":   break
            case _:        print("Неизвестная команда.")

if __name__ == "__main__":
    initial_contacts = load_data(file_path)
    main(initial_contacts, file_path)