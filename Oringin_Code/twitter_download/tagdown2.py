import httpx
import asyncio
import re
import os
import csv
import time
import json
import hashlib
from datetime import datetime
from urllib.parse import quote
from url_utils import quote_url
from transaction_generate import get_url_path
from transaction_generate import get_transaction_id

with open('settings.json', 'r', encoding='utf-8') as f:
    settings = json.load(f)
cookie = settings['cookie']
# cookie = 'auth_token=79dbe246d6b57f9b5f28678447b09578b710ed2e; ct0=635cb6aa3b218d798dd2f9c5907d157b925ac12d1a0168e3dcd1e2904893cc08e6e268cee84839bba482dfad91d4675707e3ac2078b2cfd5c45a164b9ef238418db736481d1c54a58d794f7a1ac0fadb;'

# --- Basic Tag Configuration ---
tag = ''  # 填入tag 带上#号 可留空. Example: "#MyTopic"

# --- Advanced Search Configuration ---
# Fill in the desired parts. Leave empty if not needed.
# Note: Twitter search can be sensitive to the order and combination of too many complex terms.
# Test your constructed query in https://x.com/search-advanced first.

search_all_these_words = ""  # Example: "what's happening"
search_exact_phrase = ""      # Example: "happy hour" (will be enclosed in quotes)
search_any_of_these_keywords = "" # Example: "cats dogs" (will be enclosed in parentheses)
search_none_of_these_words = "" # Example: "cats dogs" (each word will be prefixed with -)
search_hashtags = ["#ZeroTrust"] # Example: ["#ThrowbackThursday", "#Tech"] (will be "(#hashtag1 #hashtag2)")
                                 # Or a single string: "#hashtag1 #hashtag2" (will be wrapped in parentheses if not already)
search_from_user = ""         # Example: "elonmusk" (without @)
search_filter_links = True    # Example: True to add 'filter:links', False to omit
search_exclude_replies = True # Example: True to add '-filter:replies', False to omit
search_until_date = "2025-05-17"  # YYYY-MM-DD
search_since_date = "2025-01-01"  # YYYY-MM-DD

# --- Constructing _filter ---
filter_parts = []
if search_all_these_words:
    filter_parts.append(search_all_these_words)
if search_exact_phrase:
    filter_parts.append(f'"{search_exact_phrase}"') # Twitter needs exact phrases in quotes
if search_any_of_these_keywords:
    # Twitter syntax for "any of these" is typically (word1 OR word2) or just (word1 word2)
    filter_parts.append(f"({search_any_of_these_keywords})")
if search_none_of_these_words:
    # Each word should be prefixed with a hyphen
    excluded_words = [f"-{word.strip()}" for word in search_none_of_these_words.split() if word.strip()]
    if excluded_words:
        filter_parts.append(" ".join(excluded_words))
if search_hashtags:
    if isinstance(search_hashtags, list):
        # Ensure hashtags start with # and form a group like (#hash1 #hash2)
        valid_hashtags = [h.strip() for h in search_hashtags if h.strip().startswith("#")]
        if valid_hashtags:
            filter_parts.append(f"({' '.join(valid_hashtags)})")
    elif isinstance(search_hashtags, str) and search_hashtags.strip():
        # If it's a string like "#tag1 #tag2", wrap it if not already
        cleaned_hashtags = search_hashtags.strip()
        if cleaned_hashtags.startswith("(") and cleaned_hashtags.endswith(")"):
            filter_parts.append(cleaned_hashtags)
        else:
            filter_parts.append(f"({cleaned_hashtags})")

if search_from_user:
    filter_parts.append(f"(from:{search_from_user.replace('@', '')})") # Remove @ if user included it
if search_filter_links:
    filter_parts.append("filter:links")
if search_exclude_replies:
    filter_parts.append("-filter:replies")
if search_until_date:
    filter_parts.append(f"until:{search_until_date}")
