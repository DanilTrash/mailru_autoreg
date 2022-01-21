from configparser import ConfigParser
import requests


config = ConfigParser()
config.read("config.ini")
smsman_token = config['sms_man']['sms_man_token']
URL = 'http://api.sms-man.ru/control'


def countries():
    return requests.get(f'http://api.sms-man.ru/stubs/handler_api.php?action=getCountries&api_key={smsman_token}').json()
    # return requests.get(f'http://api.sms-man.ru/control/countries?token={smsman_token}').json()


def balance():
    return requests.get(f'{URL}/get-balance?token={smsman_token}').json().get('balance')


def limits(country_id):
    return requests.get(f'http://api.sms-man.ru/stubs/handler_api.php?'
                        f'action=getPrices'
                        f'&api_key={smsman_token}'
                        f'&country={country_id}').json()
    # return requests.get(f'{URL}/limits?token={smsman_token}&country_id=${country_id}&application_id=${application_id}')


def get_number(country_id, application_id):
    return requests.get(f'http://api.sms-man.ru/stubs/handler_api.php?action=getNumber&'
                        f'api_key={smsman_token}&'
                        f'service={application_id}&'
                        f'country={country_id}').content.decode().split(':')
    # return requests.get(f'{URL}/get-number?token={smsman_token}&country_id={country_id}&application_id={application_id}').json()


def get_sms(request_id):
    return requests.get(f'{URL}/get-sms?token={smsman_token}&request_id={request_id}').json()


def set_status(request_id, status):
    return requests.get(f'{URL}/set-status?token={smsman_token}&request_id={request_id}&status={status}').json()


def applications():
    return requests.get(f'{URL}/applications?token={smsman_token}').json()
