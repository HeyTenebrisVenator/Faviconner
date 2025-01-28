import mmh3
import requests
import sys
try:
    file = sys.argv[1]
    if file == '-h' or  file == 'help':
        print('Usage: python faviconner.py /path/to/domains /path/to/save...')
    else:
        try:
            open(file)
        except:
            print('Error: File not found')
            sys.exit(1)
    try:
        save = sys.argv[2]
        open(save)
    except:
        print('Error: File not found')
        sys.exit(1)
except IndexError:
    print('Usage: python3 faviconner.py /path/to/domains /path/to/save...')
    sys.exit(1)

for domain in file:
    domain = domain.replace('\n', '')
    try:
        response = requests.get(f'http://{domain}/favicon.ico')
        if response.status_code == 200:
            favicon = response.content.encode('base64')
            hash = mmh3.hash(favicon)
            open(save, 'w').write(f'{domain} - {hash}\n')
            open(save + '_hashs', 'a').write(hash)
    except:
        pass