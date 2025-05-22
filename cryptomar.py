import time
import os
import sys
import platform
import ctypes
import random
import hashlib
import subprocess
import requests
import threading
import queue
import pyperclip
from datetime import datetime

from tqdm import tqdm
from multiprocessing import Process, Value, shared_memory
import CryptoMar

# === CONFIG ===
FILE_PATH = 'P2WPKH.nonzero.txt'  # Вхідний файл з адресами
PAYMENT_FILE = "payment_confirmed.txt"
BLOCKSTREAM_API = 'https://blockstream.info/api/address/'
num_processes = os.cpu_count()
BLOCKCHAIN_EXPLORER = "https://www.blockchain.com/btc/address/"


def cryptomar():
    print("""|=========================================================================================|
|                                                                                         |
|                 _____                      _           __  __                           |
|                / ____|                    | |         |  \/  |                          |
|               | |      _ __  _   _  _ __  | |_   ___  | \  / |  __ _  _ __              |
|               | |     | '__|| | | || '_ \ | __| / _ \ | |\/| | / _` || '__|             | 
|               | |____ | |   | |_| || |_) || |_ | (_) || |  | || (_| || |                |
|                \_____||_|    \__, || .__/  \__| \___/ |_|  |_| \__,_||_|                |
|                               __/ || |                                                  |
|                              |___/ |_|                                                  |
|                                                                                         |
|=========================================================================================|""")


# Визначаємо країну користувача
def get_country():
    try:
        # Визначення глобальної IP-адреси
        ip_response = requests.get("https://api.ipify.org?format=json")
        ip = ip_response.json().get("ip")

        country_response = requests.get(f"https://ipinfo.io/{ip}/json")
        country = country_response.json().get("country")

        return country

    except requests.RequestException:
        return None

user_input = ""


def auto_select_english():
    global language
    if get_country() == "UA":
        language = "Українська"
        print("\n|  Мова встановлена автоматично.                                                          |")
    elif get_country() == "RU":
        language = "Русский"
        print("\n|  Язык выбран автоматически.                                                             |")
    else:
        language = "English"
        print("\n|  Language selected automatically.                                                       |")
    set_language()


def get_language():
    global language, user_input
    print("\n" * 100)
    cryptomar()
    print("|                                                                                         |")
    print("|  Select language (default: English):                                                    |")
    print("|  1 - English                                                                            |")
    print("|  2 - Русский                                                                            |")
    print("|  3 - Українська                                                                         |")
    print("|  4 - Español                                                                            |")
    print("|  5 - Deutsch                                                                            |")
    print("|  6 - Français                                                                           |")
    print("|  7 - Português                                                                          |")
    print("|  8 - Türkçe                                                                             |")

    prompt = "|  Enter your choice (automatically after 30 seconds): "

    choice = input_with_timeout(prompt, timeout=30)

    print("\n" * 100)
    cryptomar()

    if choice in ("", None, "1"):
        language = "English"
        print("|                                                                                         |")
        print("|  English language set                                                                   |")
    elif choice == "2":
        language = "Русский"
        print("|                                                                                         |")
        print("|  Установлен русский язык                                                                |")
    elif choice == "3":
        language = "Українська"
        print("|                                                                                         |")
        print("|  Встановлено українську мову                                                            |")
    elif choice == "4":
        language = "Español"
        print("|                                                                                         |")
        print("|  Idioma español establecido                                                             |")
    elif choice == "5":
        language = "Deutsch"
        print("|                                                                                         |")
        print("|  Sprache Deutsch eingestellt                                                            |")
    elif choice == "6":
        language = "Français"
        print("|                                                                                         |")
        print("|  Langue française définie                                                               |")
    elif choice == "7":
        language = "Português"
        print("|                                                                                         |")
        print("|  Idioma português definido                                                              |")
    elif choice == "8":
        language = "Türkçe"
        print("|                                                                                         |")
        print("|  Türkçe dili seçildi                                                                    |")
    else:
        if get_country() == "UA":
            language = "Українська"
            print("|                                                                                         |")
            print("|  Встановлено автоматично українську мову                                                |")
        elif get_country() == "RU":
            language = "Русский"
            print("|                                                                                         |")
            print("|  Установлен автоматически русский язык                                                  |")
        else:
            language = "English"
            print("|                                                                                         |")
            print("|  English language set automatically                                                     |")

    set_language()

