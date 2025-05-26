# app/controllers/twitter_download/tag_down_logic.py
import httpx
import asyncio
import re
import os
import csv
import time
import json
import hashlib
from typing import Optional, List
from datetime import datetime
from urllib.parse import quote

# Assuming url_utils and transaction_generate are in the same directory
from .url_utils import quote_url
from .transaction_generate import get_url_path, get_transaction_id

# --- Global variables that will be set by initiate_download ---
# These are placeholders and will be overridden by parameters
_cookie = 'auth_token=79dbe246d6b57f9b5f28678447b09578b710ed2e; ct0=635cb6aa3b218d798dd2f9c5907d157b925ac12d1a0168e3dcd1e2904893cc08e6e268cee84839bba482dfad91d4675707e3ac2078b2cfd5c45a164b9ef238418db736481d1c54a58d794f7a1ac0fadb;'
_tag_param = ''
_search_all_these_words_param = ""
_search_exact_phrase_param = ""
_search_any_of_these_keywords_param = ""
_search_none_of_these_words_param = ""
_search_hashtags_param = []
_search_from_user_param = ""
_search_filter_links_param = True
_search_exclude_replies_param = True
_search_until_date_param = ""
_search_since_date_param = ""

_down_count_param = 10000
_media_latest_param = True
_text_down_param = False
_max_concurrent_requests_param = 2

# These will be derived within initiate_download
_filter_derived = ""
_search_query_for_api_derived = ""
_folder_name_source_derived = "" # For the subfolder name inside the target directory
_mode_derived = ""
_product_derived = ""
_entries_count_derived = 0


# --- Helper Functions (Copied from original, ensure no direct global var use unless intended) ---
def clean_filename_for_paths(string_val): # Renamed from del_special_char for clarity
    # Allow spaces in the string for better readability, but they will be removed for folder names.
    string_val = re.sub(r'[^#\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\u3040-\u31FF\._-]', '', string_val)
    string_val = string_val.replace(" ", "_") # Replace spaces with underscores
    # Limit length to avoid issues with file systems
    return string_val[:100] # Limit length

def stamp2time(msecs_stamp:int) -> str:
    timeArray = time.localtime(msecs_stamp/1000)
    otherStyleTime = time.strftime("%Y-%m-%d %H-%M", timeArray)
    return otherStyleTime

def hash_save_token(media_url):
    m = hashlib.md5()
    m.update(f'{media_url}'.encode('utf-8'))
    return m.hexdigest()[:4]

def get_heighest_video_quality(variants) -> str:
    if not variants: return None # Handle empty variants
    if len(variants) == 1:
        return variants[0].get('url')

    max_bitrate = 0
    heighest_url = None
    for i in variants:
        if 'bitrate' in i and i.get('url'): # Check if URL exists
            try:
                bitrate = int(i['bitrate'])
                if bitrate > max_bitrate:
                    max_bitrate = bitrate
                    heighest_url = i['url']
            except ValueError: # Handle non-integer bitrate
                continue
    # If no bitrate found, return the first available URL
    return heighest_url if heighest_url else variants[0].get('url')


