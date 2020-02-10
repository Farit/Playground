import re
import os
import os.path
import argparse

from pydub import AudioSegment


def convert_time_str_to_milliseconds(time_str):
    """
    time_str: 00:01:16,326
    """
    hours, minutes, seconds = time_str.strip().split(":")
    seconds, milliseconds = seconds.split(',')
    return int(
        3600000 * int(hours) +
        60000 * int(minutes) +
        1000 * int(seconds) +
        int(milliseconds)
    )


def process_srt_file(srt_file_path):
    current_srt_line = None
    end_text_symbols = ['.']
    time_span_re_pattern = re.compile(
        r'\d\d:\d\d:\d\d,\d\d\d\s-->\s\d\d:\d\d:\d\d,\d\d\d$'
    )
    data = {}
    # The Unicode character \ufeff is the byte order mark or BOM, and is used
    # to tell the difference between big- and little-endian UTF-16 encoding.
    # We should give the correct encoding when opening a file
    with open(srt_file_path, encoding='utf-8-sig') as fh:
        for line in fh:
            line = line.strip()

            if not line:
                continue

            if line.isdecimal():
                if (
                        current_srt_line is None or
                        data[current_srt_line]['text'].strip()[-1] in end_text_symbols
                ):
                    current_srt_line = line
                    data[current_srt_line] = {}
                    data[current_srt_line]['text'] = ''
                    data[current_srt_line]['start_time_str'] = []
                    data[current_srt_line]['end_time_str'] = []

            elif re.match(time_span_re_pattern,line):
                start_time_str, end_time_str = line.split('-->')
                data[current_srt_line]['start_time_str'].append(
                    start_time_str.strip()
                )
                data[current_srt_line]['end_time_str'].append(
                    end_time_str.strip()
                )

            else:
                data[current_srt_line]['text'] += line + ' '
    return data


def main(audio_file_path, srt_file_path, output_dir, audio_format='mp3'):
    srt_data_dict: dict = process_srt_file(srt_file_path)
    audio_file = getattr(AudioSegment, f'from_{audio_format}')(audio_file_path)
    os.mkdir(output_dir)

    delta_threshold = 5000
    srt_data_list: list = list(srt_data_dict.items())
    srt_data_list.sort(key=lambda i: int(i[0]))

    for ind, (srt_line, srt_datum) in enumerate(srt_data_list):
        current_start_time = convert_time_str_to_milliseconds(
            srt_datum['start_time_str'][0]
        )
        if ind != 0:
            previous_end_time = convert_time_str_to_milliseconds(
                srt_data_list[ind-1][1]['end_time_str'][-1]
            )
            delta = current_start_time - previous_end_time
            delta = delta if delta < delta_threshold else delta_threshold
            start_time = current_start_time - (delta // 2)
        else:
            start_time = current_start_time

        current_end_time = convert_time_str_to_milliseconds(
            srt_datum['end_time_str'][-1]
        )
        if ind < len(srt_data_list) - 1:
            next_start_time = convert_time_str_to_milliseconds(
                srt_data_list[ind+1][1]['start_time_str'][0]
            )
            delta = next_start_time - current_end_time
            delta = delta if delta < delta_threshold else delta_threshold
            end_time = current_end_time + (delta // 2)
        else:
            end_time = current_end_time

        audio_slice = audio_file[start_time:end_time + 1]
        audio_slice.export(
            f'{output_dir}/{srt_line}.{audio_format}',
            format=audio_format
        )

        with open(f'{output_dir}/{srt_line}.txt', 'w') as fh:
            fh.write(srt_datum['text'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--audio-file-path', required=True)
    parser.add_argument('--srt-file-path', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    main(
        audio_file_path=args.audio_file_path,
        srt_file_path=args.srt_file_path,
        output_dir=args.output_dir
    )