def set_language():
    global FOUND, ADRESS, BALANCE, SATOSHIS, WIF, CHECK, AUTOMATIC, PAYMENTADRESS
    global FEE, CHECKBALANCE, CURRENTBALANCE, WAITING, PLEASEADD, RECEIVED
    global SETUP, SOON, LOADING, LOADED, ADRESSES, GOODLUCK, WANNAPAY, PLEASEPAY, PAYMENTCONFIRMED, PAYNOW, PROGRAMPRICE, PAYMENTWALLET, PAYMENT_INSTRUCTIONS, FREEVERSION

    # ================= Встановлюємо мовний параметр =================
    if language == "English":
        # ============== Мовні налаштування для англійської мови ==============
        FOUND = "|  Address with balance found!                                                            |"
        ADRESS = "|  Address: "
        BALANCE = "|  Balance: "
        SATOSHIS = " satoshis. "
        WIF = "|  WIF: "
        CHECK = "|  Check on Blockchain:                                                                   |"
        AUTOMATIC = (f"|  To obtain the key for this wallet                                                      |\n"
                     f"|  a 10% fee must be paid.                                                                |")
        PAYMENTADRESS = "|  Payment address: "
        FEE = "|  Fee: "
        CHECKBALANCE = (
            f"\r|  Do not close the program until you complete the payment                                |\n"
            f"\r|  and receive the key! Otherwise, data will be lost!                                     |\n"
            f"\r|  After payment confirmation, wait for the program's message                             |\n"
            f"\r|  about the successful transfer of funds to your wallet address!                         |\n"
            f"\r|  Checking balance...                                                                    |")
        CURRENTBALANCE = "|  Current balance: "
        WAITING = "Waiting for payment..."
        PLEASEADD = "Please add "
        RECEIVED = "|  Payment received: "
        SETUP = "|  Setup completed.                                                                       |"
        SOON = "|  Please wait, the process will start soon...                                            |"
        LOADING = "|------------------------------ Loading addresses into memory ----------------------------|"
        LOADED = "|  Loaded "
        ADRESSES = " addresses."
        GOODLUCK = (f"|  The key search process is not fast.                                                    |\n"
                    f"|  It can take days or even weeks.                                                        |\n"
                    f"|  It all depends on your processor's power and luck.                                     |\n"
                    f"|_________________________________________________________________________________________|\n"
                    f"|                                                                                         |")
        WANNAPAY =  f"|  Want to buy the full version of the program? Press Enter... (30 seconds)               |"
        PLEASEPAY = f"|  To use the program, you need to make a payment.                                        |"
        PAYMENTCONFIRMED = ("|  Payment has been confirmed and verified.                                               |\n"
                            "|  Full version of the program has been launched.                                         |")
        PAYNOW = f"|  You can make the payment to the specified wallet:                                      |"
        PROGRAMPRICE = f"|  Price: "
        PAYMENTWALLET = f"|  Wallet for payment: "
        PAYMENT_INSTRUCTIONS = (
            f"|  If you have made the payment, do not close the program                                 |\n"
            f"|  until confirmation is received; otherwise, the funds will be lost!                     |\n"
            f"|-----------------------------------------------------------------------------------------|\n"
            f"|  If you restart the program, a new wallet will be generated for payment.                |\n"
            f"|  Please complete the payment and wait for confirmation                                  |\n"
            f"|  within the same session!                                                               |\n"
            f"|-----------------------------------------------------------------------------------------|\n"
            f"|  Once the payment is received, the program will automatically start working,            |\n"
            f"|  and the payment information will be saved.                                             |\n"
            f"|  Payment is made only once.                                                             |\n"
            f"|                                                                                         |\n"
            f"|  The transfer may take 10 minutes or longer.                                            |"
        )
        FREEVERSION = ("|  Free version of the program has been launched.                                         |\n"
                       "|  Address processing speed is limited                                                    |")


    elif language == "Русский":
        # ============== Мовні налаштування для російської мови ==============
        FOUND =       "|  Адрес с балансом найден!                                                               |"
        ADRESS =      "|  Адрес: "
        BALANCE =     "|  Баланс: "
        SATOSHIS =    " сатоши. "
        WIF =         "|  WIF: "
        CHECK =       "|  Проверка на блокчейне:                                                                 |"
        AUTOMATIC = (f"|  Для получения ключа от этого кошелька                                                  |\n"
                     f"|  необходимо оплатить комиссию в размере 10%.                                            |")
        PAYMENTADRESS = "|  Адрес для оплаты: "
        FEE =         "|  Комиссия: "
        CHECKBALANCE = (f"\r|  Не закрывайте программу, пока не завершите оплату                                      |\n"
                        f"\r|  и не получите ключ! В противном случае данные будут потеряны!                          |\n"
                        f"\r|  После подтверждения оплаты дождитесь сообщения программы                               |\n"
                        f"\r|  о успешной передаче средств на ваш кошелёк!                                            |\n"
                        f"\r|  Проверка баланса...                                                                    |")
        CURRENTBALANCE = "|  Текущий баланс: "
        WAITING = "Ожидание оплаты..."
        PLEASEADD = "Пожалуйста, добавьте "
        RECEIVED =   "|  Оплата получена: "
        SETUP =      "|  Настройка завершена.                                                                   |"
        SOON =       "|  Пожалуйста, подождите, процесс скоро начнется...                                       |"
        LOADING =    "|------------------------------- Загрузка адресов в память -------------------------------|"
        LOADED =     "|  Загружено "
        ADRESSES = " адресов."
        GOODLUCK = (f"|  Процесс поиска ключа не является быстрым.                                              |\n"
                    f"|  Это может занять дни или даже недели.                                                  |\n"
                    f"|  Все зависит от мощности вашего процессора и удачи.                                     |\n"
                    f"|_________________________________________________________________________________________|\n"
                    f"|                                                                                         |")
        WANNAPAY =  f"|  Хотите купить полную версию программы? Нажмите Enter... (30 секунд)                    |"
        PLEASEPAY = f"|  Для использования программы необходимо произвести оплату.                              |"
        PAYMENTCONFIRMED = ("|  Оплата подтверждена и проверена.                                                       |\n"
                            "|  Запущена полная версия программы.                                                      |")
        PAYNOW = f"|  Вы можете произвести оплату на указанный кошелёк:                                      |"
        PROGRAMPRICE = f"|  Стоимость: "
        PAYMENTWALLET = f"|  Кошелёк для оплаты: "
        PAYMENT_INSTRUCTIONS = (
            f"|  Если вы произвели оплату, не закрывайте программу                                      |\n"
            f"|  до получения подтверждения; иначе средства будут потеряны!                             |\n"
            f"|-----------------------------------------------------------------------------------------|\n"
            f"|  Если программу перезагрузить, для оплаты будет создан                                  |\n"
            f"|  новый кошелёк.                                                                         |\n"
            f"|  Пожалуйста, произведите оплату и дождитесь подтверждения                               |\n"
            f"|  в рамках одной сессии!                                                                 |\n"
            f"|-----------------------------------------------------------------------------------------|\n"
            f"|  После получения оплаты программа автоматически начнёт работу,                          |\n"
            f"|  и сохранит данные об оплате.                                                           |\n"
            f"|  Оплата производится только один раз.                                                   |\n"
            f"|                                                                                         |\n"
            f"|  Перевод может занять 10 минут или дольше.                                              |"
        )
        FREEVERSION = ("|  Запущена бесплатная версия программы.                                                  |\n"
                       "|  Скорость обработки адресов ограничена                                                  |")

    elif language == "Українська":
        # ============== Мовні налаштування для української мови ==============
        FOUND =       "|  Адресу з балансом знайдено!                                                            |"
        ADRESS =      "|  Адреса: "
        BALANCE =     "|  Баланс: "
        SATOSHIS =    " сатоші. "
        WIF =         "|  WIF: "
        CHECK =       "|  Перевірка на блокчейні:                                                                |"
        AUTOMATIC = (f"|  Для отримання ключа від цього гаманця                                                  |\n"
                     f"|  необхідно сплатити комісію у розмірі 10%.                                              |")
        PAYMENTADRESS = "|  Адреса для оплати: "
        FEE = "|  Комісія: "
        CHECKBALANCE = (f"\r|  Не закривайте програму, поки не завершите оплату                                       |\n"
                        f"\r|  та не отримаєте ключ! Інакше дані будуть втрачені!                                     |\n"
                        f"\r|  Після підтвердження оплати зачекайте на повідомлення програми                          |\n"
                        f"\r|  про успішну передачу коштів на вашу адресу!                                            |\n"
                        f"\r|  Перевірка балансу...                                                                   |")
        CURRENTBALANCE = "|  Поточний баланс: "
        WAITING = "Очікування оплати..."
        PLEASEADD = "Будь ласка, додайте "
        RECEIVED = "|  Оплату отримано: "
        SETUP =      "|  Налаштування завершено.                                                                |"
        SOON =       "|  Будь ласка, зачекайте, процес скоро розпочнеться...                                    |"
        LOADING =    "|----------------------------- Завантаження адрес у пам'ять ------------------------------|"
        LOADED = "|  Завантажено "
        ADRESSES = " адрес."
        GOODLUCK = (f"|  Процес пошуку ключа не є швидким.                                                      |\n"
                    f"|  Це може зайняти дні або навіть тижні.                                                  |\n"
                    f"|  Все залежить від потужності вашого процесора та удачі.                                 |\n"
                    f"|_________________________________________________________________________________________|\n"
                    f"|                                                                                         |")
        WANNAPAY =  f"|  Бажаєте придбати повну версію програми? Натисніть Enter... (30 секунд)                 |"
        PLEASEPAY = f"|  Для використання програми необхідно здійснити оплату.                                  |"
        PAYMENTCONFIRMED = (f"|  Оплата підтверджена та перевірена.                                                     |\n"
                            f"|  Запущено повну версію програми.                                                        |")
        PAYNOW = f"|  Ви можете здійснити оплату на вказаний гаманець:                                       |"
        PROGRAMPRICE = f"|  Вартість: "
        PAYMENTWALLET = f"|  Гаманець для оплати: "
        PAYMENT_INSTRUCTIONS = (
            f"|  Якщо ви здійснили оплату, не закривайте програму                                       |\n"
            f"|  до отримання підтвердження; інакше кошти будуть втрачені!                              |\n"
            f"|-----------------------------------------------------------------------------------------|\n"
            f"|  Якщо ви перезапустите програму, для оплати буде створено                               |\n"
            f"|  новий гаманець.                                                                        |\n"
            f"|  Будь ласка, здійсніть оплату та дочекайтеся підтвердження                              |\n"
            f"|  в межах однієї сесії!                                                                  |\n"
            f"|-----------------------------------------------------------------------------------------|\n"
            f"|  Після отримання оплати програма автоматично розпочне роботу,                           |\n"
            f"|  і збережуться дані про оплату.                                                         |\n"
            f"|  Оплату потрібно здійснити лише один раз.                                               |\n"
            f"|                                                                                         |\n"
            f"|  Переказ може зайняти 10 хвилин або довше.                                              |"
        )
        FREEVERSION = ("|  Запущено безкоштовну версію програми.                                                  |\n"
                       "|  Швидкість обробки адрес обмежено                                                       |")


    elif language == "Español":

        # ============== Configuración de idioma para español ==============

        FOUND = "|  ¡Dirección con saldo encontrada!                                                       |"

        ADRESS = "|  Dirección: "

        BALANCE = "|  Saldo: "

        SATOSHIS = " satoshis. "

        WIF = "|  WIF: "

        CHECK = "|  Verificar en la blockchain:                                                            |"

        AUTOMATIC = (f"|  Para obtener la clave de esta cartera                                                  |\n"

                     f"|  se debe pagar una comisión del 10%.                                                    |")

        PAYMENTADRESS = "|  Dirección de pago: "

        FEE = "|  Comisión: "

        CHECKBALANCE = (

            f"\r|  No cierre el programa hasta que complete el pago                                       |\n"

            f"\r|  y reciba la clave. ¡De lo contrario, se perderán los datos!                           |\n"

            f"\r|  Después de la confirmación del pago, espere el mensaje del programa                    |\n"

            f"\r|  sobre la transferencia exitosa de fondos a su dirección.                               |\n"

            f"\r|  Verificando saldo...                                                                   |")

        CURRENTBALANCE = "|  Saldo actual: "

        WAITING = "Esperando el pago..."

        PLEASEADD = "Por favor agregue "

        RECEIVED = "|  Pago recibido: "

        SETUP = "|  Configuración completada.                                                              |"

        SOON = "|  Por favor espere, el proceso comenzará pronto...                                       |"

        LOADING = "|-------------------------- Cargando direcciones en la memoria ---------------------------|"

        LOADED = "|  Cargadas "

        ADRESSES = " direcciones."

        GOODLUCK = (f"|  El proceso de búsqueda de la clave no es rápido.                                       |\n"

                    f"|  Puede tardar días o incluso semanas.                                                   |\n"

                    f"|  Todo depende de la potencia de su procesador y la suerte.                              |\n"

                    f"|_________________________________________________________________________________________|\n"

                    f"|                                                                                         |")

        WANNAPAY = f"|  ¿Desea comprar la versión completa? Presione Enter... (30 segundos)                    |"

        PLEASEPAY = f"|  Para usar el programa, necesita realizar un pago.                                      |"

        PAYMENTCONFIRMED = (
            "|  El pago ha sido confirmado y verificado.                                               |\n"

            "|  La versión completa del programa ha sido iniciada.                                     |")

        PAYNOW = f"|  Puede realizar el pago a la cartera especificada:                                      |"

        PROGRAMPRICE = f"|  Precio: "

        PAYMENTWALLET = f"|  Cartera para pago: "

        PAYMENT_INSTRUCTIONS = (

            f"|  Si ya ha realizado el pago, no cierre el programa                                      |\n"

            f"|  hasta recibir la confirmación; de lo contrario, se perderán los fondos.                |\n"

            f"|-----------------------------------------------------------------------------------------|\n"

            f"|  Si reinicia el programa, se generará una nueva cartera para el pago.                   |\n"

            f"|  Por favor, complete el pago y espere la confirmación                                   |\n"

            f"|  dentro de la misma sesión.                                                             |\n"

            f"|-----------------------------------------------------------------------------------------|\n"

            f"|  Una vez recibido el pago, el programa comenzará a funcionar automáticamente            |\n"

            f"|  y la información del pago se guardará.                                                 |\n"

            f"|  El pago se realiza solo una vez.                                                       |\n"

            f"|                                                                                         |\n"

            f"|  La transferencia puede tardar 10 minutos o más.                                        |")

        FREEVERSION = ("|  Se ha iniciado la versión gratuita del programa.                                       |\n"

                       "|  La velocidad de procesamiento está limitada                                            |")
    elif language == "Deutsch":
        # ============== Spracheinstellungen für Deutsch ==============
        FOUND = "|  Adresse mit Guthaben gefunden!                                                         |"
        ADRESS = "|  Adresse: "
        BALANCE = "|  Guthaben: "
        SATOSHIS = " Satoshis. "
        WIF = "|  WIF: "
        CHECK = "|  Auf Blockchain prüfen:                                                                 |"
        AUTOMATIC = (f"|  Um den Schlüssel für diese Wallet zu erhalten,                                         |\n"
                     f"|  ist eine Gebühr von 10 % erforderlich.                                                 |")
        PAYMENTADRESS = "|  Zahlungsadresse: "
        FEE = "|  Gebühr: "
        CHECKBALANCE = (
            f"\r|  Schließen Sie das Programm nicht, bevor Sie die Zahlung abgeschlossen haben            |\n"
            f"\r|  und den Schlüssel erhalten! Andernfalls gehen Daten verloren!                          |\n"
            f"\r|  Nach Zahlungsbestätigung warten Sie bitte auf die Nachricht des Programms              |\n"
            f"\r|  über die erfolgreiche Überweisung auf Ihre Wallet-Adresse!                             |\n"
            f"\r|  Guthaben wird überprüft...                                                             |")
        CURRENTBALANCE = "|  Aktuelles Guthaben: "
        WAITING = "Warten auf Zahlung..."
        PLEASEADD = "Bitte fügen Sie hinzu "
        RECEIVED = "|  Zahlung empfangen: "
        SETUP = "|  Einrichtung abgeschlossen.                                                             |"
        SOON =  "|  Bitte warten Sie, der Vorgang beginnt in Kürze...                                      |"
        LOADING = "|---------------------------- Lade Adressen in den Speicher ------------------------------|"
        LOADED = "|  Geladen: "
        ADRESSES = " Adressen."
        GOODLUCK = (f"|  Der Schlüsselsuchvorgang ist nicht schnell.                                            |\n"
                    f"|  Es kann Tage oder sogar Wochen dauern.                                                 |\n"
                    f"|  Es hängt alles von der Leistung Ihres Prozessors und Ihrem Glück ab.                   |\n"
                    f"|_________________________________________________________________________________________|\n"
                    f"|                                                                                         |")
        WANNAPAY = f"|  Möchten Sie die Vollversion kaufen? Drücken Sie Enter... (30 Sekunden)                 |"
        PLEASEPAY = f"|  Um das Programm zu nutzen, ist eine Zahlung erforderlich.                              |"
        PAYMENTCONFIRMED = ("|  Zahlung wurde bestätigt und verifiziert.                                               |\n"
                             "|  Vollversion des Programms wurde gestartet.                                             |")
        PAYNOW = f"|  Sie können die Zahlung an die angegebene Wallet senden:                                |"
        PROGRAMPRICE = f"|  Preis: "
        PAYMENTWALLET = f"|  Wallet für Zahlung: "
        PAYMENT_INSTRUCTIONS = (
            f"|  Wenn Sie bereits bezahlt haben, schließen Sie das Programm nicht,                      |\n"
            f"|  bevor Sie eine Bestätigung erhalten; andernfalls gehen Ihre Mittel verloren!           |\n"
            f"|-----------------------------------------------------------------------------------------|\n"
            f"|  Wenn Sie das Programm neu starten, wird eine neue Wallet für die Zahlung erzeugt.      |\n"
            f"|  Bitte führen Sie die Zahlung innerhalb derselben Sitzung durch                         |\n"
            f"|  und warten Sie auf die Bestätigung.                                                    |\n"
            f"|-----------------------------------------------------------------------------------------|\n"
            f"|  Nach Zahlungseingang startet das Programm automatisch                                  |\n"
            f"|  und speichert die Zahlungsinformationen.                                               |\n"
            f"|  Die Zahlung ist nur einmal erforderlich.                                               |\n"
            f"|                                                                                         |\n"
            f"|  Die Überweisung kann 10 Minuten oder länger dauern.                                    |")
        FREEVERSION = ("|  Die kostenlose Version des Programms wurde gestartet.                                  |\n"
                       "|  Die Verarbeitungsgeschwindigkeit ist begrenzt                                          |")
    elif language == "Français":
        # ============== Paramètres linguistiques pour le français ==============
        FOUND =        "|  Adresse avec solde trouvée !                                                           |"
        ADRESS = "|  Adresse : "
        BALANCE = "|  Solde : "
        SATOSHIS = " satoshis. "
        WIF = "|  WIF : "
        CHECK =       "|  Vérifier sur la blockchain :                                                           |"
        AUTOMATIC = (f"|  Pour obtenir la clé de ce portefeuille,                                                |\n"
                     f"|  un paiement de 10 % est requis.                                                        |")
        PAYMENTADRESS = "|  Adresse de paiement : "
        FEE = "|  Frais : "
        CHECKBALANCE = (
            f"\r|  Ne fermez pas le programme tant que le paiement n’est pas effectué                     |\n"
            f"\r|  et que la clé n’est pas reçue ! Sinon, les données seront perdues.                     |\n"
            f"\r|  Après confirmation du paiement, attendez le message du programme                       |\n"
            f"\r|  indiquant le transfert réussi vers votre adresse.                                      |\n"
            f"\r|  Vérification du solde...                                                               |")
        CURRENTBALANCE = "|  Solde actuel : "
        WAITING = "En attente du paiement..."
        PLEASEADD = "Veuillez ajouter "
        RECEIVED = "|  Paiement reçu : "
        SETUP =   "|  Configuration terminée.                                                                |"
        SOON =    "|  Veuillez patienter, le processus va bientôt commencer...                               |"
        LOADING = "|---------------------------- Chargement des adresses en mémoire -------------------------|"
        LOADED = "|  Chargées : "
        ADRESSES = " adresses."
        GOODLUCK = (f"|  Le processus de recherche de clé n’est pas rapide.                                     |\n"
                    f"|  Cela peut prendre des jours, voire des semaines.                                       |\n"
                    f"|  Tout dépend de la puissance de votre processeur et de la chance.                       |\n"
                    f"|_________________________________________________________________________________________|\n"
                    f"|                                                                                         |")
        WANNAPAY =  f"|  Vous souhaitez acheter la version complète ? Appuyez sur Entrée... (30 secondes)       |"
        PLEASEPAY = f"|  Pour utiliser le programme, vous devez effectuer un paiement.                          |"
        PAYMENTCONFIRMED = ("|  Paiement confirmé et vérifié.                                                          |\n"
                            "|  Version complète du programme lancée.                                                  |")
        PAYNOW = f"|  Vous pouvez effectuer le paiement à l’adresse suivante :                               |"
        PROGRAMPRICE = f"|  Prix : "
        PAYMENTWALLET = f"|  Portefeuille de paiement : "
        PAYMENT_INSTRUCTIONS = (
            f"|  Si vous avez effectué le paiement, ne fermez pas le programme                          |\n"
            f"|  avant la confirmation ; sinon, les fonds seront perdus.                                |\n"
            f"|-----------------------------------------------------------------------------------------|\n"
            f"|  Si vous redémarrez le programme, un nouveau portefeuille sera généré.                  |\n"
            f"|  Veuillez finaliser le paiement et attendre la confirmation                             |\n"
            f"|  dans la même session.                                                                  |\n"
            f"|-----------------------------------------------------------------------------------------|\n"
            f"|  Une fois le paiement reçu, le programme démarrera automatiquement                      |\n"
            f"|  et les informations de paiement seront enregistrées.                                   |\n"
            f"|  Le paiement est requis une seule fois.                                                 |\n"
            f"|                                                                                         |\n"
            f"|  Le transfert peut prendre 10 minutes ou plus.                                          |")
        FREEVERSION = ("|  La version gratuite du programme a été lancée.                                         |\n"
                       "|  La vitesse de traitement des adresses est limitée                                      |")
    elif language == "Português":
        # ============== Configurações de idioma para português ==============
        FOUND = "|  Endereço com saldo encontrado!                                                         |"
        ADRESS = "|  Endereço: "
        BALANCE = "|  Saldo: "
        SATOSHIS = " satoshis. "
        WIF = "|  WIF: "
        CHECK =       "|  Verificar na blockchain:                                                               |"
        AUTOMATIC = (f"|  Para obter a chave desta carteira,                                                     |\n"
                     f"|  é necessário pagar uma taxa de 10%.                                                    |")
        PAYMENTADRESS = "|  Endereço para pagamento: "
        FEE = "|  Taxa: "
        CHECKBALANCE = (
            f"\r|  Não feche o programa até concluir o pagamento                                          |\n"
            f"\r|  e receber a chave! Caso contrário, os dados serão perdidos!                            |\n"
            f"\r|  Após a confirmação do pagamento, aguarde a mensagem do programa                        |\n"
            f"\r|  sobre a transferência bem-sucedida para sua carteira!                                  |\n"
            f"\r|  Verificando saldo...                                                                   |")
        CURRENTBALANCE = "|  Saldo atual: "
        WAITING = "Aguardando pagamento..."
        PLEASEADD = "Por favor, adicione "
        RECEIVED = "|  Pagamento recebido: "
        SETUP =              "|  Configuração concluída.                                                                |"
        SOON =               "|  Aguarde, o processo começará em breve...                                               |"
        LOADING =            "|-------------------------- Carregando endereços na memória ------------------------------|"
        LOADED = "|  Carregados: "
        ADRESSES = " endereços."
        GOODLUCK =         (f"|  O processo de busca da chave não é rápido.                                             |\n"
                            f"|  Pode levar dias ou até semanas.                                                        |\n"
                            f"|  Tudo depende da potência do seu processador e da sorte.                                |\n"
                            f"|_________________________________________________________________________________________|\n"
                            f"|                                                                                         |")
        WANNAPAY =          f"|  Deseja comprar a versão completa? Pressione Enter... (30 segundos)                     |"
        PLEASEPAY =         f"|  Para usar o programa, é necessário realizar um pagamento.                              |"
        PAYMENTCONFIRMED =  ("|  Pagamento confirmado e verificado.                                                     |\n"
                             "|  A versão completa do programa foi iniciada.                                            |")
        PAYNOW =            f""
        PROGRAMPRICE =      f"|  Preço: "
        PAYMENTWALLET =     f"|  Carteira para pagamento: "
        PAYMENT_INSTRUCTIONS = (
            f"|  Se você já realizou o pagamento, não feche o programa                                  |\n"
            f"|  antes de receber a confirmação; caso contrário, os fundos serão perdidos.              |\n"
            f"|-----------------------------------------------------------------------------------------|\n"
            f"|  Se você reiniciar o programa, uma nova carteira será gerada para pagamento.            |\n"
            f"|  Conclua o pagamento e aguarde a confirmação                                            |\n"
            f"|  na mesma sessão.                                                                       |\n"
            f"|-----------------------------------------------------------------------------------------|\n"
            f"|  Assim que o pagamento for recebido, o programa iniciará automaticamente                |\n"
            f"|  e as informações de pagamento serão salvas.                                            |\n"
            f"|  O pagamento é feito apenas uma vez.                                                    |\n"
            f"|                                                                                         |\n"
            f"|  A transferência pode levar 10 minutos ou mais.                                         |")
        FREEVERSION =  ("|  A versão gratuita do programa foi iniciada.                                            |\n"
                        "|  A velocidade de processamento dos endereços é limitada                                 |")
    elif language == "Türkçe":
        # ============== Türkçe dil ayarları ==============
        FOUND = "|  Bakiyesi olan bir adres bulundu!                                                       |"
        ADRESS = "|  Adres: "
        BALANCE = "|  Bakiye: "
        SATOSHIS = " satoshi. "
        WIF = "|  WIF: "
        CHECK = "|  Blockchain'de kontrol et:                                                              |"
        AUTOMATIC = (f"|  Bu cüzdanın anahtarını almak için                                                      |\n"
                     f"|  %10 oranında bir ücret ödemeniz gerekiyor.                                             |")
        PAYMENTADRESS = "|  Ödeme adresi: "
        FEE = "|  Ücret: "
        CHECKBALANCE = (
            f"\r|  Ödeme tamamlanana ve anahtar alınana kadar programı kapatmayın                         |\n"
            f"\r|  Aksi halde veriler kaybolur!                                                           |\n"
            f"\r|  Ödeme onaylandıktan sonra, programın başarılı transfer mesajını bekleyin               |\n"
            f"\r|  Cüzdan adresinize gönderilen fonları bildirecektir.                                    |\n"
            f"\r|  Bakiye kontrol ediliyor...                                                             |")
        CURRENTBALANCE = "|  Güncel bakiye: "
        WAITING = "Ödeme bekleniyor..."
        PLEASEADD = "Lütfen ekleyin "
        RECEIVED = "|  Ödeme alındı: "
        SETUP =   "|  Kurulum tamamlandı.                                                                    |"
        SOON =    "|  Lütfen bekleyin, işlem yakında başlayacak...                                           |"
        LOADING = "|------------------------------ Adresler belleğe yükleniyor ------------------------------|"
        LOADED = "|  Yüklenen: "
        ADRESSES = " adres."
        GOODLUCK = (f"|  Anahtar arama işlemi hızlı değildir.                                                   |\n"
                    f"|  Günler hatta haftalar sürebilir.                                                       |\n"
                    f"|  İşlem gücü ve şansa bağlıdır.                                                          |\n"
                    f"|_________________________________________________________________________________________|\n"
                    f"|                                                                                         |")
        WANNAPAY = f"|  Tam sürümü satın almak ister misiniz? Enter tuşuna basın... (30 saniye)                |"
        PLEASEPAY = f"|  Programı kullanmak için ödeme yapmanız gerekiyor.                                      |"
        PAYMENTCONFIRMED = ("|  Ödeme onaylandı ve doğrulandı.                                                         |\n"
                             "|  Programın tam sürümü başlatıldı.                                                       |")
        PAYNOW = f"|  Ödemeyi aşağıdaki cüzdan adresine yapabilirsiniz:                                      |"
        PROGRAMPRICE = f"|  Fiyat: "
        PAYMENTWALLET = f"|  Ödeme cüzdanı: "
        PAYMENT_INSTRUCTIONS = (
            f"|  Ödeme yaptıysanız, onay alınana kadar programı kapatmayın                              |\n"
            f"|  Aksi halde fonlar kaybolur.                                                            |\n"
            f"|-----------------------------------------------------------------------------------------|\n"
            f"|  Programı yeniden başlatırsanız, yeni bir ödeme cüzdanı oluşturulur.                    |\n"
            f"|  Aynı oturum içinde ödemeyi tamamlayın ve onayı bekleyin.                               |\n"
            f"|-----------------------------------------------------------------------------------------|\n"
            f"|  Ödeme alındığında program otomatik olarak başlayacak                                   |\n"
            f"|  ve ödeme bilgileri kaydedilecektir.                                                    |\n"
            f"|  Ödeme sadece bir kez yapılır.                                                          |\n"
            f"|                                                                                         |\n"
            f"|  Transfer 10 dakika veya daha uzun sürebilir.                                           |")
        FREEVERSION = ("|  Programın ücretsiz sürümü başlatıldı.                                                  |\n"
                       "|  Adres işleme hızı sınırlıdır                                                           |")

