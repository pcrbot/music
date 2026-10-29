"""
Reference link:
https://github.com/bluetomlee/NetEase-MusicBox/blob/master/src/api.py
"""
import json

from hoshino import logger, aiorequests


class NetEase:
    def __init__(self):
        self.header = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/search/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) '
            + 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 '
            + 'Safari/537.36',
            'X-Real-IP': '39.156.69.79',
            'X-Forwarded-For': '39.156.69.79',
        }
        self.cookies = {
            'appver': '1.5.2'
        }

    async def httpRequest(self, action, query=None):
        resp = await aiorequests.post(
            action,
            data=query,
            headers=self.header,
            timeout=3
        )
        data = await resp.json()
        return data

    async def search(self, s, stype=1, offset=0, total='true'):
        action = 'http://music.163.com/api/search/get/web'
        data = {
            's': s,
            'type': stype,
            'offset': offset,
            'total': total,
            'limit': 60
        }
        return await self.httpRequest(action, data)


async def _fetch_covers(ids):
    """批量查询专辑封面，失败时返回空字典"""
    if not ids:
        return {}
    try:
        resp = await aiorequests.get(
            'http://music.163.com/api/song/detail/',
            params={'ids': json.dumps(ids)},
            headers={'Referer': 'http://music.163.com/', 'User-Agent': 'Mozilla/5.0'},
            timeout=5
        )
        data = await resp.json()
        return {
            song['id']: (song.get('album') or {}).get('picUrl', '')
            for song in data.get('songs', [])
        }
    except Exception as e:
        logger.warning(f'获取网易云封面失败：{type(e)}')
        return {}


async def search(keyword: str, result_num: int = 3):
    n = NetEase()
    song_list = []
    data = await n.search(keyword)
    if data and data['code'] == 200:
        try:
            songs = data['result']['songs'][:result_num]
            covers = await _fetch_covers([item['id'] for item in songs])
            for item in songs:
                song_list.append(
                    {
                        'name': item['name'],
                        'id': item['id'],
                        'artists': ' '.join(
                            [artist['name'] for artist in item['artists']]
                        ),
                        'type': '163',
                        'url': f'https://music.163.com/song?id={item["id"]}',
                        'image': covers.get(item['id'], '')
                    }
                )
            return song_list
        except Exception as e:
            logger.warning(f'获取网易云歌曲失败, 返回数据data={data}, 错误信息error={e}')
    return song_list


if __name__ == "__main__":
    song_list = search('起风了')
    if song_list:
        for song in song_list:
            print(song)
