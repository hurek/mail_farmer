# Rambler Email Autoreg
Note: The project is made for educational purposes to understand how playwright and captcha services work.
Use the code wisely and for educational purposes.

## Quick start

1. Install requirements with `pip install -r requirements.txt`
2. Download playwright browsers with `playwright install` command
3. Rename .env_EXAMPLE to .env and put your 2Captcha api token here
4. Run script with `python3 main.py`. Tested on Python v3.9+

## Generator options
1. Use minute-box service
2. Use Faker library. Also supports `locale` flag to generate names for locales.
To choose generator options change following line in `main.py` file (inside loop):
```
profile = MailProfile.generate_new(locale='ru', use_minute_box=False)
```

P.S. Feel free to create your own MailProfile generator and submit PR.