PRICE = int(10000)


def generate_payment_hash():
    secret_code = 0
    pass

def payment_verification():
    global num_processes
    if os.path.exists(PAYMENT_FILE):
        # Проверяем подлинность оплаты
        with open(PAYMENT_FILE, "r") as file:
            saved_hash = file.read().strip()
        current_hash = generate_payment_hash()

        if saved_hash == current_hash:
            time.sleep(3)
            print(PAYMENTCONFIRMED)
            num_processes = os.cpu_count()
            return
        else:
            num_processes = os.cpu_count() // 2
            pass

    print("\n" * 100)
    cryptomar()
    print(PLEASEPAY)
    print(f"{PROGRAMPRICE}{PRICE}{SATOSHIS}{' ' * (90 - len(f'{PROGRAMPRICE}{PRICE}{SATOSHIS}'))}|")
    print(PAYNOW)


    # Генерация адреса для оплаты
    payment_priv_key = CryptoMar.get_priv_key()
    payment_wif, _ = CryptoMar.get_wif(payment_priv_key)
    payment_wallet = CryptoMar.get_bech32(payment_priv_key)

    print("|-----------------------------------------------------------------------------------------|")
    print(f"{PAYMENTWALLET}{payment_wallet}{' ' * (90 - len(f'{PAYMENTWALLET}' + payment_wallet))}|")
    print(PAYMENT_INSTRUCTIONS)
    print("|-----------------------------------------------------------------------------------------|")

    while True:
        balance = check_balance(payment_wallet)
        f = f"{BALANCE}{balance}{SATOSHIS}{WAITING}"
        sys.stdout.write(f"\r{f}{' '*(90 - len(f))}|")
        sys.stdout.flush()

        if balance >= PRICE:
            print(PAYMENTCONFIRMED)
            num_processes = os.cpu_count()
            "Тут реалізовано відправлення коштів за програму автору"

            # Сохранение подтверждения оплаты с хешем системы
            with open(PAYMENT_FILE, "w") as file:
                file.write(generate_payment_hash())
            break
        else:
            time.sleep(30)

