#config.py
#pytelegrambotapi - библиотека для телеграм бота
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL' : 'https://amigopizza-9eaba.firebaseio.com'
})


token = '384499767:AAGzeusXxbfqfqc3i8isAUa3iPzouTfwxac'