if search_since_date:
    filter_parts.append(f"since:{search_since_date}")

_filter = " ".join(filter_parts)
# Ensure _filter does not start/end with spaces that might mess up `tag + _filter` logic later
_filter = _filter.strip()


# (可选项) 高级搜索
# 旧的_filter注释掉，现在由上面的配置生成
# _filter = "(#ZeroTrust) until:2025-05-17 since:2025-01-01"
# 请在 https://x.com/search-advanced 中组装搜索条件，复制搜索栏的内容填入_filter
# 注意，_filter中所有出现的双引号都需要改为单引号或添加转义符 例如 "Monika" -> 'Monika'

down_count = 10000

media_latest = True
# media_latest为True时，对应 [最新] 标签页，False对应 [媒体] 标签页 (与文本模式无关)
# 开启时建议 _filter 包含 'filter:links -filter:replies' (现在可以通过上面的配置项设置)


text_down = False
# 文本下载模式，会消耗大量API次数
# 开启文本下载时 不要包含 filter:links (现在可以通过 search_filter_links=False 来控制)

#最大并发数量，遇到多次下载失败时适当降低
max_concurrent_requests = 2

if text_down:
    entries_count = 20
    product = 'Latest'
    mode = 'text'
    # If text_down is True, ensure filter:links is not part of the query
    # This is now handled by the construction logic if search_filter_links is set to False
else:
    entries_count = 50
    product = 'Media'
    mode = 'media'
    if media_latest:
        entries_count = 20
        product = 'Latest'
        mode = 'media_latest'

# The original code had: _filter = ' ' + _filter
# This was to ensure a space between tag and _filter if both were present.
# We will construct the full search query string more carefully.
# The `_search_query_for_api` will be the final string for the API.
# The `_folder_name_source` will be used for naming folders.

_folder_name_source = ""
if tag and tag.strip():
    _folder_name_source = tag.strip()
elif _filter: # if tag is empty but _filter is not
    _folder_name_source = _filter
else: # if both tag and _filter are empty
    _folder_name_source = "generic_search_results" # Default folder name

# Construct the final query string for the API
# This replaces `tag + _filter` and the `_filter = ' ' + _filter` logic
final_query_parts = []
if tag and tag.strip():
    final_query_parts.append(tag.strip())
if _filter: # _filter is already stripped
    final_query_parts.append(_filter)
_search_query_for_api = " ".join(final_query_parts).strip()


def del_special_char(string):
    # Allow spaces in the string for better readability, but they will be removed for folder names.
    # For folder names, we might want to replace spaces with underscores or remove them.
    # The original regex removes almost everything non-alphanumeric.
    string = re.sub(r'[^#\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\u3040-\u31FF\._-]', '', string) # Added hyphen and underscore
    string = string.replace(" ", "_") # Replace spaces with underscores for folder names
    return string

def stamp2time(msecs_stamp:int) -> str:
    timeArray = time.localtime(msecs_stamp/1000)
    otherStyleTime = time.strftime("%Y-%m-%d %H-%M", timeArray)
    return otherStyleTime

def hash_save_token(media_url):
    m = hashlib.md5()
    m.update(f'{media_url}'.encode('utf-8'))
    return m.hexdigest()[:4]


def get_heighest_video_quality(variants) -> str:
    if len(variants) == 1:
        return variants[0]['url']

    max_bitrate = 0
    heighest_url = None
    for i in variants:
        if 'bitrate' in i:
            if int(i['bitrate']) > max_bitrate:
                max_bitrate = int(i['bitrate'])
                heighest_url = i['url']
    return heighest_url