def wait_for_input_or_timeout(timeout):
    """
    Чекає на Enter або тайм-аут.
    Повертає True, якщо Enter натиснуто, False — якщо сплив таймер.
    """
    q = queue.Queue()

    def read_input():
        try:
            input()
            q.put(True)  # Користувач натиснув Enter
        except:
            q.put(False)

    thread = threading.Thread(target=read_input)
    thread.daemon = True
    thread.start()

    try:
        return q.get(timeout=timeout)
    except queue.Empty:
        return False  # Тайм-аут


def ask():
    global num_processes

    if os.path.exists(PAYMENT_FILE):
        with open(PAYMENT_FILE, "r") as file:
            saved_hash = file.read().strip()
        current_hash = generate_payment_hash()

        if saved_hash == current_hash:
            print(PAYMENTCONFIRMED)
            num_processes = os.cpu_count()
            return

    # Питаємо про оплату
    print(WANNAPAY)
    sys.stdout.flush()

    pressed_enter = wait_for_input_or_timeout(30)

    if pressed_enter:
        payment_verification()  # запустити перевірку оплати
    else:
        print(FREEVERSION)
        num_processes = os.cpu_count() // 2  # безкоштовний режим

def input_with_timeout(prompt, timeout=30):
    q = queue.Queue()

    def read_input():
        print(prompt, end='', flush=True)
        try:
            user_input = input()
        except Exception:
            user_input = ""
        q.put(user_input.strip())

    thread = threading.Thread(target=read_input)
    thread.daemon = True
    thread.start()

    try:
        return q.get(timeout=timeout)
    except queue.Empty:
        # Тайм-аут — обираємо мову автоматично за країною
        country = get_country()
        if country == "UA":
            return "3"
        elif country == "RU":
            return "2"
        else:
            return "1"

