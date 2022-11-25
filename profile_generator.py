import dataclasses
import json
import random
import secrets
import string
from datetime import date
from typing import Optional

import requests
import urllib3
from faker import Faker
from requests import Session
from transliterate import translit
from urllib3.exceptions import InsecureRequestWarning

from utils import GENDER_VALUES, EMAIL_SUFFIXES
urllib3.disable_warnings(InsecureRequestWarning)


# noinspection PyMethodMayBeStatic
@dataclasses.dataclass
class MailProfile:
	name: str
	lastname: str
	username: str
	email_suffix: str
	password: str
	gender: str
	dob: date
	registered: bool = False

	def __init__(
			self,
			name: str,
			lastname: str,
			username: str,
			email_suffix: str,
			password: str,
			gender: str,
			dob: date,
			registered: bool
	):
		self.name = name
		self.lastname = lastname
		self.username = username
		self.email_suffix = email_suffix
		self.password = password
		self.gender = gender
		self.dob = dob
		self.registered = registered

	@staticmethod
	def generate_new(locale: str = 'en', use_minute_box: bool = False):
		fake = Faker(locale)
		if use_minute_box:
			provider = MailBox()
			provider.connect()
			provider.close()
			username = provider.email.split("@", 1)[0]
			first, last = username.split(".", 1)
			gender = random.choice(GENDER_VALUES)
		else:
			gender = random.choice(GENDER_VALUES)
			first = fake.first_name_male() if gender == "Мужской" else fake.first_name_female()
			last = fake.last_name_male() if gender == "Мужской" else fake.last_name_female()

			full = translit(" ".join([first, last]), reversed=True) if locale == 'ru' else " ".join([first, last])
			full = "".join(x for x in full if x.isalpha() or x.isspace())
			username = MailProfile.create_username(full)

		password = MailProfile.generate_password()

		email_suffix = random.choice(EMAIL_SUFFIXES)

		while True:
			dob: date = fake.date_time()
			if 1975 <= dob.year < 2000:
				break
			if dob.month == 2 and dob.day > 28:
				dob.replace(day=random.randint(1, 28))

		name = first
		lastname = last
		username = username
		password = password
		birthday: date = dob

		return MailProfile(
			name,
			lastname,
			username,
			email_suffix,
			password,
			gender,
			birthday,
			registered=True
		)

	@staticmethod
	def create_username(name: str):
		return MailProfile.username_generator(name.lower())

	@staticmethod
	def generate_password():
		alphabet = string.ascii_letters + string.digits
		password = ''.join(secrets.choice(alphabet) for _ in range(8))
		result = f"{random.choice(string.ascii_uppercase)}{password}!{random.choice('0123456789')}"
		return result

	@staticmethod
	def username_generator(name: str):
		items = name.split(" ")
		name = items[0]
		surname = items[1]

		name = MailProfile.transform(name)
		surname = MailProfile.transform(surname)

		items = [name, surname]

		if random.choice([True, False]):
			for idx, item in enumerate(items):
				if not item:
					continue
				items[idx] = item.capitalize()

		if random.choice([True, False]):
			result = ".".join(items)
		else:
			result = "".join(items)

		if len(result) < 7:
			result += str(random.randint(100, 10000))
		return result

	@staticmethod
	def transform(item: str) -> str:
		if not item:
			return item

		processors = [
			MailProfile.crop_right_processor,
			MailProfile.crop_left_processor,
			MailProfile.capitalize_processor
		]
		if random.choice([True, False]):
			processor = random.choice(processors)
			return processor(item)
		else:
			return item

	@staticmethod
	def crop_right_processor(item: str) -> str:
		indexes = [idx for idx, _ in enumerate(item) if idx != 0]
		crop_length = random.choice(indexes)
		return item[:crop_length]

	@staticmethod
	def crop_left_processor(item: str) -> str:
		indexes = [idx for idx, _ in enumerate(item) if idx != len(item) - 1]
		crop_length = random.choice(indexes)
		return item[crop_length:]

	@staticmethod
	def capitalize_processor(item: str) -> str:
		return item.capitalize()

	@staticmethod
	def pascal_case_processor(item: str) -> str:
		return "".join([x for x in item.title() if not x.isspace() and x.isalpha()])


class MailBox:
	url: str = 'https://www.minuteinbox.com'

	connection: Optional[Session] = None
	email: str = ''

	def _init_connection(self) -> None:
		self.connection = requests.Session()
		self.connection.verify = False

	def connect(self) -> str:
		self.close()
		self._init_connection()
		self.connection.get(self.url + "/")
		response = self.connection.get(self.url + "/index/index", headers={
			"X-KL-Ajax-Request": "Ajax_Request",
			"X-Requested-With": "XMLHttpRequest",
		})
		data = json.loads(response.content.lstrip(b'\xef\xbb\xbf'))
		self.email = data.get("email")
		if not self.email:
			raise ValueError("Email is not found in the mailbox")
		return self.email

	def close(self):
		if self.connection is not None:
			self.connection.close()
			self.connection = None
