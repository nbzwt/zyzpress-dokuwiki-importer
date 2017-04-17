zyzpress-doku-importer
======================

[![License](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](LICENSE)

Import an existing DokuWiki based blog to zyzPress.

It can also load tags and category from an existing mongodb JSON dump.

## How to use

### 1. Prepare dependency

```
apt install php7.0-cli
apt install python3 pip3
pip3 install pymongo
```

### 2. Put your webroot in a folder called 'dokuwiki'

You should have .\importer.py and .\dokuwiki\index.php

### 3. Run tool and follow the instruction

```
python3 importer.py
```

## Troubleshooting

If you got 'PermissionError: [Errno 13] Permission denied', you probably need to:
```
chmod +x ./dokuwiki/bin/render.php
```

If you find that pictures with CJK or other unicode characters failed to load, run this in the img folder:
```
deurlname *.*
```

## License

>The MIT License (MIT)
>
>Copyright (c) 2017 ZephRay
>
>Permission is hereby granted, free of charge, to any person obtaining a copy
>of this software and associated documentation files (the "Software"), to deal
>in the Software without restriction, including without limitation the rights
>to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
>copies of the Software, and to permit persons to whom the Software is
>furnished to do so, subject to the following conditions:
>
>The above copyright notice and this permission notice shall be included in
>all copies or substantial portions of the Software.
>
>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
>IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
>FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
>AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
>LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
>OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
>THE SOFTWARE.