def print_banner():
    print(f"""|_________________________________________________________________________________________|
|====================================== Welcome to =======================================|
|                                        ᴄʀʏᴘᴛᴏᴍᴀʀ                                        |
|====================================== Version 1.1 ======================================|
|                                                                                         |""")
    d = f"|  Rate: 1 BTC = {get_bitcoin_price()} USD. ({datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')})"
    print(f"{d}{' ' * (90 - len(d))}|")

def print_running_banner():
    print(f"""|====================================== In Progress ======================================|
|                                        ᴄʀʏᴘᴛᴏᴍᴀʀ                                        |
|====================================== Version 1.1 ======================================|""")

# === Завантаження адрес у пам'ять з використанням Memory Mapping ===
def load_addresses():
    with open(FILE_PATH, 'r') as f:
        addresses = {line.split()[0] for line in f}
    return addresses

    # === Збереження знайдених пар ключ - адреса у файл ===

# === Перевірка балансу через API ===
def check_balance(address):
    try:
        response = requests.get(f'{BLOCKSTREAM_API}{address}')
        if response.status_code == 200:
            data = response.json()
            balance = data.get('chain_stats', {}).get('funded_txo_sum', 0) - data.get('chain_stats', {}).get('spent_txo_sum', 0)
            return balance
    except Exception as e:
        print(f'|  Error retrieving balance                                           |')
    return 0


