import urllib.request

def query_horizons(id_string):
    if " " in id_string:
        id_string = id_string.replace(" ", "%20")

    url_begin_str = "https://ssd.jpl.nasa.gov/api/horizons_lookup.api?sstr="
    url = url_begin_str + id_string
    try:
        with urllib.request.urlopen(url) as response:
            html_bytes = response.read()
            html_content = html_bytes.decode('utf-8')
    except urllib.error.URLError as e:
        print(f"Error making request: {e.reason}")

    no_match_identifier = '"count":0'
    single_match_identifier = '"count":1'
    asteroid_check_identifier = '"type":"asteroid'

    id_number = {}

    if no_match_identifier in html_content:
        pass
    elif single_match_identifier in html_content:
        if asteroid_check_identifier in html_content:
            extract_substr = '"name":"'
            start_index = html_content.find(extract_substr) + len(extract_substr)
            end_index = html_content.find(' ', start_index)
            id_number = html_content[start_index:end_index]
        else:
            extract_substr = '"spkid":"'
            start_index = html_content.find(extract_substr) + len(extract_substr)
            end_index = html_content.find('"', start_index)
            id_number = html_content[start_index:end_index]
    else:
        extract_count = '"count":'
        total_cnt_str_start_idx = html_content.rfind(extract_count) + len(extract_count)
        total_cnt_str_idx = html_content.find(',', total_cnt_str_start_idx)
        total_cnt = int(html_content[total_cnt_str_start_idx:total_cnt_str_idx])
        
        results_start = html_content.find('"result":[') + len('"result":[')
        start_idx_cnt = results_start
        id_number = {}

        for i in range(total_cnt):
            start_index = html_content.find("{", start_idx_cnt)
            end_index = html_content.find("}", start_index)

            html_content_substr = html_content[start_index:end_index]

            extract_substr_name = '"name":"'
            start_sub_idx = html_content_substr.find(extract_substr_name) + len(extract_substr_name)
            end_sub_idx = html_content_substr.find('"', start_sub_idx)
            id_number_name = html_content_substr[start_sub_idx:end_sub_idx]

            extract_substr_spkid = '"spkid":"'
            start_sub_idx = html_content_substr.find(extract_substr_spkid) + len(extract_substr_spkid)
            end_sub_idx = html_content_substr.find('"', start_sub_idx)
            id_number_spkid = html_content_substr[start_sub_idx:end_sub_idx]

            id_number[id_number_name] = id_number_spkid
            if i != total_cnt - 1:
                start_idx_cnt = end_index + 1
        
    return id_number

if __name__ == "__main__":
    result = query_horizons("Neptune")
    print(result)