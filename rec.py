import sqlite3 as sl
import easygui as gui
import os

conn = sl.connect("Phonebook.db")
cur = conn.cursor()

cur.execute("""
            CREATE TABLE IF NOT EXISTS users
            (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            surname TEXT,
            phone TEXT,
            birthday TEXT,
            email TEXT
            );
            """)

#Функция для отображения телефонного справочника
def display_phonebook():
  
  #Создание списка контактов
  cur.execute('SELECT * FROM Users ORDER BY id ASC')
  results = cur.fetchall()

  contact_list = []
  for row in results:
    id, name, surname, phone, birthday, email = row   
    contact_list.append("{} {}: {}, birtday {}, e-mail {}".format(name, surname, phone, birthday, email))
  #Отображение контактов в окне EasyGUI
  gui.textbox("Телефонный справочник", "Контакты", "\n".join(contact_list))

#Функция для сохранения телефонного справочника в файл
def save_phonebook():
  cur.execute ("SELECT * FROM Users ORDER BY id ASC")
  rows = cur.fetchall ()
  filedir = gui.diropenbox(msg="Выберите каталог", title="Каталог")
  if filedir != None:
    filename = os.path.join(filedir,"phonebook.csv")
    file = open(filename, 'w')
    file.write("id;name;surname;phone;birthday;email\n")
    for row in rows:
      file.write(";".join(map(str,row))+'\n')
    file.close()
    gui.msgbox ("Записи сохранены в файл phonebook.csv.", "Экспорт", ok_button="Close")

#Функция для импорта телефонного справочника из файла
def import_phonebook():
  filename = gui.fileopenbox('Выберете csv-файл для импорта данных')
  if filename != None:
    if filename[-4:] != '.csv':
      gui.msgbox ("Неверный формат файла.", "Импорт", ok_button="Close")
    else:
      file = open(filename, 'r')
      i = 0
      for line in file:
        if i == 0:
          i += 1
          continue
        id, name, surname, phone, birthday, email = line.strip().split(";")
        cur.execute("INSERT INTO users (name, surname, phone, birthday, email) VALUES (?, ?, ?, ?, ?);", (name, surname, phone, birthday, email))
        i += 1
      if i != 0: i -=1  
      conn.commit()
      gui.msgbox (f"Добавлено {i} контактов", "Импорт", ok_button="Close")
      
#Функция для поиска контакта в телефонном справочнике
def search_contact():
  poisk = gui.enterbox("Введите данные контакта:")
  cur.execute("SELECT * FROM users WHERE name = ? or surname = ? ;", (poisk, poisk))
  results = cur.fetchall()
  if len(results) > 0:
    contact_list = []
    for row in results:
      id, name, surname, phone, birthday, email = row   
      contact_list.append("{} {}: {}, birtday {}, e-mail {}".format(name, surname, phone, birthday, email))
    gui.textbox("Найдены следующие контакты", "Контакты", "\n".join(contact_list))
  else:
    gui.msgbox("Контакт не найден")

#Функция для добавления контакта в телефонный справочник
def add_contact():
  msg = "Введите данные контакта"
  title = "Добавление контакта" 
  fieldNames = ["Имя","Фамилия","Номер телефона","Дата рождения","e-mail"]
  box = gui.multenterbox(msg,title, fieldNames)
  if box != None:
    name, surname, phone, birthday, email = box
    #Не успела сделать проверку на наличие введенного контакта в БД
    cur.execute("INSERT INTO users (name, surname, phone, birthday, email) VALUES (?, ?, ?, ?, ?);", (name, surname, phone, birthday, email))
    conn.commit()
    gui.msgbox ("Контакт сохранен", "Сохранение", ok_button="Close")

#Функция для удаления контакта из телефонного справочника
def delete_contact():
  msg = "Введите данные контакта"
  title = "Удаление контакта" 
  fieldNames = ["Имя","Фамилия"]
  box = gui.multenterbox(msg,title, fieldNames)
  if box != None:
    name, surname = box
    cur.execute("SELECT id FROM users WHERE name = ? and surname = ? ;", (name, surname))
    results = cur.fetchall()
    if len(results) > 0:
      cur.execute("Delete FROM users WHERE name = ? and surname = ? ;", (name, surname))
      conn.commit()  
      gui.msgbox("Контакт удален")
    else:
      gui.msgbox("Контакт не найден")  

#Функция для изменения контакта в телефонном справочнике
def modify_contact():
  msg = "Введите данные контакта"
  title = "изменение контакта" 
  fieldNames = ["Имя","Фамилия"]
  box = gui.multenterbox(msg,title, fieldNames)
  if box != None:
    name, surname = box
    cur.execute("SELECT * FROM users WHERE name = ? and surname = ? ;", (name, surname))
    results = cur.fetchall()
    if len(results) > 0:
      id, name, surname, phone, birthday, email  = results[0]
      default_list = [name, surname, phone, birthday, email]
      fieldNames = ["Имя","Фамилия","Номер телефона","Дата рождения","e-mail"]
      box = gui.multenterbox(msg,title, fieldNames, default_list)
      if box != None:
        name, surname, phone, birthday, email = box
        cur.execute("Update users set name = ? , surname = ? , phone = ? , birthday = ? , email = ? where id = ? ;", (name, surname, phone, birthday, email,id))
        conn.commit()
        gui.msgbox ("Контакт сохранен", "Изменение", ok_button="Close")
    else:
      gui.msgbox("Контакт не найден")

#Основной код

while True:
  #Отображение главного меню
  choices = ["Просмотр", "Сохранение в файл", "Импорт из файла", "Поиск", "Добавление", "Удаление", "Изменение", "Выход"]
  choice = gui.buttonbox("Телефонный справочник", choices = choices)

  #Обработка выбранного действия
  if choice == "Просмотр":
    display_phonebook()
  elif choice == "Сохранение в файл":
    save_phonebook()
  elif choice == "Импорт из файла":
    phonebook = import_phonebook()
  elif choice == "Поиск":
    search_contact()
  elif choice == "Добавление":
    add_contact()
  elif choice == "Удаление":
    delete_contact()
  elif choice == "Изменение":
    modify_contact()
  else:
    break 

conn.close()