from hoshino import logger, aiorequests

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"


async def search(keyword, result_num: int = 3):
    """ 搜索音乐 """
    number = 5
    song_list = []
    params = {"w": keyword, "format": "json", "p": "1", "n": number}

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Charset": "UTF-8,*;q=0.5",
        "Accept-Encoding": "gzip,deflate,sdch",
        "Accept-Language": "en-US,en;q=0.8",
        "referer": "http://m.y.qq.com",
        "User-Agent": USER_AGENT
    }
    try:
        resp = await aiorequests.get(
            url="https://c.y.qq.com/soso/fcgi-bin/client_search_cp",
            params=params,
            headers=headers,
            timeout=3
        )
        res_data = await resp.json()
    except Exception as e:
        logger.warning(f'Request QQ Music Timeout {e}')
        return None
    try:
        for item in res_data['data']['song']['list'][:result_num]:
            song_list.append(
                {
                    'name': item['songname'],
                    'id': item['songid'],
                    'artists': ' '.join(
                        artist['name'] for artist in item['singer']
                    ),
                    'type': 'qq'
                }
            )
        return song_list
    except KeyError as e:
        logger.warning(f'No Result: {e}')
        return None