def download_control(media_lst, csv_writer_instance, current_max_concurrent_requests):
    async def _main():
        async def down_save(url_info_tuple, _csv_info, is_image_flag): # Renamed for clarity
            media_dl_url, csv_data_list, _ = url_info_tuple # Unpack, third item is is_image
            
            if is_image_flag: # Use the passed flag
                media_dl_url += '?format=png&name=4096x4096'

            count = 0
            while True:
                try:
                    async with semaphore:
                        async with httpx.AsyncClient() as client:
                            # Use quote_url from url_utils.py
                            response = await client.get(quote_url(media_dl_url), timeout=(3.05, 16)) 
                    
                    # csv_data_list[6] is the saved_path
                    with open(csv_data_list[6], 'wb') as f:
                        f.write(response.content)
                    break
                except Exception as e:
                    count += 1
                    print(e)
                    print(f'{csv_data_list[6]}=====>第{count}次下载失败,正在重试 ({media_dl_url})')
                    if count >= 3: # Max retries
                        print(f"Failed to download {media_dl_url} after 3 retries.")
                        return # Stop trying

            csv_writer_instance.data_input(csv_data_list)

        semaphore = asyncio.Semaphore(current_max_concurrent_requests)
        tasks = []
        for url_info in media_lst: # url_info is [media_url, csv_info_list, is_image_bool]
            tasks.append(asyncio.create_task(down_save(url_info, url_info[1], url_info[2])))
        await asyncio.gather(*tasks)
    
    # Run the asyncio event loop for this download batch
    # If called from an already running loop (FastAPI), this needs care.
    # For simplicity in a threaded context, a new loop might be okay.
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If in FastAPI, better to use await directly or run_coroutine_threadsafe
            # For now, assuming this function is run in a separate thread by run_in_executor
            # where a new loop can be created if needed.
            # This part might need adjustment based on how FastAPI/asyncio interact.
            # A simple approach for a threaded call:
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(_main())
        else:
            asyncio.run(_main())
    except RuntimeError as e: # Handle "Event loop is closed" or "There is no current event loop"
        print(f"Asyncio loop error in download_control: {e}. Creating new loop.")
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(_main())


class csv_gen():
    def __init__(self, base_folder_path: str, current_mode_for_filename: str) -> None:
        # base_folder_path is like "Data/keyword/socialmedia/twitter/tag/search_query_subfolder"
        self.csv_file_path = os.path.join(base_folder_path, f'{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}-{current_mode_for_filename}.csv')
        self.f = open(self.csv_file_path, 'w', encoding='utf-8-sig', newline='')
        self.writer = csv.writer(self.f)

        self.writer.writerow(['Run Time : ' + datetime.now().strftime('%Y-%m-%d %H-%M-%S')])
        if _text_down_param: # Use the global param set by initiate_download
            main_par = ['Tweet Date', 'Display Name', 'User Name', 'Tweet URL', 'Tweet Content', 'Favorite Count',
                        'Retweet Count', 'Reply Count']
        else:
            main_par = ['Tweet Date', 'Display Name', 'User Name', 'Tweet URL', 'Media Type', 'Media URL', 'Saved Path',
                        'Tweet Content', 'Favorite Count', 'Retweet Count', 'Reply Count']
        self.writer.writerow(main_par)
        print(f"CSV will be saved to: {self.csv_file_path}")

    def csv_close(self):
        if self.f and not self.f.closed:
            self.f.close()
            print(f"CSV file closed: {self.csv_file_path}")


    def stamp2time(self, msecs_stamp: int) -> str: # Redundant, already global, but keep for class encapsulation if preferred
        timeArray = time.localtime(msecs_stamp / 1000)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M", timeArray)
        return otherStyleTime

    def data_input(self, main_par_info: list) -> None:
        main_par_info[0] = self.stamp2time(main_par_info[0])
        self.writer.writerow(main_par_info)


