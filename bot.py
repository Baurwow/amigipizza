#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config, telebot, requests, firebase_admin
from firebase_admin import db
from telebot import types
from emoji import emojize

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=["start"])
def start(message):
	root = db.reference('/Меню')
	menu = root.get()

	markup = types.ReplyKeyboardMarkup()
	print(menu)

	for key in menu:
		menu1 = types.KeyboardButton(key)
		markup.row(menu1)
	bot.send_message(message.chat.id, "Привет! Я БаурБот.\nЯ помогу заказать еду в АмигоПицца.\nПожалуйста выберите категорию:", reply_markup=markup)

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
	tmp = ""
	total = 0
	for key, value in order.items():
		total = total + value["count"] * value["price"]
		tmp = tmp + key + " = " + str(value["count"]) + " x " + str(value["price"]) + " = " + str(value["count"] * value["price"])  + " тенге \n"
	bot.send_message("565221822", tmp + "\nВсего: " + str(total) + " тенге \nОт: " + str(message.contact.phone_number) + " @" +  str(message.chat.username))
	bot.send_message(message.chat.id, "Спасибо,  Ваш заказ отправлен")
	db.reference("/users/"+str(user_id)+"/basket").delete()




@bot.message_handler(content_types=["text"])
def answer(message): 
	user_id = message.from_user.id
	menu = db.reference('/Меню').get()
	current = db.reference('/users/'+str(user_id) + "/current").get()

	 
	if message.text == "Добавить в корзину":
		dish = db.reference("/users/"+str(user_id)+'/current_dish').get()
		count = db.reference("/users/"+str(user_id)+"/basket/" + current + ": " +dish + "/count").get()
		price = db.reference("/users/"+str(user_id)+"/basket/" + current + ": " +dish + "/price").get()
		print(count)
		if count == None:
			db.reference("/users/"+str(user_id)+"/basket/" + current + ": " +dish).update({"count": 1, 'price': db.reference("/users/"+str(user_id) + '/current_price').get()})
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
			bot.send_message(message.chat.id, tmp + "\nВсего: " + str(total) + " тенге", reply_markup=markup)
	elif message.text == "Отправить заказ":
		phone = db.reference("/users/" + str(user_id) + "/phone").get()
		first_name = db.reference("/users/" + str(user_id) + "/first_name").get()
		login = db.reference("/users/" + str(user_id) + "/login").get()
		if phone == None and login == None:
			keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
			button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
			back_menu = types.KeyboardButton(text="↩️Назад в Меню")
			keyboard.row(button_phone, back_menu)
			bot.send_message(message.chat.id, "Отправь мне свой номер телефона для отправки заказа!", reply_markup=keyboard)
		else:
			order = db.reference("/users/"+str(user_id)+str("/basket")).get()
			tmp = ""
			total = 0
			for key, value in order.items():
				total = total + value["count"] * value["price"]
				tmp = tmp + key + " = " + str(value["count"]) + " x " + str(value["price"]) + " = " + str(value["count"] * value["price"])  + " тенге \n"
			bot.send_message("565221822", tmp + "\nВсего: " + str(total) + " тенге \nОт: " + str(phone) + " @" + str(login))
			bot.send_message(message.chat.id, "Спасибо,  Ваш заказ отправлен")
			db.reference("/users/"+str(user_id)+"/basket").delete()

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
	if current:
		root = db.reference("/Меню/" + current)
		ctg = root.get()

		if message.text in ctg:
			name = message.text
			dish = db.reference("/Меню/" + current + "/" + name).get()
			db.reference("/users/"+str(user_id)).update({'current_dish': name})
			db.reference("/users/"+str(user_id)).update({'current_price': dish['cena']})

			user_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
			if current == 'Пицца':
				user_markup.row("Традиционное", "Тонкое", '↩️Назад')
				bot.send_message(message.chat.id, "Выберите тип теста:", reply_markup=user_markup)

			else:

				user_markup.row('Добавить в корзину')
				user_markup.row('↩️Назад', 'Корзина')


			bot.send_message(message.chat.id, dish["info"])
			bot.send_message(message.chat.id, dish["price"])
			bot.send_message(message.chat.id, dish["img"], reply_markup=user_markup)
	if message.text in menu:
		category = message.text
		db.reference("/users/"+str(user_id)).update({'current': category})
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		root = db.reference("/Меню/" + category)
		dish = root.get()
		for key in dish:
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
	
bot.polling(none_stop=True)