def download_control(media_lst, _csv):
    async def _main():
        async def down_save(url, _csv_info, is_image):
            if is_image:
                url += '?format=png&name=4096x4096'

            count = 0
            while True:
                try:
                    async with semaphore:
                        async with httpx.AsyncClient() as client:
                            response = await client.get(quote_url(url), timeout=(3.05, 16))
                    with open(_csv_info[6], 'wb') as f:
                        f.write(response.content)
                    break
                except Exception as e:
                    count += 1
                    print(e)
                    print(f'{_csv_info[6]}=====>第{count}次下载失败,正在重试')

            _csv.data_input(_csv_info)

        semaphore = asyncio.Semaphore(max_concurrent_requests)
        await asyncio.gather(*[asyncio.create_task(down_save(url[0], url[1], url[2])) for url in media_lst])

    asyncio.run(_main())


class csv_gen():
    def __init__(self, save_path: str) -> None:
        self.f = open(f'{save_path}/{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}-{mode}.csv', 'w', encoding='utf-8-sig', newline='')
        self.writer = csv.writer(self.f)

        # 初始化
        self.writer.writerow(['Run Time : ' + datetime.now().strftime('%Y-%m-%d %H-%M-%S')])
        if text_down:
            main_par = ['Tweet Date', 'Display Name', 'User Name', 'Tweet URL', 'Tweet Content', 'Favorite Count',
                        'Retweet Count', 'Reply Count']
        else:  # media格式
            main_par = ['Tweet Date', 'Display Name', 'User Name', 'Tweet URL', 'Media Type', 'Media URL', 'Saved Path',
                        'Tweet Content', 'Favorite Count', 'Retweet Count', 'Reply Count']
        self.writer.writerow(main_par)

    def csv_close(self):
        self.f.close()

    def stamp2time(self, msecs_stamp: int) -> str:
        timeArray = time.localtime(msecs_stamp / 1000)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M", timeArray)
        return otherStyleTime

    def data_input(self, main_par_info: list) -> None:
        main_par_info[0] = self.stamp2time(main_par_info[0])  # 传进来的是int时间戳，故转换一下
        self.writer.writerow(main_par_info)