def get_bitcoin_price():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        data = response.json()
        price = data['bitcoin']['usd']
        return price
    except Exception as e:
        return 100000


# === Основний потік ===
def worker(counter, found, address_shm_name, address_size):
    existing_shm = shared_memory.SharedMemory(name=address_shm_name)
    address_bytes = existing_shm.buf[:address_size]
    address_set = set(address_bytes.tobytes().decode().splitlines())

    local_counter = 0
    while not found.value:
        priv_key = CryptoMar.get_priv_key()
        adress = CryptoMar.get_bech32(priv_key)

        if adress in address_set:
            wif, _ = CryptoMar.get_wif(priv_key)
            balance = check_balance(adress)
            massage = f"|===== FOUND =====|\n|---- ADRESS -----|\n{adress}\n|---- BALANCE ----|\n{balance} sat.\n|------ WIF ------|\n{wif}\n|=================|"
            print(massage)

        # Збільшення показнику швидкості і обробки для версії 1.2
        local_counter += 2

        # Менше блокувань
        if local_counter >= 1:
            with counter.get_lock():
                counter.value += local_counter
            local_counter = 0

    # Додаємо залишок локального лічильника після завершення
    with counter.get_lock():
        counter.value += local_counter


if __name__ == '__main__':
    counter = Value('i', 0, lock=True)
    found = Value('b', False)
    start_time = time.time()
    get_language()
    ask()
    print_banner()

    print(SETUP)
    print(SOON)
    print("|                                                                                         |")
    print(LOADING)
    address_set = load_addresses()
    e = f"{LOADED}{len(address_set)}{ADRESSES}"
    print(f"{e}{' '*(90-len(e))}|")
    print(f"|-----------------------------------------------------------------------------------------|")
    print(f"|                                                                                         |")
    print_running_banner()

    print(GOODLUCK)


    # === Зберігаємо адреси у спільній пам'яті ===
    address_str = '\n'.join(address_set)
    address_bytes = address_str.encode()
    shm = shared_memory.SharedMemory(create=True, size=len(address_bytes))
    shm.buf[:len(address_bytes)] = address_bytes

