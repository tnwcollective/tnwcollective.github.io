# render.py
# A terribly simple static CMS for tnwc.
# I need to make a README for this...

import json
import os
import re
import sys

# Configuration
TMPL_FILE = "template.html" # base 'theme' for all pages
SB_FILE = "sidebar.html" # for building navigation
DESC = "The New Web Collective." # for meta tags
URL = "https://tnwcollective.github.io" # for absolute paths

failures = 0 # count issues

# Check we have necessary files
def check_env():
    if os.path.exists(TMPL_FILE) == False:
        print("I can't continue without a template file!")
        quit()
    if os.path.exists("files.json") == False:
        print("There's no list of files to work with...")
        quit()

# Indent lines n times, but not if they're code blocks
def indent(string, n):
    out = ""
    c = 0
    current_n = n
    for line in string.split("\n"):
        if "<pre>" in line: current_n = 0
        if line != "":
            if c > 0:
                out += "\t" * current_n + line + "\n"
            else: out += line + "\n"
        c += 1
        if "</pre>" in line: current_n = n
    return(out.rstrip("\n"))

def render(src_path, dest_path, meta_props):
    global failures

    tmpl_file = open(TMPL_FILE, "r", encoding = "utf-8")
    tmpl = tmpl_file.read()
    tmpl_file.close()

    if os.path.exists(src_path) == False:
        failures += 1
        print("  ! not found!")
        return
    src_file = open(src_path, "r", encoding="utf-8")
    src = src_file.read()
    src_file.close()

    if len(src.split("\n")[0]) > 1 and src.split("\n")[0][1] == "!":
        title = src.split("\n")[0].replace("<!--", "").replace("-->", "")
    else:
        failures += 1
        print("  ! no source header")
        return

    out = tmpl.replace("$CONTENT", indent(src, 4))
    out = out.replace("$TITLE", title)

    if os.path.exists(SB_FILE) == True:
        sidebar_file = open(SB_FILE, "r", encoding="utf-8")
        sidebar = sidebar_file.read()
        sidebar_file.close()
        out = out.replace("$SIDEBAR", indent(sidebar, 5))
    else:
        print("  * no sidebar")

    if "desc" in meta_props:
        out = out.replace("$DESC", meta_props["desc"])
    else:
        out = out.replace("$DESC", DESC)

    out = out.replace("$URL", URL) # done last so we can write to the sidebar

    out_file = open(dest_path, "w", encoding = "utf-8")
    out_file.write(out)
    out_file.close()

check_env()

# Make the URL your local path for testing
if len(sys.argv) == 2 and sys.argv[1] == "-l":
    print("(I'm building locally...)")
    URL = __file__.replace("\\", "/")

list_file = open("files.json", "r")
list_data = json.load(list_file)
list_file.close()

for f in list_data:
    meta_props = {}
    print("+ " + f["dest"].replace("src/", ""))
    if "desc" in f:
        meta_props["desc"] = f["desc"]
    render(f["src"], f["dest"], meta_props)

if failures == 0:
    print("All done!")
elif failures == 1:
    print("I'm finished, but with 1 failure!")
else:
    print("I'm finished, but with " + str(failures) + " failures!")
