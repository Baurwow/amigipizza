#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config, telebot, requests, firebase_admin
from firebase_admin import db
from telebot import types

from flask import Flask, request

bot = telebot.TeleBot(config.token, threaded=False)

server = Flask(__name__)


@bot.message_handler(commands=["start"])
def start(message):
	root = db.reference('/Меню')
	menu = root.get()

	markup = types.ReplyKeyboardMarkup()
	print(menu)

	for key in menu:
		menu1 = types.KeyboardButton(key)
		markup.row(menu1)
	bot.send_message(message.chat.id, "Привет! Я АмигоПиццаБот.\nЯ помогу Вам заказать еду .\nПожалуйста выберите категорию:", reply_markup=markup)

@bot.message_handler(commands=["post"])
def post(message):
	user_id = message.from_user.id
	admin = db.reference('/users/'+str(user_id)+'/admin').get()
	if admin == True:
		spisok = db.reference("/users/").get()
		for key in spisok:
			print(key)
			bot.send_message(key, str(message.text[5:]))


@bot.message_handler(content_types=["contact"])
def con(message):
	user_id = message.from_user.id
	print(message)
	
	db.reference("/users/"+str(user_id)).update({'phone': message.contact.phone_number})
	if message.contact.first_name:
		db.reference("/users/"+str(user_id)).update({'first_name': message.contact.first_name})
	if message.chat.username:
		db.reference("/users/"+str(user_id)).update({'login': message.chat.username})
		order = db.reference("/users/"+str(user_id)+str("/basket")).get()
		adres = db.reference("/users/" + str(user_id) + "/adres").get()
		tip = db.reference("/users/"+str(user_id)+'/tip').get()
	if adres == None:
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.row('Отправить заказ')
		markup.row('✖️Очистить заказ')
		markup.row('↩️Назад в Меню')
		bot.send_message(message.chat.id, "А теперь остался последний шаг,Напишите свой адрес и на какое время(в такой очередности: Улица,Дом,Подъезд,Этаж,Кв,и время):", reply_markup=markup)
		db.reference("/users/"+str(user_id)).update({'previous': "Адрес"})
	else:
		tmp = ""
		total = 0
		for key, value in order.items():
			total = total + value["count"] * value["price"]
			tmp = tmp + key + " = " + str(value["count"]) + " x " + str(value["price"]) + " = " + str(value["count"] * value["price"])  + " тенге \n"
		bot.send_message("390370994", tmp + "\nВсего: " + str(total) + " тенге \nОт: " + str(message.contact.phone_number) + " @" +  str(message.chat.username) + ', адрес и время:'+str(adres))
		bot.send_message(message.chat.id, "Спасибо,  Ваш заказ отправлен,пожалуйста дождитесь звонка оператора! ")
		db.reference("/users/"+str(user_id)+"/basket").delete()
		db.reference("/users/"+str(user_id)+"/adres").delete()
		db.reference("/users/"+str(user_id)+'/tip').delete()

