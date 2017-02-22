# The  class tries to parse the GitHub's link attribute from the header
# and allow the client to query the next, previous, last links.
#
# Example :
# '<https://api.github.com/organizations/913567/repos?page=3>; rel="next", <https://api.github.com/organizations/913567/repos?page=5>; rel="last", <https://api.github.com/organizations/913567/repos?page=1>; rel="first", <https://api.github.com/organizations/913567/repos?page=1>; rel="prev"'
# next = https://api.github.com/organizations/913567/repos?page=3
# last = https://api.github.com/organizations/913567/repos?page=5
# first = https://api.github.com/organizations/913567/repos?page=1
# prev = https://api.github.com/organizations/913567/repos?page=1


class LinkParser:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.key_link_dict = {}

        key_links = self.raw_data.split(',')

        for i, key_link_string in enumerate(key_links):
            key_links[i] = key_link_string.strip()

            if ';' not in key_links[i]:
                continue

            key_link_parts = key_links[i].split(';')
            link_part = ''
            key_part = ''
            found_both_parts = True

            for j, klp in enumerate(key_link_parts):
                key_link_parts[j] = klp.strip()

                if key_link_parts[j].startswith('<') and key_link_parts[j].endswith('>'):
                    link_part = key_link_parts[j][1:-1]

                elif 'rel=' in key_link_parts[j]:
                    kv = key_link_parts[j].split('=')
                    key_part = kv[1].strip()[1:-1]

                else:
                    found_both_parts = False
                    break

            if found_both_parts:
                self.key_link_dict[key_part] = link_part

    def get_link(self, key):
        if key in self.key_link_dict:
            return self.key_link_dict[key]
        else:
            return ''