class tag_down_executor(): # Renamed from tag_down to avoid confusion with filename
    def __init__(self, base_target_dir: str):
        # base_target_dir is "Data/keyword/socialmedia/twitter/tag"
        # _folder_name_source_derived is the name for the subfolder (e.g., #ZeroTrust_...)
        self.final_data_folder = os.path.join(base_target_dir, clean_filename_for_paths(_folder_name_source_derived))
        
        if not os.path.exists(self.final_data_folder):
            os.makedirs(self.final_data_folder, exist_ok=True)
        print(f"Data will be saved in: {self.final_data_folder}")

        self.media_subfolder = os.path.join(self.final_data_folder, 'media')
        if not os.path.exists(self.media_subfolder):
            os.makedirs(self.media_subfolder, exist_ok=True)

        self.csv_writer = csv_gen(self.final_data_folder, _mode_derived) # Pass full path for CSV

        self._headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'cookie': _cookie, # Use the global _cookie
        }
        try:
            re_token = 'ct0=(.*?);'
            csrf_token_match = re.findall(re_token, _cookie)
            if not csrf_token_match:
                raise ValueError("ct0 token not found in cookie. Check your cookie format.")
            self._headers['x-csrf-token'] = csrf_token_match[0]
        except Exception as e:
            print(f"Error extracting CSRF token: {e}. Proceeding without x-csrf-token if not found.")
            self._headers['x-csrf-token'] = "" # Fallback or handle error

        self._headers['referer'] = f'https://twitter.com/search?q={quote(_search_query_for_api_derived)}&src=typed_query&f={_product_derived.lower()}'


        self.cursor = ''
        self.ct_generator = get_transaction_id() # Instantiate from transaction_generate.py

        # Use _down_count_param and _entries_count_derived
        num_iterations = _down_count_param // _entries_count_derived if _entries_count_derived > 0 else 0
        print(f"Starting download: {_down_count_param} tweets, {_entries_count_derived} per batch, {num_iterations} iterations.")

        for i in range(num_iterations):
            print(f"Processing batch {i+1}/{num_iterations}")
            variables_dict = {
                "rawQuery": _search_query_for_api_derived,
                "count": _entries_count_derived,
                "cursor": self.cursor,
                "querySource": "typed_query",
                "product": _product_derived
            }
            features_json_string = '{"rweb_video_screen_enabled":false,"profile_label_improvements_pcf_label_in_post_enabled":true,"rweb_tipjar_consumption_enabled":true,"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"premium_content_api_read_enabled":false,"communities_web_enable_tweet_community_results_fetch":true,"c9s_tweet_anatomy_moderator_badge_enabled":true,"responsive_web_grok_analyze_button_fetch_trends_enabled":false,"responsive_web_grok_analyze_post_followups_enabled":true,"responsive_web_jetfuel_frame":false,"responsive_web_grok_share_attachment_enabled":true,"articles_preview_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"responsive_web_grok_show_grok_translated_post":false,"responsive_web_grok_analysis_button_from_backend":false,"creator_subscriptions_quote_tweet_preview_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_grok_image_annotation_enabled":true,"responsive_web_enhance_cards_enabled":false}'
            base_url = "https://x.com/i/api/graphql/AIdc203rPpK_k_2KWSdm7g/SearchTimeline"
            url_params = {
                "variables": json.dumps(variables_dict, separators=(',', ':')),
                "features": features_json_string
            }
            encoded_params = "&".join([f"{key}={quote(value)}" for key, value in url_params.items()])
            api_url = f"{base_url}?{encoded_params}"
            
            # Use get_url_path from transaction_generate.py
            _path_for_tid = get_url_path(api_url) 
            self._headers['x-client-transaction-id'] = self.ct_generator.generate_transaction_id(method='GET', path=_path_for_tid)
            
            if _text_down_param:
                if not self.search_save_text(api_url):
                    print("Stopping text download due to issues or no more data.")
                    break
            else:
                if _media_latest_param:
                    media_lst_result = self.search_media_latest(api_url)
                else:
                    media_lst_result = self.search_media(api_url)
                
                if not media_lst_result:
                    print("No media found in this batch or stopping due to issues.")
                    # Consider if 'return' was intended to stop all further batches.
                    # If so, this loop should break or a flag should be set.
                    # For now, it continues to the next iteration if num_iterations > 1
                    # but if it's the last one, it effectively stops.
                    # If it should stop all further processing:
                    # self.csv_writer.csv_close() # Close CSV before exiting
                    # return # This would exit the __init__
                    break # This exits the loop

                download_control(media_lst_result, self.csv_writer, _max_concurrent_requests_param)
            
            if not self.cursor: # If cursor becomes empty, no more pages
                print("Cursor is empty, assuming no more pages.")
                break
            time.sleep(1) # Small delay between batches

        self.csv_writer.csv_close()
        print(f"Download process finished for {self.final_data_folder}")

    def _parse_tweet_data(self, tweet_item_content):
        # Helper to extract common tweet data, returns a dict or None
        tweet_data = {}
        try:
            # Handle variations like 'tweet' for retweets or 'tweet_results' for direct tweets
            tweet_core_data = tweet_item_content.get('tweet_results', {}).get('result')
            if not tweet_core_data: # Fallback for different structures
                 tweet_core_data = tweet_item_content.get('tweet', {}).get('result') # Example structure
                 if not tweet_core_data: # Another common structure
                     tweet_core_data = tweet_item_content 

            # If 'tweet' is a direct child (e.g. in lists of tweets)
            if 'tweet' in tweet_core_data:
                tweet_data_source = tweet_core_data['tweet']
            else:
                tweet_data_source = tweet_core_data


            legacy = tweet_data_source.get('legacy', {})
            core_user = tweet_data_source.get('core', {}).get('user_results', {}).get('result', {}).get('legacy', {})

            tweet_data['display_name'] = core_user.get('name', 'N/A')
            tweet_data['screen_name'] = '@' + core_user.get('screen_name', 'N/A')
            
            # Timestamp logic
            edit_control = tweet_data_source.get('edit_control', {})
            if 'editable_until_msecs' in edit_control:
                tweet_data['time_stamp'] = int(edit_control['editable_until_msecs']) - 3600000
            elif 'edit_control_initial' in edit_control and 'editable_until_msecs' in edit_control['edit_control_initial']:
                 tweet_data['time_stamp'] = int(edit_control['edit_control_initial']['editable_until_msecs']) - 3600000
            else:
                created_at_str = legacy.get('created_at')
                if created_at_str:
                    dt_object = datetime.strptime(created_at_str, '%a %b %d %H:%M:%S %z %Y')
                    tweet_data['time_stamp'] = int(dt_object.timestamp() * 1000)
                else:
                    return None # Cannot proceed without timestamp

            tweet_data['favorite_count'] = legacy.get('favorite_count', 0)
            tweet_data['retweet_count'] = legacy.get('retweet_count', 0)
            tweet_data['reply_count'] = legacy.get('reply_count', 0)
            
            status_id = legacy.get('conversation_id_str') or legacy.get('id_str')
            if not status_id: return None
            tweet_data['tweet_url'] = f'https://twitter.com/{tweet_data["screen_name"].lstrip("@")}/status/{status_id}'
            
            full_text = legacy.get('full_text', '')
            tweet_data['tweet_content'] = full_text.split('https://t.co/')[0].strip() if full_text else 'N/A'
            
            tweet_data['extended_entities_media'] = legacy.get('extended_entities', {}).get('media', [])
            return tweet_data

        except Exception as e:
            # print(f"Error parsing tweet data: {e}, Item: {json.dumps(tweet_item_content)[:200]}")
            return None


    def _process_media_item(self, media_item_raw, tweet_info_dict):
        # Helper to process a single media item from extended_entities
        # Returns [media_url_for_download, csv_info_list, is_image_bool] or None
        media_url_dl = None
        media_type_str = ''
        is_image = False
        file_extension = ''

        if 'video_info' in media_item_raw:
            media_url_dl = get_heighest_video_quality(media_item_raw['video_info'].get('variants', []))
            media_type_str = 'Video'
            is_image = False
            file_extension = '.mp4'
        elif 'media_url_https' in media_item_raw: # Image
            media_url_dl = media_item_raw['media_url_https']
            media_type_str = 'Image'
            is_image = True
            file_extension = '.png' # Default to png, original script used this
        
        if not media_url_dl:
            return None

        # Construct filename for saving
        safe_screen_name = clean_filename_for_paths(tweet_info_dict['screen_name'])
        time_str = stamp2time(tweet_info_dict['time_stamp']) # Use global stamp2time
        media_hash = hash_save_token(media_url_dl) # Use global hash_save_token
        
        saved_file_name = f'{time_str}_{safe_screen_name}_{media_hash}{file_extension}'
        saved_file_path = os.path.join(self.media_subfolder, saved_file_name)

        csv_info = [
            tweet_info_dict['time_stamp'], 
            tweet_info_dict['display_name'], 
            tweet_info_dict['screen_name'],
            tweet_info_dict['tweet_url'],
            media_type_str,
            media_url_dl, # This is the URL to the media on Twitter's servers
            saved_file_path, # Local path where it will be saved
            tweet_info_dict['tweet_content'],
            tweet_info_dict['favorite_count'],
            tweet_info_dict['retweet_count'],
            tweet_info_dict['reply_count']
        ]
        return [media_url_dl, csv_info, is_image]

    def _extract_entries_and_cursor(self, raw_data_json, is_initial_call):
        # Helper to robustly extract tweet entries and cursor
        entries_list = []
        new_cursor = None
        try:
            timeline_instructions = raw_data_json['data']['search_by_raw_query']['search_timeline']['timeline']['instructions']
            
            # Find cursor: usually in the last instruction or an entry of type 'cursor-bottom'
            for instruction in reversed(timeline_instructions):
                if instruction.get('type') == 'TimelineAddEntries' or 'entries' in instruction:
                    for entry in reversed(instruction.get('entries', [])):
                        if entry.get('content', {}).get('entryType') == 'TimelineTimelineCursor' and \
                           entry['content'].get('cursorType') == 'Bottom':
                            new_cursor = entry['content'].get('value')
                            break
                        # Fallback for older cursor style if needed
                        if entry.get('content', {}).get('entryType') == 'TimelineTimelineModule' and \
                           entry['content'].get('cursorType') == 'Bottom': # Less common now
                             new_cursor = entry['content'].get('value')
                             break
                if new_cursor: break
            
            # If cursor not found via specific types, try the original script's logic as a fallback for initial call
            if not new_cursor and is_initial_call and timeline_instructions and 'entries' in timeline_instructions[-1]:
                 if len(timeline_instructions[-1]['entries']) > 0 and 'value' in timeline_instructions[-1]['entries'][-1].get('content', {}):
                    new_cursor = timeline_instructions[-1]['entries'][-1]['content']['value']


            # Extract entries (tweets)
            for instruction in timeline_instructions:
                if instruction.get('type') == 'TimelineAddEntries':
                    for entry in instruction.get('entries', []):
                        entry_content = entry.get('content', {})
                        if entry_content.get('entryType') == 'TimelineTimelineItem' and \
                           'itemContent' in entry_content and \
                           entry_content['itemContent'].get('itemType') == 'TimelineTweet':
                            if 'tweet_results' in entry_content['itemContent'] and \
                               'result' in entry_content['itemContent']['tweet_results']:
                                if 'promotedMetadata' not in entry_content['itemContent']['tweet_results']['result'].get('legacy', {}): # Skip promoted
                                    entries_list.append(entry_content['itemContent']) # Add the itemContent part
                        # Original script's logic for initial call (moduleItems)
                        elif is_initial_call and entry_content.get('entryType') == 'TimelineTimelineModule' and 'items' in entry_content:
                            for item_wrapper in entry_content.get('items',[]):
                                item_content_in_module = item_wrapper.get('item',{}).get('itemContent',{})
                                if item_content_in_module.get('itemType') == 'TimelineTweet':
                                     if 'tweet_results' in item_content_in_module and \
                                        'result' in item_content_in_module['tweet_results']:
                                         if 'promotedMetadata' not in item_content_in_module['tweet_results']['result'].get('legacy', {}):
                                            entries_list.append(item_content_in_module)
                # For subsequent calls, if entries are directly under an instruction (less common now)
                elif not is_initial_call and instruction.get('type') == 'TimelineReplaceEntry' and 'entry' in instruction: # Example
                    # This part is highly dependent on exact API response for replacements
                    pass


        except (KeyError, IndexError, TypeError) as e:
            print(f"Error parsing API response structure: {e}. Response snippet: {str(raw_data_json)[:500]}")
            return [], self.cursor # Return existing cursor on error
        
        # print(f"Extracted {len(entries_list)} entries. New cursor: {new_cursor is not None}")
        return entries_list, new_cursor if new_cursor else self.cursor # Fallback to old cursor if new one not found


    def search_media_common(self, url, is_latest_tab_logic):
        media_to_download_list = []
        try:
            response = httpx.get(url, headers=self._headers, timeout=30)
            response.raise_for_status() # Raise an exception for HTTP errors
            raw_data = response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} while fetching {url}. Response: {e.response.text[:200]}")
            if e.response.status_code == 429: # Rate limit
                print("Rate limit exceeded. Try again later or check cookie.")
            return None # Indicate failure
        except (json.JSONDecodeError, httpx.RequestError) as e:
            print(f"Error fetching or decoding data from {url}: {e}")
            return None

        is_initial = not self.cursor
        tweet_entries_from_api, new_api_cursor = self._extract_entries_and_cursor(raw_data, is_initial_call=is_initial)
        
        if new_api_cursor: # Update cursor only if a new one is found
            self.cursor = new_api_cursor
        elif not tweet_entries_from_api and not is_initial : # No entries and not initial call, likely end of data
            self.cursor = "" # Clear cursor to stop pagination

        if not tweet_entries_from_api:
            print("No tweet entries found in the response.")
            return [] # Return empty list, not None, to distinguish from error

        for tweet_item_content in tweet_entries_from_api: # tweet_item_content is itemContent
            parsed_tweet_info = self._parse_tweet_data(tweet_item_content)
            if not parsed_tweet_info:
                continue

            if parsed_tweet_info['extended_entities_media']:
                for media_item_raw in parsed_tweet_info['extended_entities_media']:
                    processed_media_package = self._process_media_item(media_item_raw, parsed_tweet_info)
                    if processed_media_package:
                        media_to_download_list.append(processed_media_package)
            # else:
                # print(f"Tweet {parsed_tweet_info['tweet_url']} has no media in extended_entities.")
        
        return media_to_download_list

    def search_media(self, url): # For "Media" tab
        return self.search_media_common(url, is_latest_tab_logic=False)

    def search_media_latest(self, url): # For "Latest" tab (which can also contain media)
        return self.search_media_common(url, is_latest_tab_logic=True)


    def search_save_text(self, url): # For text-only download
        try:
            response = httpx.get(url, headers=self._headers, timeout=30)
            response.raise_for_status()
            raw_data = response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} while fetching {url} for text. Response: {e.response.text[:200]}")
            return False # Indicate failure
        except (json.JSONDecodeError, httpx.RequestError) as e:
            print(f"Error fetching or decoding text data from {url}: {e}")
            return False

        is_initial = not self.cursor
        tweet_entries_from_api, new_api_cursor = self._extract_entries_and_cursor(raw_data, is_initial_call=is_initial)
        
        if new_api_cursor:
            self.cursor = new_api_cursor
        elif not tweet_entries_from_api and not is_initial:
            self.cursor = ""

        if not tweet_entries_from_api:
            print("No tweet entries found for text processing.")
            return True # No data, but not an error that should stop the process if more batches exist

        processed_count = 0
        for tweet_item_content in tweet_entries_from_api:
            parsed_tweet_info = self._parse_tweet_data(tweet_item_content)
            if not parsed_tweet_info:
                continue
            
            # For text mode, CSV format is different
            text_csv_info = [
                parsed_tweet_info['time_stamp'], # Will be converted by csv_gen
                parsed_tweet_info['display_name'],
                parsed_tweet_info['screen_name'],
                parsed_tweet_info['tweet_url'],
                parsed_tweet_info['tweet_content'],
                parsed_tweet_info['favorite_count'],
                parsed_tweet_info['retweet_count'],
                parsed_tweet_info['reply_count']
            ]
            self.csv_writer.data_input(text_csv_info)
            processed_count +=1
        
        print(f"Processed {processed_count} tweets for text.")
        return True # Success for this batch


