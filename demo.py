import asyncio
import threading
import os
import random
import sys
import time
import uuid
import aiofiles
import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from asyncio import Semaphore
from urllib.parse import urlencode
from signer.argus import Argus
from signer.ladon import Ladon
from signer.gorgon import Gorgon

# Additional variables
__offset = ["-28800", "-21600"]
__devices = ["SM-G9900","SM-A136U1", "SM-M225FV", "SM-E426B", "SM-M526BR", "SM-M326B","SM-A528B","SM-F711B","SM-F926B","SM-A037G","SM-A225F","SM-M325FV","SM-A226B","SM-M426B","SM-A525F","SM-N976N","SM-M526B","SM-G570MSM","SM-A520F","SM-G975F","SM-A215U1","SM-A125F","SM-J730F","SM-A207F","SM-G970F","SM-A236B","SM-J730F","SM-J730F","SM-G970F","SM-J730F","SM-J730F","SM-J327T1","SM-A205U","SM-A136B","SM-G991B","SM-G525F","SM-A528B","SM-A528B","SM-A528B","SM-A136B","SM-G900F","SM-A226B","SM-A528B","SM-A515F","SM-G935T","SM-A505F","SM-P619","SM-N976B","SM-A510M","SM-J530FM","SM-G998B","SM-A500FU", "SM-G935F"]
__versionCode = ["190303", "190205", "190204", "190103", "180904", "180804", "180803", "180802",  "270204"]
__versionUa = [247, 312, 322, 357, 358, 415, 422, 444, 466]
__resolution = ["900*1600", "720*1280"]
__dpi = ["240", "300"]

regions = ["DZ", "US", "GB", "FR", "DE"]
device_brands = ["OPPO", "Samsung", "Huawei", "Xiaomi", "OnePlus"]
timezones = ["Africa/Algiers", "America/New_York", "Europe/London", "Europe/Paris", "Europe/Berlin"]
android_versions = ["12", "11", "10", "9", "8.1"]
device_types = ["CPH2121", "SM-G960F", "P30", "Mi 9", "GM1900"]
builds = ["SP1A.210812.016", "RQ3A.210905.001", "QP1A.190711.020", "RP1A.200720.012"]

# Define the cookies
cookies = {
    "passport_csrf_token": "4e3897a60a72f0dcb50cce1ef0f4eab9",
    "passport_csrf_token_default": "4e3897a60a72f0dcb50cce1ef0f4eab9",
    "uid_tt": "bdfa5caa410ab2abaed167b5126a72b4b5de1c7b5e53ffe63598c9397dcdb55a"
}

async def load_proxies(file_path):
    async with aiofiles.open(file_path, 'r') as file:
        lines = await file.readlines()
    return [line.strip() for line in lines]

def generate_random_device_id():
    return str(uuid.uuid4())

def generate_timestamp():
    return str(int(time.time() * 1000))

def generate_random_user_agent():
    android_version = random.choice(android_versions)
    device_type = random.choice(device_types)
    build = random.choice(builds)
    cronet_version = f"711894ae {time.strftime('%Y-%m-%d')}"
    quic_version = f"5f987023 {time.strftime('%Y-%m-%d')}"
    return f"com.zhiliaoapp.musically/2023503040 (Linux; U; Android {android_version}; en; {device_type}; Build/{build}; Cronet/TTNetVersion:{cronet_version} QuicVersion:{quic_version})"

def generate_random_headers(video_id, device_id, version_name, params, unix_timestamp, app_name):
    user_agent = generate_random_user_agent()
    rticket = generate_timestamp()
    x_khronos = int(time.time())
    x_ladon = Ladon.encrypt(x_khronos, 1611921764, 1233)

    try:
        argus = Argus.get_sign(
            queryhash=f"device_id={device_id}&version_name={version_name}&video_id={video_id}",
            timestamp=unix_timestamp,
            aid=1233,
            license_id=1611921764,
            data="",
            platform="android",
            sec_device_id="",
            sdk_version="2.9.2",
            sdk_version_int=292
        )
    except Exception as e:
        print(f"Failed to generate Argus: {e}")
        argus = "default_argus"

    params_str = urlencode(params)
    gorgon = Gorgon(params=params_str, unix=unix_timestamp)
    gorgon_headers = gorgon.get_value()

    # Select random TikTok API endpoint
    api_endpoints = [
        "api16-core-c-alisg.tiktokv.com",
        "api16-core-c-useast1a.tiktokv.com",
        "api16-core-va.tiktokv.com",
        "api19-core-c-useast1a.tiktokv.com",
        "api19-core-va.tiktokv.com",
        "api19-normal-c-useast1a.tiktokv.com",
        "api21-core-c-alisg.tiktokv.com",
        "api22-core-c-useast1a.tiktokv.com",
        "api22-normal-c-useast1a.tiktokv.com"
    ]
    random_endpoint = random.choice(api_endpoints)