class tag_down():
    def __init__(self):
        # Use the determined _folder_name_source for folder path
        self.folder_path = os.getcwd() + os.sep + del_special_char(_folder_name_source) + os.sep

        if not os.path.exists(self.folder_path):  # 创建主文件夹
            os.makedirs(self.folder_path)

        self.media_folder = os.path.join(self.folder_path, 'media')
        if not os.path.exists(self.media_folder):  # 创建 media 子文件夹
            os.makedirs(self.media_folder)

        self.csv = csv_gen(self.folder_path)

        self._headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
        }
        
        self._headers['cookie'] = cookie
        re_token = 'ct0=(.*?);'
        self._headers['x-csrf-token'] = re.findall(re_token, cookie)[0]
        # Use _search_query_for_api for the referer URL
        self._headers['referer'] = f'https://twitter.com/search?q={quote(_search_query_for_api)}&src=typed_query&f=media' # or product

        self.cursor = ''
        self.ct = get_transaction_id()

        for i in range(down_count // entries_count):
            # Use _search_query_for_api for the API URL
            api_url_template = 'https://x.com/i/api/graphql/AIdc203rPpK_k_2KWSdm7g/SearchTimeline?variables={{"rawQuery":"{}","count":{},"cursor":"{}","querySource":"typed_query","product":"{}"}}&features={{"rweb_video_screen_enabled":false,"profile_label_improvements_pcf_label_in_post_enabled":true,"rweb_tipjar_consumption_enabled":true,"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"premium_content_api_read_enabled":false,"communities_web_enable_tweet_community_results_fetch":true,"c9s_tweet_anatomy_moderator_badge_enabled":true,"responsive_web_grok_analyze_button_fetch_trends_enabled":false,"responsive_web_grok_analyze_post_followups_enabled":true,"responsive_web_jetfuel_frame":false,"responsive_web_grok_share_attachment_enabled":true,"articles_preview_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"responsive_web_grok_show_grok_translated_post":false,"responsive_web_grok_analysis_button_from_backend":false,"creator_subscriptions_quote_tweet_preview_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_grok_image_annotation_enabled":true,"responsive_web_enhance_cards_enabled":false}}'
            
            # Construct the variables part for the URL
            variables_dict = {
                "rawQuery": _search_query_for_api, # Use the fully constructed query
                "count": entries_count,
                "cursor": self.cursor,
                "querySource": "typed_query",
                "product": product
            }
            # The features part is static in your original code, so keep it as a long string for now.
            # For better readability, it could also be a dict converted to JSON string.
            features_json_string = '{"rweb_video_screen_enabled":false,"profile_label_improvements_pcf_label_in_post_enabled":true,"rweb_tipjar_consumption_enabled":true,"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"premium_content_api_read_enabled":false,"communities_web_enable_tweet_community_results_fetch":true,"c9s_tweet_anatomy_moderator_badge_enabled":true,"responsive_web_grok_analyze_button_fetch_trends_enabled":false,"responsive_web_grok_analyze_post_followups_enabled":true,"responsive_web_jetfuel_frame":false,"responsive_web_grok_share_attachment_enabled":true,"articles_preview_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"responsive_web_grok_show_grok_translated_post":false,"responsive_web_grok_analysis_button_from_backend":false,"creator_subscriptions_quote_tweet_preview_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_grok_image_annotation_enabled":true,"responsive_web_enhance_cards_enabled":false}'

            # Manually construct the URL as the original graphql one has a specific structure
            # where variables and features are separate query parameters.
            base_url = "https://x.com/i/api/graphql/AIdc203rPpK_k_2KWSdm7g/SearchTimeline"
            url_params = {
                "variables": json.dumps(variables_dict, separators=(',', ':')), # Compact JSON
                "features": features_json_string
            }
            # Encode parameters for the URL
            encoded_params = "&".join([f"{key}={quote(value)}" for key, value in url_params.items()])
            url = f"{base_url}?{encoded_params}"

            _path = get_url_path(url) # get_url_path needs the unquoted path part
            # quote_url is applied later in download_control, but for path generation it might need unquoted
            # For httpx.get, it's better to pass params as a dict if possible, but this API structure is specific.
            # The original code called quote_url on the entire constructed URL string. We'll keep that for now.

            self._headers['x-client-transaction-id'] = self.ct.generate_transaction_id(method='GET', path=_path)
            
            if text_down:
                if not self.search_save_text(url): # Pass the fully constructed URL
                    break
            else:
                if media_latest:
                    media_lst = self.search_media_latest(url) # Pass the fully constructed URL
                else:
                    media_lst = self.search_media(url) # Pass the fully constructed URL
                if not media_lst:
                    return # Changed from break to return as per original structure
                download_control(media_lst, self.csv)

        self.csv.csv_close()

    def search_media(self, url):
        # ... (rest of the function remains the same)
        # Make sure any internal references to global `_filter` or `tag` are reviewed
        # if they were used for anything other than the main query URL.
        # In this function, `url` is passed as an argument, so it should be fine.
        media_lst = []

        response = httpx.get(url, headers=self._headers).text # URL is already fully formed
        try:
            raw_data = json.loads(response)
        except Exception:
            if 'Rate limit exceeded' in response:
                print('API次数已超限')
            else:
                print('获取数据失败')
            print(response)
            return # Return None or empty list as per original logic

        if not self.cursor:  # 第一次
            # Check if the expected path exists
            try:
                entries = raw_data['data']['search_by_raw_query']['search_timeline']['timeline']['instructions'][-1]['entries']
            except (KeyError, IndexError, TypeError):
                print("Error parsing initial response structure for 'entries'. Raw data:")
                print(response[:1000]) # Print a snippet of the response
                return
            
            if len(entries) < 2: # Original condition was len(raw_data) == 2, assuming raw_data was entries
                print("Not enough entries in initial response to proceed or find cursor.")
                return
            self.cursor = entries[-1]['content']['value']
            raw_data_lst = entries[0]['content']['items'] # Assuming this structure holds
        else:
            try:
                instructions = raw_data['data']['search_by_raw_query']['search_timeline']['timeline']['instructions']
                self.cursor = instructions[-1]['entry']['content']['value'] # Original: raw_data[-1]['entry']['content']['value']
                if 'moduleItems' in instructions[0]: # Original: raw_data[0]
                    raw_data_lst = instructions[0]['moduleItems']
                else:
                    print("No 'moduleItems' in subsequent response.")
                    return
            except (KeyError, IndexError, TypeError):
                print("Error parsing subsequent response structure. Raw data:")
                print(response[:1000])
                return


        for tweet_item in raw_data_lst:
            # Ensure tweet_item path is correct
            try:
                tweet = tweet_item['item']['itemContent']['tweet_results']['result']
            except KeyError:
                # print("Skipping item due to missing path to tweet_results.result")
                continue # Skip this item if structure is not as expected

            try:
                display_name = tweet['core']['user_results']['result']['legacy']['name']
                screen_name = '@' + tweet['core']['user_results']['result']['legacy']['screen_name']
            except KeyError:
                # print("Skipping tweet due to missing user info.")
                continue
            try:
                time_stamp = int(tweet['edit_control']['editable_until_msecs']) - 3600000
            except KeyError:
                if 'edit_control_initial' in tweet.get('edit_control', {}): # Safe access
                    time_stamp = int(tweet['edit_control']['edit_control_initial']['editable_until_msecs']) - 3600000
                else:
                    # print("Skipping tweet due to missing timestamp info.")
                    continue
            try:
                Favorite_Count = tweet['legacy']['favorite_count']
                Retweet_Count = tweet['legacy']['retweet_count']
                Reply_Count = tweet['legacy']['reply_count']
                _status_id = tweet['legacy']['conversation_id_str'] # Changed from status_id_str to conversation_id_str as per common API usage
                tweet_url = f'https://twitter.com/{screen_name.lstrip("@")}/status/{_status_id}'
                tweet_content = tweet['legacy']['full_text'].split('https://t.co/')[0]
            except KeyError as e:
                # print(f"Skipping tweet due to missing legacy info: {e}")
                continue
            try:
                raw_media_lst_extended = tweet['legacy']['extended_entities']['media']
                for _media in raw_media_lst_extended:
                    if 'video_info' in _media:
                        media_url = get_heighest_video_quality(_media['video_info']['variants'])
                        media_type = 'Video'
                        is_image = False
                        _file_name = os.path.join(self.media_folder,
                                                  f'{stamp2time(time_stamp)}_{del_special_char(screen_name)}_{hash_save_token(media_url)}.mp4')
                    else:
                        media_url = _media['media_url_https']
                        media_type = 'Image'
                        is_image = True
                        _file_name = os.path.join(self.media_folder,
                                                  f'{stamp2time(time_stamp)}_{del_special_char(screen_name)}_{hash_save_token(media_url)}.png')

                    media_csv_info = [time_stamp, display_name, screen_name, tweet_url, media_type, media_url,
                                      _file_name, tweet_content, Favorite_Count, Retweet_Count, Reply_Count]
                    media_lst.append([media_url, media_csv_info, is_image])
            except KeyError: # This handles cases where 'extended_entities' or 'media' might be missing (e.g., text-only tweets if not filtered)
                # print("Tweet has no extended_entities or media.")
                pass # Continue to next tweet if no media
            except Exception as e: # Catch other unexpected errors during media processing
                print(f"Error processing media for a tweet: {e}")
                continue
        return media_lst

    def search_media_latest(self, url):
        # ... (rest of the function remains the same)
        # Similar review for global variable usage as in search_media.
        media_lst = []

        response = httpx.get(url, headers=self._headers).text # URL is already fully formed
        try:
            raw_data = json.loads(response)
        except json.JSONDecodeError:
            print("Failed to decode JSON from response in search_media_latest. Response snippet:")
            print(response[:500])
            return [] # Or handle error appropriately

        if not self.cursor:  # 第一次
            try:
                entries = raw_data['data']['search_by_raw_query']['search_timeline']['timeline']['instructions'][-1]['entries']
                if len(entries) < 2: # Assuming at least 2 entries for cursor and data
                    print("Initial response doesn't have enough entries for cursor/data in search_media_latest.")
                    return []
                self.cursor = entries[-1]['content']['value']
                raw_data_lst = entries[:-2] # Original logic
            except (KeyError, IndexError, TypeError) as e:
                print(f"Error parsing initial response in search_media_latest: {e}. Response snippet:")
                print(response[:500])
                return []
        else: # Subsequent calls
            try:
                instructions = raw_data['data']['search_by_raw_query']['search_timeline']['timeline']['instructions']
                self.cursor = instructions[-1]['entry']['content']['value']
                if 'entries' in instructions[0]: # Check if 'entries' key exists in the first instruction
                    raw_data_lst = instructions[0]['entries']
                else:
                    # This case might mean no more results or a change in API structure
                    # print("No 'entries' in subsequent response instructions[0] in search_media_latest.")
                    return []
            except (KeyError, IndexError, TypeError) as e:
                print(f"Error parsing subsequent response in search_media_latest: {e}. Response snippet:")
                print(response[:500])
                return []

        for tweet_entry in raw_data_lst:
            if 'promoted' in tweet_entry.get('entryId', ''): # Safe access to entryId
                continue
            
            try:
                tweet = tweet_entry['content']['itemContent']['tweet_results']['result']
            except KeyError:
                # print("Skipping entry, couldn't find tweet_results.result.")
                continue

            # Handle cases where 'tweet' might be nested differently (e.g. for retweets or API variations)
            if 'tweet' in tweet: # If there's a nested 'tweet' object, use it
                tweet_data_source = tweet['tweet']
            else:
                tweet_data_source = tweet # Otherwise, use the current 'tweet' object

            try:
                display_name = tweet_data_source['core']['user_results']['result']['legacy']['name']
                screen_name = '@' + tweet_data_source['core']['user_results']['result']['legacy']['screen_name']
            except KeyError:
                # print("Skipping tweet, couldn't find user legacy info.")
                continue
            
            try:
                # Check for edit_control existence before accessing its children
                edit_control = tweet_data_source.get('edit_control')
                if edit_control and 'editable_until_msecs' in edit_control:
                    time_stamp = int(edit_control['editable_until_msecs']) - 3600000
                elif edit_control and 'edit_control_initial' in edit_control and 'editable_until_msecs' in edit_control['edit_control_initial']:
                    time_stamp = int(edit_control['edit_control_initial']['editable_until_msecs']) - 3600000
                else: # If no timestamp, try to get created_at as a fallback, or skip
                    created_at_str = tweet_data_source.get('legacy', {}).get('created_at')
                    if created_at_str:
                        # Convert 'Wed May 15 10:00:00 +0000 2024' to timestamp
                        dt_object = datetime.strptime(created_at_str, '%a %b %d %H:%M:%S %z %Y')
                        time_stamp = int(dt_object.timestamp() * 1000)
                    else:
                        # print("Skipping tweet, couldn't determine timestamp.")
                        continue
            except (KeyError, ValueError) as e: # ValueError for strptime
                print(f"Error parsing timestamp: {e}")
                continue

            try:
                legacy_data = tweet_data_source.get('legacy', {})
                Favorite_Count = legacy_data.get('favorite_count', 0)
                Retweet_Count = legacy_data.get('retweet_count', 0)
                Reply_Count = legacy_data.get('reply_count', 0)
                _status_id = legacy_data.get('conversation_id_str') # or 'id_str' if conversation_id_str is not what you need
                if not _status_id: # Fallback if conversation_id_str is None
                    _status_id = legacy_data.get('id_str') 
                
                if not _status_id: # If still no status ID, cannot form URL
                    # print("Skipping tweet, status ID not found.")
                    continue

                tweet_url = f'https://twitter.com/{screen_name.lstrip("@")}/status/{_status_id}'
                tweet_content = legacy_data.get('full_text', '').split('https://t.co/')[0]
            except KeyError as e: # Should be less frequent with .get()
                print(f"Error accessing legacy tweet data: {e}")
                continue
            
            try:
                # Check for extended_entities and media presence
                extended_entities = legacy_data.get('extended_entities')
                if extended_entities and 'media' in extended_entities:
                    raw_media_lst_items = extended_entities['media']
                    for _media_item in raw_media_lst_items:
                        if 'video_info' in _media_item:
                            media_url = get_heighest_video_quality(_media_item['video_info']['variants'])
                            media_type = 'Video'
                            is_image = False
                            _file_name = os.path.join(self.media_folder,
                                                      f'{stamp2time(time_stamp)}_{del_special_char(screen_name)}_{hash_save_token(media_url)}.mp4')
                        else: # Assumed image if not video
                            media_url = _media_item['media_url_https']
                            media_type = 'Image'
                            is_image = True
                            _file_name = os.path.join(self.media_folder,
                                                      f'{stamp2time(time_stamp)}_{del_special_char(screen_name)}_{hash_save_token(media_url)}.png')
                        
                        media_csv_info = [time_stamp, display_name, screen_name, tweet_url, media_type, media_url,
                                          _file_name, tweet_content, Favorite_Count, Retweet_Count, Reply_Count]
                        media_lst.append([media_url, media_csv_info, is_image])
            except KeyError: # Catches if 'extended_entities' or 'media' is missing within legacy_data.
                pass # No media, or structure differs.
            except Exception as e:
                print(f"An unexpected error occurred while processing media: {e}")
        return media_lst

    def search_save_text(self, url):
        # ... (rest of the function remains the same)
        # Similar review for global variable usage as in search_media.
        response = httpx.get(url, headers=self._headers).text # URL is already fully formed
        try:
            raw_data = json.loads(response)
        except json.JSONDecodeError:
            print(f"Failed to decode JSON in search_save_text. Response: {response[:200]}")
            return False


        if not self.cursor:  # 第一次
            try:
                entries = raw_data['data']['search_by_raw_query']['search_timeline']['timeline']['instructions'][-1]['entries']
                if len(entries) < 2: # Expect at least cursor and one item
                    return False # Not enough data
                self.cursor = entries[-1]['content']['value']
                raw_data_lst = entries[:-2] # As per original logic
            except (KeyError, IndexError, TypeError):
                print(f"Error parsing initial response in search_save_text. Response: {response[:200]}")
                return False
        else: # Subsequent calls
            try:
                instructions = raw_data['data']['search_by_raw_query']['search_timeline']['timeline']['instructions']
                # Check if there are enough instructions to get a cursor
                if not instructions or not instructions[-1].get('entry'):
                    # print("Cannot find cursor in subsequent response.")
                    return False # No cursor means we can't paginate further or no more results
                self.cursor = instructions[-1]['entry']['content']['value']
                
                # Check for actual tweet entries
                if len(instructions) < 2 or 'entries' not in instructions[0]:
                    # This might mean no more tweets, or the structure changed
                    # print("No entries found in subsequent response or structure mismatch.")
                    return False # No actual data entries
                raw_data_lst = instructions[0]['entries']
            except (KeyError, IndexError, TypeError):
                print(f"Error parsing subsequent response in search_save_text. Response: {response[:200]}")
                return False

        if not raw_data_lst: # If, after parsing, raw_data_lst is empty, no items to process
            return False


        for tweet_entry in raw_data_lst:
            if 'promoted' in tweet_entry.get('entryId', ''): #.get for safety
                continue
            
            try:
                # Navigate to the actual tweet data
                tweet_content_item = tweet_entry.get('content', {}).get('itemContent', {}).get('tweet_results', {}).get('result')
                if not tweet_content_item:
                    continue # Skip if path is broken

                # Check if there's a nested 'tweet' object, common for retweets or certain tweet types
                tweet = tweet_content_item.get('tweet', tweet_content_item) # Use nested 'tweet' if exists, else use parent
            except KeyError:
                continue


            try:
                edit_control = tweet.get('edit_control')
                if edit_control and 'editable_until_msecs' in edit_control:
                    time_stamp = int(edit_control['editable_until_msecs']) - 3600000
                elif edit_control and 'edit_control_initial' in edit_control and 'editable_until_msecs' in edit_control['edit_control_initial']:
                    time_stamp = int(edit_control['edit_control_initial']['editable_until_msecs']) - 3600000
                else: # Fallback to created_at if edit_control is not available/useful
                    created_at_str = tweet.get('legacy', {}).get('created_at')
                    if created_at_str:
                        dt_object = datetime.strptime(created_at_str, '%a %b %d %H:%M:%S %z %Y')
                        time_stamp = int(dt_object.timestamp() * 1000)
                    else:
                        continue # Skip if no valid timestamp
            except (KeyError, ValueError): # ValueError for strptime
                continue

            try:
                core_user_results = tweet.get('core', {}).get('user_results', {}).get('result', {})
                display_name = core_user_results.get('legacy', {}).get('name')
                screen_name = '@' + core_user_results.get('legacy', {}).get('screen_name', 'unknown_user')
                if not display_name or screen_name == '@unknown_user':
                    continue # Skip if user info is missing
            except KeyError: # Should be rare with .get()
                continue

            try:
                legacy_data = tweet.get('legacy', {})
                Favorite_Count = legacy_data.get('favorite_count', 0)
                Retweet_Count = legacy_data.get('retweet_count', 0)
                Reply_Count = legacy_data.get('reply_count', 0)
                _status_id = legacy_data.get('conversation_id_str') or legacy_data.get('id_str') # Fallback for status ID
                
                if not _status_id:
                    continue # Skip if no status ID

                tweet_url = f'https://twitter.com/{screen_name.lstrip("@")}/status/{_status_id}'
                tweet_content = legacy_data.get('full_text', '').split('https://t.co/')[0]
            except KeyError: # Should be rare with .get()
                continue

            self.csv.data_input([time_stamp, display_name, screen_name, tweet_url, tweet_content, Favorite_Count, Retweet_Count, Reply_Count])
        return True


if __name__ == '__main__':
    print('无过程输出...(๑´ڡ`๑)')
    # Test with some configurations
    # Example 1: Default from your original _filter
    # search_hashtags = ["#ZeroTrust"]
    # search_until_date = "2025-05-17"
    # search_since_date = "2025-01-01"
    # search_filter_links = False # Assuming default was no filter:links
    # search_exclude_replies = False # Assuming default was no -filter:replies

    # Example 2: More complex search
    # tag = "#AITrends"
    # search_all_these_words = "machine learning"
    # search_exact_phrase = "future of AI"
    # search_any_of_these_keywords = "innovation breakthrough"
    # search_none_of_these_words = "hype rumor"
    # search_hashtags = ["#DeepLearning", "#ML"]
    # search_from_user = "someaicompany"
    # search_filter_links = True
    # search_exclude_replies = True
    # search_until_date = "2024-12-31"
    # search_since_date = "2024-01-01"

    # Reconstruct _filter and _search_query_for_api based on the new settings
    # This logic is already at the top of the script, so it will run before tag_down()
    
    tag_down()
    print('已完成')