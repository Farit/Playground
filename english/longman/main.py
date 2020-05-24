import re
import json
import os
import os.path
import argparse
import urllib.parse
import typing
import logging
import pathlib

import requests

from bs4 import BeautifulSoup
from tornado.httpclient import HTTPRequest, HTTPResponse, HTTPClient


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class GetVocabulary:
    WORDS_DIR = pathlib.Path(os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'words_data'
    ))

    def __init__(self):
        self.http_client = HTTPClient()

    def __call__(self, args: argparse.Namespace):
        self.WORDS_DIR.mkdir(exist_ok=True)

        words: typing.List[str] = args.words
        for word in words:
            logger.info('Processing the word: %s', word)
            orig_word = word
            word = re.sub(r'\s+', ' ', word).strip().replace(' ', '-')

            html_file = self.get_word_html(word)
            if html_file is None:
                logger.error('Could not get html: %s', word)
                continue

            json_file_path = self.parse_word_html_page(
                word=word, html_file_path=html_file
            )
            self.make_flashcards(
                orig_word=orig_word, word=word, json_file_path=json_file_path
            )

    def get_word_html(self, word):
        html_file = None
        res: requests.Response = requests.get(
            f'https://www.ldoceonline.com/dictionary/{word}'
        )
        if res.status_code != 200:
            err_msg = f'[{res.status_code}] {res.text}'
            logger.error('Getting word="%s" html ERROR="%s"', word, err_msg)
            return html_file

        html_file = os.path.join(self.WORDS_DIR, f'{word}.html')
        with open(html_file, 'w') as fh:
            fh.write(res.text)
        return html_file

    def parse_word_html_page(self, word, html_file_path):
        with open(html_file_path) as fh:
            html_doc = fh.read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        senses = soup.find_all("span", attrs={"class": "Sense"})

        data = []
        for sense in senses:
            datum = {}
            number = sense.attrs['id'].split('__')[1]
            if number:
                datum['number'] = number.strip()

            sign_post = sense.find('span', attrs={'class': 'signpost'.upper()})
            if sign_post and sign_post.parent == sense:
                datum['sign_post'] = sign_post.text.strip()

            definition = sense.find('span', attrs={'class': 'def'.upper()})
            if definition and definition.parent == sense:
                datum['definition'] = definition.text.strip()

            datum['examples'] = []

            examples = sense.find_all(
                "span", attrs={"class": "example".upper()}
            )
            for example in examples:
                if example.span and 'data-src-mp3' in example.span.attrs:
                    explanation = ''
                    parent_tag = example.parent

                    if parent_tag and 'GramExa' in parent_tag.attrs.get('class'):
                        prop_form = parent_tag.find(
                            "span", attrs={"class": "propform".upper()}
                        )
                        if prop_form and prop_form.parent == parent_tag:
                            explanation += prop_form.text

                        gloss = parent_tag.find(
                            "span", attrs={"class": "gloss".upper()}
                        )
                        if gloss and gloss.parent == parent_tag:
                            explanation += gloss.text

                    if parent_tag and 'ColloExa' in parent_tag.attrs.get('class'):
                        geo = parent_tag.find(
                            "span", attrs={"class": 'geo'.upper()}
                        )
                        if geo and geo.parent == parent_tag:
                            geo = geo.text
                        else:
                            geo = ''

                        registerlab = parent_tag.find(
                            "span", attrs={"class": 'registerlab'.upper()}
                        )
                        if registerlab and registerlab.parent == parent_tag:
                            registerlab = registerlab.text
                        else:
                            registerlab = ''

                        if geo or registerlab:
                            explanation += '[{}]  '.format(
                                ','.join(
                                    i.strip()
                                    for i in [geo, registerlab] if i.strip()
                                )
                            )

                        for item_tag in ['collo', 'gloss']:
                            item = parent_tag.find(
                                "span", attrs={"class": item_tag.upper()}
                            )
                            if item and item.parent == parent_tag:
                                explanation += item.text

                    text = example.text.strip().replace('’', "'")
                    match = re.search(r'\(\=.*\)', text)
                    if match:
                        explanation += ' ' + match.group()
                        text = re.sub(r'\(\=.*\)', ' ', text)

                    datum['examples'].append({
                        'explanation': explanation,
                        'audio': example.span.attrs['data-src-mp3'],
                        'eng_text': text
                    })

            if datum['examples']:
                data.append(datum)

        output = os.path.join(self.WORDS_DIR, f'{word}.json')
        with open(output, 'w') as fh:
            json.dump(data, fh, ensure_ascii=False, indent=4)
        return output

    def make_flashcards(self, orig_word, word, json_file_path):
        with open(json_file_path) as fh:
            data = json.load(fh)

        work_dir = self.WORDS_DIR.joinpath(f'{word}_flashcards')
        work_dir.mkdir(exist_ok=True)

        flashcard_num = 0
        for datum in data:
            for flashcard in datum['examples']:
                flashcard_num += 1
                audio_file = self.download_audio(audio_url=flashcard['audio'])
                if audio_file:
                    output_json = os.path.join(work_dir, f'{flashcard_num}.json')
                    with open(output_json, 'w') as fh:
                        explanation = f'{orig_word.upper()} -- '
                        if 'sing_post' in datum:
                            explanation += f'[{datum["sing_post"]}] '
                        if 'definition' in datum:
                            explanation += f'({datum["definition"]}) '
                        if 'explanation' in datum:
                            explanation += f'{datum["explanation"]} '
                        word_translation = self.translate(text=orig_word)
                        if word_translation:
                            explanation += f'{word_translation}'

                        json.dump({
                            'question': self.translate(text=flashcard['eng_text']),
                            'answer': flashcard['eng_text'],
                            'explanation': explanation.strip()
                        }, fh, ensure_ascii=False, indent=4)

                    output_mp3 = work_dir.joinpath(f'{flashcard_num}.mp3')
                    output_mp3.write_bytes(audio_file)

    def translate(self, text):
        url = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
        api_key = os.getenv('YANDEX_TRANSLATE_API_KEY')
        params = urllib.parse.urlencode({
            'key': api_key,
            'text': text,
            'lang': 'en-ru'
        })
        data = {}

        http_request = HTTPRequest(
            f'{url}?{params}',
            method='POST',
            body=json.dumps(data)
        )

        try:
            response: HTTPResponse = self.http_client.fetch(
                http_request,
                # argument only affects the `HTTPError` raised
                # when a non-200 response code is
                # used, instead of suppressing all errors.
                raise_error=False
            )
        except Exception as err:
            logger.exception(f'YaTranslate error: {err}')
            return None

        if response.code == 200:
            try:
                data = json.loads(response.body)
                if data['code'] == 200:
                    return data['text'][0]
            except Exception as err:
                logger.exception(f'YaTranslate error: {err}')

        logger.error(f'YaTranslate error: {response.body}')

    def download_audio(self, audio_url):
        http_request = HTTPRequest(f'{audio_url}', method='GET')

        try:
            response: HTTPResponse = self.http_client.fetch(
                http_request,
                # argument only affects the `HTTPError` raised
                # when a non-200 response code is
                # used, instead of suppressing all errors.
                raise_error=False
            )
        except Exception as err:
            logger.exception(f'Download audio error: {err}')
            return None

        if response.code == 200:
            try:
                return response.body
            except Exception as err:
                logger.exception(f'Download audio error: {err}')
        logger.error(f'Download audio error: {response.body}')


if __name__ == '__main__':
    get_vocabulary = GetVocabulary()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True, dest='')

    parser_get_vocabulary = subparsers.add_parser('get-vocabulary')
    parser_get_vocabulary.add_argument('words', nargs='+')
    parser_get_vocabulary.set_defaults(func=get_vocabulary)

    args = parser.parse_args()
    args.func(args)