headers = {
        'Accept-Encoding': 'gzip',
        'Connection': 'Keep-Alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': f"passport_csrf_token={cookies['passport_csrf_token']}; passport_csrf_token_default={cookies['passport_csrf_token_default']}; uid_tt={cookies['uid_tt']}",
        'Host': random_endpoint,
        'passport-sdk-version': '30990',
        'sdk-version': '2',
        'User-Agent': user_agent,
        'X-Argus': argus,
        'X-Gorgon': gorgon_headers['x-gorgon'],
        'X-Khronos': gorgon_headers['x-khronos'],
        'X-SS-REQ-TICKET': gorgon_headers['x-ss-req-ticket'],
        'X-Ladon': x_ladon,
        'X-SS-STUB': 'ABAB9C45B6F5F3593F021D37AF534D94',  # Dummy value, should be generated
        'x-tt-req-timeout': '90000',
        'x-tt-store-region': 'id',
        'x-tt-store-region-src': 'did',
        'x-tt-ultra-lite': '1',
        'x-vc-bdturing-sdk-version': '2.3.2.118n',
        'appName': app_name,
        'Device-ID': str(device_id)
    }
    return headers

async def send_tiktok_request(session, video_id, params, semaphore, app_name):
    async with semaphore:
        try:
            device_id = random.randint(1000000000000000000, 9999999999999999999)
            iid = random.randint(1000000000000000000, 9999999999999999999)
            rticket = generate_timestamp()
            ts = generate_timestamp()
            first_install_time = str(int(ts) - random.randint(100000, 200000))
            last_install_time = str(int(ts) - random.randint(50000, 100000))
            session_id = generate_timestamp()
            region = "DE"
            device_brand = "asus"
            timezone = "Africa/Harare"
            device_type = "ASUS_Z01QD"
            version_name = "38.3.3"  # Define a version_name to use
            params = {
                'os_api': "25",
                'device_type': device_type,
                'ssmix': "a",
                'manifest_version_code': "340802",
                'dpi': random.choice(__dpi),
                'region': region,
                'carrier_region': region,
                'app_name': "musically_go",
                'version_name': version_name,
                'timezone_offset': random.choice(__offset),
                'ts': ts,
                'ab_version': version_name,
                'ac2': "wifi",
                'ac': "wifi",
                'app_type': "normal",
                'host_abi': "x86",
                'channel': "googleplay",
                'update_version_code': random.choice(__versionCode),
                '_rticket': rticket,
                'device_platform': "android",
                'iid': iid,
                'build_number': version_name,
                'locale': "de-DE",
                'op_region': region,
                'version_code': random.choice(__versionCode),
                'timezone_name': timezone,
                'cdid': str(uuid.uuid4()),
                'openudid': uuid.uuid4().hex[:16],
                'device_id': device_id,
                'sys_region': region,
                'app_language': "de",
                'resolution': random.choice(__resolution),
                'device_brand': device_brand,
                'language': "de",
                'os_version': "7.1.2",
                'aid': "1340"
            }
            unix_timestamp = int(time.time())
            headers = generate_random_headers(video_id, device_id, version_name, params, unix_timestamp, app_name)
            api_endpoints = [
                    "api16-core-c-alisg.tiktokv.com",
                    "api16-core-c-useast1a.tiktokv.com",
                    "api16-core-va.tiktokv.com",
                    "api19-core-c-useast1a.tiktokv.com",
                    "api19-core-va.tiktokv.com",
                    "api19-normal-c-useast1a.tiktokv.com",
                    "api21-core-c-alisg.tiktokv.com",
                    "api22-core-c-useast1a.tiktokv.com",
                    "api22-normal-c-useast1a.tiktokv.com"
            ]

random_endpoint = random.choice(api_endpoints)
            url = f"https://{random_endpoint}/aweme/v1/aweme/stats/"

            payload = {
                "order": "1",
                "first_install_time": first_install_time,
                "request_id": "",
                "is_ad": "false",
                "follow_status": "0",
                "tab_type": "0",
                "aweme_type": "0",
                "item_id": video_id,
                "impr_order": "1",
                "sync_origin": "false",
                "pre_item_playtime": "",
                "follower_status": "0",
                "session_id": session_id,
                "pre_hot_sentence": "",
                "pre_item_id": "",
                "play_delta": "1",
                "action_time": ts,
                "item_source_category": "1",
                "item_distribute_source": "for_you_page"
            }

            async with session.post(url, params=params, data=payload, headers=headers) as response:
                response_text = await response.text()
                if response.status == 200:
                    json_response = await response.json()
                    if json_response.get("status_code") == 0:
                        print(f"Success: {json_response}")
                    else:
                        pass
                    pass

        except aiohttp.ClientConnectionError as e:
            pass


async def main(video_id, use_proxies, app_name):
    proxies = await load_proxies('proxies.txt') if use_proxies == 'yes' else [None] * 100

    connector = TCPConnector(limit_per_host=0)
    timeout = ClientTimeout(total=20)  # Increased timeout for better reliability
    semaphore = Semaphore(100)  # Control concurrency with a semaphore

    async with ClientSession(connector=connector, timeout=timeout) as session:
        while True:
            tasks = [send_tiktok_request(session, video_id, {}, semaphore, app_name) for _ in range(100)]
            await asyncio.gather(*tasks, return_exceptions=True)

def start():
    app_name = random.choice(["tiktok_web", "musically_go"])
    asyncio.run(main(video_id, use_proxies, app_name))
video_id = "7141368418283965701"
use_proxies = "no"
for i in range(1000):
 t = threading.Thread(target=start()).start()