@bot.message_handler(content_types=["text"])
def answer(message): 
	user_id = message.from_user.id
	menu = db.reference('/Меню').get()
	current = db.reference('/users/'+str(user_id) + "/current").get()
	admin = db.reference('/users/'+str(user_id)+'/admin').get()

	 
	if message.text == "Добавить в корзину":
		dish = db.reference("/users/"+str(user_id)+'/current_dish').get()
		if (current == "Пицца"):
			tip = db.reference("/users/"+str(user_id)+'/tip').get()
			count = db.reference("/users/"+str(user_id)+"/basket/" + current + ": " +dish+ ","+ " тесто: " + tip + "/count").get()
			price = db.reference("/users/"+str(user_id)+"/basket/" + current + ": " +dish+ ","+ " тесто: " + tip + "/price").get()
		else:
			count = db.reference("/users/"+str(user_id)+"/basket/" + current + ": " +dish + "/count").get()
			price = db.reference("/users/"+str(user_id)+"/basket/" + current + ": " +dish + "/price").get()
		print(count)
		if count == None:
			if (current == "Пицца"):
				db.reference("/users/"+str(user_id)+"/basket/" + current + ": " +dish+ ","+ " тесто: " + tip).update({"count": 1, 'price': db.reference("/users/"+str(user_id) + '/current_price').get()})
			else:
				db.reference("/users/"+str(user_id)+"/basket/" + current + ": " +dish).update({"count": 1, 'price': db.reference("/users/"+str(user_id) + '/current_price').get()})
		else:
			if (current == "Пицца"):
				db.reference("/users/"+str(user_id)+"/basket/" + current + ": " +dish+ ","+ " тесто: " + tip).update({"count": count + 1})
			else:
				db.reference("/users/"+str(user_id)+"/basket/" + current + ": " +dish).update({"count": count + 1})

		bot.send_message(message.chat.id, dish + " добавлено в корзину")
	elif message.text == "Корзина":
		order = db.reference("/users/"+str(user_id)+str("/basket")).get()
		if order == None:
			markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
			markup.row('↩️Назад в Меню')
			bot.send_message(message.chat.id, "Корзина пуста", reply_markup=markup)
		else:
			markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
			print(order)
			markup.row('Отправить заказ')
			markup.row('✖️Очистить заказ')
			markup.row('↩️Назад в Меню')
			bot.send_message(message.chat.id, "Ваш заказ: \n")
			tmp = ""
			total = 0
			for key, value in order.items():
				total = total + value["count"] * value["price"]
				tmp = tmp + key + " = " + str(value["count"]) + " x " + str(value["price"]) + " = " + str(value["count"] * value["price"])  + " тенге \n"
			bot.send_message(message.chat.id, tmp + "\nВсего: " + str(total) + " тенге" + " (Без учета Акции,если Вы заказали по Акции)", reply_markup=markup)
	elif message.text == "Отправить заказ":
		phone = db.reference("/users/" + str(user_id) + "/phone").get()
		login = db.reference("/users/" + str(user_id) + "/login").get()
		first_name = db.reference("/users/" + str(user_id) + "/first_name").get()
		adres = db.reference("/users/" + str(user_id) + "/adres").get()
		tip = db.reference("/users/"+str(user_id)+'/tip').get()

		if phone == None and login == None:
			keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
			button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
			back_menu = types.KeyboardButton(text="↩️Назад в Меню",)
			keyboard.row(button_phone, back_menu)
			bot.send_message(message.chat.id, "Отправьте мне свой номер телефона для отправки заказа!", reply_markup=keyboard)
		elif adres == None:
			bot.send_message(message.chat.id, "А теперь остался последний шаг,Напишите свой адрес и на какое время(в такой очередности: Улица,Дом,Подъезд,Этаж,Кв,и время):")
			db.reference("/users/"+str(user_id)).update({'previous': "Адрес"})
		else:
			order = db.reference("/users/"+str(user_id)+str("/basket")).get()


			tmp = ""
			total = 0
			for key, value in order.items():
				total = total + value["count"] * value["price"]
				tmp = tmp + key + " = " + str(value["count"]) + " x " + str(value["price"]) + " = " + str(value["count"] * value["price"])  + " тенге \n"
			bot.send_message("390370994", tmp + "\nВсего: " + str(total) + " тенге \nОт: " + str(phone) + " @" + str(login) + ", адрес и время:" + str(adres))
			bot.send_message(message.chat.id, "Спасибо,  Ваш заказ отправлен,пожалуйста дождитесь звонка оператора!")
			db.reference("/users/"+str(user_id)+"/basket").delete()
			db.reference("/users/"+str(user_id)+"/adres").delete()
			db.reference("/users/"+str(user_id)+'/tip').delete()
	elif message.text == "✖️Очистить заказ":
		db.reference("/users/"+str(user_id)+"/basket").delete()
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.row('↩️Назад в Меню')
		bot.send_message(message.chat.id, " Ваша корзина очищена", reply_markup=markup)
	elif message.text == "↩️Назад":
		root = db.reference("/Меню/" + current)
		dishes = root.get()
		markup = types.ReplyKeyboardMarkup()
		for key in dishes:
			btn = types.KeyboardButton(key)
			markup.row(btn)
		markup.row('↩️Назад в Меню')
		bot.send_message(message.chat.id, "Выберите блюдо", reply_markup=markup)

	elif message.text == 'Скрыть':
		dish = db.reference("/users/"+str(user_id)+'/current_dish').get()

		if admin == True:
			dish = db.reference("/Меню/" + current + '/' + dish).update({'enabled': False})
			bot.send_message(message.chat.id, "Блюдо скрыто")
	elif message.text == 'Показать':
		dish = db.reference("/users/"+str(user_id)+'/current_dish').get()
		if admin == True:
			dish = db.reference("/Меню/" + current + '/' + dish).update({'enabled': True})
			bot.send_message(message.chat.id, "Блюдо открыто")
	else:
		previous = db.reference("/users/" + str(user_id) + "/previous").get()
		if previous == "Адрес":
			db.reference("/users/"+str(user_id)).update({'adres': message.text})
			bot.send_message(message.chat.id, "Спасибо,  адрес и время добавлено!\nА теперь нажмите кнопку \"отправить заказ\".")
			db.reference("/users/"+str(user_id)).update({'previous': ""})
			markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
			order = db.reference("/users/"+str(user_id)+str("/basket")).get()

			markup.row('Отправить заказ')
			markup.row('✖️Очистить заказ')
			markup.row('↩️Назад в Меню')
			bot.send_message(message.chat.id, "Ваш заказ: \n")
			tmp = ""
			total = 0
			for key, value in order.items():
				total = total + value["count"] * value["price"]
				tmp = tmp + key + " = " + str(value["count"]) + " x " + str(value["price"]) + " = " + str(value["count"] * value["price"])  + " тенге \n"
			bot.send_message(message.chat.id, tmp + "\nВсего: " + str(total) + " тенге" + " (Без учета Акции,если Вы заказали по Акции)", reply_markup=markup)
			
			
	if current:
		root = db.reference("/Меню/" + current)
		ctg = root.get()

		if message.text in ctg:
			name = message.text
			dish = db.reference("/Меню/" + current + "/" + name).get()
			db.reference("/users/"+str(user_id)).update({'current_dish': name})
			db.reference("/users/"+str(user_id)).update({'current_price': dish['cena']})

			markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
			if admin == True:
				markup.row('Скрыть','Показать')

				
			if current == 'Пицца':
				markup.row("Традиционное", "Тонкое")
				markup.row('↩️Назад')
				bot.send_message(message.chat.id, dish["info"])
				bot.send_message(message.chat.id, dish["price"])
				bot.send_message(message.chat.id, dish["img"])
				bot.send_message(message.chat.id, "Выберите тип теста:", reply_markup=markup)

			else:
				markup.row('Добавить в корзину','Корзина')
				markup.row('↩️Назад', '↩️Назад в Меню')


				bot.send_message(message.chat.id, dish["info"])
				bot.send_message(message.chat.id, dish["price"])
				bot.send_message(message.chat.id, dish["img"], reply_markup=markup)
	
	if message.text == "Традиционное":
		testo=message.text
		tip = db.reference("/users/"+str(user_id)).update({'tip':testo})
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.row('Добавить в корзину')
		markup.row('↩️Назад', 'Корзина')
		bot.send_message(message.chat.id, "Тесто выбрано", reply_markup=markup)
	elif message.text == "Тонкое":
		testo=message.text
		tip = db.reference("/users/"+str(user_id)).update({'tip':testo})
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.row('Добавить в корзину')
		markup.row('↩️Назад', 'Корзина')
		bot.send_message(message.chat.id, "Тесто выбрано", reply_markup=markup)
	if message.text in menu:
		category = message.text
		db.reference("/users/"+str(user_id)).update({'current': category})
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		root = db.reference("/Меню/" + category)
		dish = root.get()
		for key, value in dish.items():
			if 'enabled' not in value or value["enabled"] or admin:
				btn = types.KeyboardButton(key)
				markup.row(btn)
		markup.row('↩️Назад в Меню', 'Корзина')
		bot.send_message(message.chat.id, "Выберите блюдо", reply_markup=markup)
	if message.text == "↩️Назад в Меню":
		root = db.reference('/Меню')
		menu = root.get()
		markup = types.ReplyKeyboardMarkup()
		for key in menu:
			menu1 = types.KeyboardButton(key)
			markup.row(menu1)
		markup.row('Корзина')
		bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=markup)
try:
	bot.polling(none_stop=True)
except Exception:
	bot.polling(none_stop=True)

@server.route('/' + config.token, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://amigopizza.herokuapp.com/' + config.token)
    return "!", 200


if name == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))