# =================== Налаштування джекпотів ===================
    # Набір гаманців та ключів наживок
    bait_adresess_and_wifs = \
        [
            ("bc1qg29k0xr0ql2efdczqktnksrlxadfxy36n8u8vd", "L16vFFpJQ918bGQ9rThEzk2NUAgo7XRnkh3e9zZrtq7FHeyEBbQH"),
            ("bc1qlk2ks63zrrcx2h06e6ejmp3hgfuzv0gmuvgv7u", "L1AHZbKxe4EBfTkEQYyQHRkjw7Yza2anp3hwqWCdjS2cUXAhKvwr"),
            ("bc1q3kv0slj624kwg72k6qrq0f44hyx3ll5p5r2pa8", "L1wCH9BxvY5cxfU9Fu3nCYcfnpBy3yEpnhwXBtewxesi7NRv6rrB")
        ]

    jackpot_adresess_and_wifs = \
        [
            ("bc1q0000005259fzmctd5xp7afs07dec5kxmp3fwgw", CryptoMar.get_wif()),
            ("bc1q0002phghjxrk327w5rpej05vtu5uamplj0c4d4", CryptoMar.get_wif()),
            ("bc1q0003knz5uk0pdcha0529u56xu093ntkkglwuqg", CryptoMar.get_wif()),
            ("bc1q03g870h3ln0xshlxwvr5jr6h6vxysx9ua9jynt", CryptoMar.get_wif()),
            ("bc1q03g8fkxu8xha5j3ekaesqkd9wnexe7kh0r4af9", CryptoMar.get_wif()),
            ("bc1q03g8nc0ujguxvvn5vfv7t23jv7rg0pvh3f4ucn", CryptoMar.get_wif()),
            ("bc1q03g9jg8ee3j47mpf6qvyskq6u2tup49d9lplqp", CryptoMar.get_wif()),
        ]

    # Створюємо процес для пошуку з аргументами
    processes = [
        Process(target=worker, args=(counter, found, shm.name, len(address_bytes)))
        for _ in range(num_processes)
    ]

    for p in processes:
        p.start()

    with tqdm(
            total=0,
            unit=' addresses',
            dynamic_ncols=False,
            bar_format="| {rate_fmt:<40}   Total: {n:<37} |".ljust(0),
            position=0,
            leave=True
    ) as pbar:
        while not found.value:

            # Оновлюємо прогрес
            pbar.n = counter.value
            pbar.refresh()
            time.sleep(2)



    for p in processes:
        p.join()

    # Звільняємо Shared Memory
    shm.close()
    shm.unlink()
