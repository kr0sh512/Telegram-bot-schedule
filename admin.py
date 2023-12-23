import schedules as bot

admin_id = '856850518'

def admin_command(func):
    def wrapper(*args, **kwargs):
        message = args[0]
        if str(message.from_user.id) != admin_id:
            bot.send_message(message.from_user.id, 'Команда доступна только администратору')            
            return

        func(*args, **kwargs)
        return

    return wrapper

def is_admin(message):
    if str(message.from_user.id) == admin_id and message.from_user.id == message.chat.id:
        return True
    
    return False

def send_admin_message(text):
    bot.send_message(admin_id, '🛑 ' + text)
    
def send_admin_document(file):
    bot.send_document(admin_id, file, '🛑 Admin file')   
    