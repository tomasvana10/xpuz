import googletrans
import subprocess

REPLACEMENTS = {
    "zh-cn": "zh",
    "zh-tw": None,
    "ht": None,
    "hmn": "hnj",
    "sm": None,
}

def parse_langcodes(langcodes):
    parsed_langcodes = langcodes
    for replacement in REPLACEMENTS:
        parsed_langcodes.remove(replacement)
        if (sub := (REPLACEMENTS[replacement])):
            parsed_langcodes.append(sub)
    
    return parsed_langcodes

def write_locales(langcodes):
    for code in langcodes:
        try:
            print(f"inserting: {code}")
            zsh_command = f"pybabel init -l {code} -i locales/base.pot -d locales"
            result = subprocess.run(['zsh', '-c', zsh_command], text=True)
        except:
            print(f"failed to insert: {code}")
        
if __name__ == "__main__":
    langcodes = list(googletrans.LANGCODES.values())
    parsed_langcodes = parse_langcodes(langcodes)
    write_locales(langcodes)