# --- Main Entry Function for External Call ---
def initiate_twitter_download(
    base_output_directory: str, # e.g., Data/mysearch/socialmedia/twitter/tag
    keyword_for_foldername: str, # Primary keyword for subfolder naming if others are empty
    
    # Search parameters
    p_tag: Optional[str] = None,
    p_search_all_these_words: Optional[str] = None,
    p_search_exact_phrase: Optional[str] = None,
    p_search_any_of_these_keywords: Optional[str] = None,
    p_search_none_of_these_words: Optional[str] = None,
    p_search_hashtags: Optional[List[str]] = None,
    p_search_from_user: Optional[str] = None,
    p_search_filter_links: bool = True,
    p_search_exclude_replies: bool = True,
    p_search_until_date: Optional[str] = None,
    p_search_since_date: Optional[str] = None,
    
    # Operational parameters
    p_down_count: int = 1000, # Reduced default for testing
    p_media_latest: bool = True,
    p_text_down: bool = False,
    p_max_concurrent_requests: int = 2
):
    global _cookie, _tag_param, _search_all_these_words_param, _search_exact_phrase_param
    global _search_any_of_these_keywords_param, _search_none_of_these_words_param, _search_hashtags_param
    global _search_from_user_param, _search_filter_links_param, _search_exclude_replies_param
    global _search_until_date_param, _search_since_date_param, _down_count_param
    global _media_latest_param, _text_down_param, _max_concurrent_requests_param
    global _filter_derived, _search_query_for_api_derived, _folder_name_source_derived
    global _mode_derived, _product_derived, _entries_count_derived

    # Load cookie from settings.json (co-located with this script)
    try:
        settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        _cookie = settings['cookie']
        if not _cookie:
            raise ValueError("Cookie is empty in settings.json")
        print("Cookie loaded successfully from settings.json")
    except Exception as e:
        print(f"FATAL: Error loading cookie from settings.json: {e}")
        print(f"Please ensure 'settings.json' exists in {os.path.dirname(__file__)} and contains a valid 'cookie' string.")
        return # Stop execution if cookie is not loaded

    # Assign parameters to global variables (this script's internal way of working)
    _tag_param = p_tag if p_tag is not None else ""
    _search_all_these_words_param = p_search_all_these_words if p_search_all_these_words is not None else ""
    _search_exact_phrase_param = p_search_exact_phrase if p_search_exact_phrase is not None else ""
    _search_any_of_these_keywords_param = p_search_any_of_these_keywords if p_search_any_of_these_keywords is not None else ""
    _search_none_of_these_words_param = p_search_none_of_these_words if p_search_none_of_these_words is not None else ""
    _search_hashtags_param = p_search_hashtags if p_search_hashtags is not None else []
    _search_from_user_param = p_search_from_user if p_search_from_user is not None else ""
    _search_filter_links_param = p_search_filter_links
    _search_exclude_replies_param = p_search_exclude_replies
    _search_until_date_param = p_search_until_date if p_search_until_date is not None else ""
    _search_since_date_param = p_search_since_date if p_search_since_date is not None else ""

    _down_count_param = p_down_count
    _media_latest_param = p_media_latest
    _text_down_param = p_text_down
    _max_concurrent_requests_param = p_max_concurrent_requests

    # --- Construct _filter_derived (from original script's logic) ---
    filter_parts = []
    if _search_all_these_words_param: filter_parts.append(_search_all_these_words_param)
    if _search_exact_phrase_param: filter_parts.append(f'"{_search_exact_phrase_param}"')
    if _search_any_of_these_keywords_param: filter_parts.append(f"({_search_any_of_these_keywords_param})")
    if _search_none_of_these_words_param:
        excluded = [f"-{word.strip()}" for word in _search_none_of_these_words_param.split() if word.strip()]
        if excluded: filter_parts.append(" ".join(excluded))
    if _search_hashtags_param:
        valid_hashtags = [h.strip() for h in _search_hashtags_param if h.strip().startswith("#")]
        if valid_hashtags: filter_parts.append(f"({' '.join(valid_hashtags)})")
    if _search_from_user_param: filter_parts.append(f"(from:{_search_from_user_param.replace('@', '')})")
    if _search_filter_links_param: filter_parts.append("filter:links")
    if _search_exclude_replies_param: filter_parts.append("-filter:replies")
    if _search_until_date_param: filter_parts.append(f"until:{_search_until_date_param}")
    if _search_since_date_param: filter_parts.append(f"since:{_search_since_date_param}")
    _filter_derived = " ".join(filter_parts).strip()

    # --- Construct _folder_name_source_derived & _search_query_for_api_derived ---
    if _tag_param and _tag_param.strip():
        _folder_name_source_derived = _tag_param.strip()
    elif _filter_derived:
        _folder_name_source_derived = _filter_derived
    else:
        _folder_name_source_derived = keyword_for_foldername # Use the main keyword if others are empty
    
    if not _folder_name_source_derived: # Ensure there's always a folder name source
        _folder_name_source_derived = "twitter_download"


    final_query_parts = []
    if _tag_param and _tag_param.strip(): final_query_parts.append(_tag_param.strip())
    if _filter_derived: final_query_parts.append(_filter_derived)
    _search_query_for_api_derived = " ".join(final_query_parts).strip()

    if not _search_query_for_api_derived:
        print("Search query is empty. Please provide a tag or filter parameters.")
        return

    # --- Set operational modes (_mode_derived, _product_derived, _entries_count_derived) ---
    if _text_down_param:
        _entries_count_derived = 20
        _product_derived = 'Latest'
        _mode_derived = 'text'
        # Ensure filter:links is not part of the query if text_down is True
        if _search_filter_links_param:
            print("Warning: 'search_filter_links' is True but 'text_down' is also True. For text download, links are usually not filtered. Overriding search_filter_links for query construction if necessary.")
            # This logic should ideally modify _filter_derived if text_down is true
            # For now, we assume the user configures it correctly or the impact is minimal.
    else: # Media download
        _entries_count_derived = 50
        _product_derived = 'Media'
        _mode_derived = 'media'
        if _media_latest_param: # "Latest" tab for media
            _entries_count_derived = 20
            _product_derived = 'Latest' # Product is 'Latest' for "Latest" tab
            _mode_derived = 'media_latest'

    print(f"--- Twitter Download Initiated ---")
    print(f"Base Output Dir: {base_output_directory}")
    print(f"Subfolder Name Source: {_folder_name_source_derived}")
    print(f"Search Query for API: {_search_query_for_api_derived}")
    print(f"Mode: {_mode_derived}, Product: {_product_derived}, Entries/Batch: {_entries_count_derived}")
    print(f"Total Tweets to attempt: {_down_count_param}")
    
    try:
        # Instantiate and run the downloader
        # base_output_directory is "Data/keyword/socialmedia/twitter/tag"
        downloader = tag_down_executor(base_target_dir=base_output_directory)
        print("--- Twitter Download Finished ---")
    except Exception as e:
        print(f"An error occurred during the download process: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # Example of how to call this refactored script for testing
    print("Running test download...")
    test_output_dir = os.path.join(os.getcwd(), "TestData", "twitter_test", "socialmedia", "twitter", "tag")
    if not os.path.exists(test_output_dir):
        os.makedirs(test_output_dir, exist_ok=True)

    initiate_twitter_download(
        base_output_directory=test_output_dir,
        keyword_for_foldername="TestKeyword", # Used if tag and filter are empty
        p_tag="#Python",
        p_search_since_date="2024-05-01", # YYYY-MM-DD
        p_search_until_date="2024-05-10", # YYYY-MM-DD
        p_down_count=50, # Small number for testing
        p_media_latest=True, # Try "Latest" tab
        p_text_down=False, # Download media
        p_max_concurrent_requests=2,
        p_search_exclude_replies=True,
        p_search_filter_links=False # For media, usually you want links if they are media links
    )