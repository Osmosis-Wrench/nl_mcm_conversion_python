import io
import re
import json

pool1 = open("pool1")
pool2 = open("pool2")
pool3 = open("pool3")
pool4 = open("pool4")
pool5 = open("pool5")
pool6 = open("pool6")
pool7 = open("pool7")
pool8 = open("pool8")

mcm_option = {}

def fix(s):
  return s[0].lower() + s[1:]

# build db
pool1stuff = re.findall("(.*(?:\=).*)", pool1.read())
length = len(pool1stuff)
for i in range(length):
    mcm_object = {}
    pool1stuff[i] = pool1stuff[i].lstrip()
    statename = fix((pool1stuff[i].split("=")[0]).strip())
    mcm_object.update({"statename" : statename})
    mcm_object.update({"AddOption" : ((pool1stuff[i].split("=")[1]).lstrip())})
    mcm_object.update({"OnOptionSelect" : ""})
    mcm_object.update({"OnOptionHighlight" : ""})
    mcm_object.update({"OnOptionMenuOpen" : ""})
    mcm_object.update({"OnOptionMenuAccept" : ""})
    mcm_object.update({"OnOptionSliderOpen" : ""})
    mcm_object.update({"OnOptionSliderAccept" : ""})
    mcm_object.update({"OnOptionKeyMapChange" : ""})
    mcm_option[mcm_object["statename"]] = mcm_object

def get_data(poolname, ret):
    poolstuff = re.split("Elseif ", poolname.read(), flags=re.IGNORECASE)
    length = len(poolstuff)
    for i in range(length):
        poolstuff[i] = poolstuff[i].lstrip()
        content = poolstuff[i].splitlines(True)
        statename = (content[0].split("==")[1]).lstrip()
        statename = statename.replace(")", '')
        statename = statename.replace("\n", '')
        statename = fix(statename)
        content.pop(0)
        codelen = len(content)
        for x in range(codelen):
            content[x] = content[x].lstrip()
            if content[x].lower() == "endif":
                content[x] = ""
        for x in range(codelen):
            if "SetToggleOptionValue" in content[x]:
                content[x] = content[x].replace("Option, ", "")
                content[x] = content[x].replace("SetToggleOptionValue", "SetToggleOptionValueST")
                myIndex = content[x].find(")")
                content[x] = content[x][:myIndex] + ", False, " + "\"{}\"".format(statename) + content[x][myIndex:]
        codeblock = "".join(map((str), content))
        mycount = codeblock.count("\n")
        codeblock = codeblock.replace("\n", "\n        ", mycount - 1)
        mcm_option[statename].update({ret : codeblock})

get_data(pool2, "OnOptionSelect")
get_data(pool3, "OnOptionHighlight")
get_data(pool4, "OnOptionMenuOpen")
get_data(pool5, "OnOptionMenuAccept")
get_data(pool6, "OnOptionSliderOpen")
get_data(pool7, "OnOptionSliderAccept")
get_data(pool8, "OnOptionKeyMapChange")

with open('data.json', 'w') as outfile:
    json.dump(mcm_option, outfile, indent=4)

def getdatafromkey(data, key, field):
    if data[key][field] != "":
        return data[key][str(field)]
    else:
        return False

def buildEvent(event, code):
    if event == "OnMenuAcceptST":
        statepart = "String state_id, int index"
    if event == "OnSliderAcceptST":
        statepart = "String state_id, float value"
    else:
        statepart = "String state_id"
    ret = "    Event {}({})\n        {}    endEvent".format(event, statepart, code)
    if event == "OnHighlightST":
        return ret
    else:
        return ret+"\n\n"

raw = (open("data.json")).read()
data = json.loads(raw)
datalen = len(data)
outData1 = ""
outData2 = ""
for key in data:
    statename = getdatafromkey(data, key, "statename")
    AddOption = getdatafromkey(data, key, "AddOption")
    OnOptionSelect = getdatafromkey(data, key, "OnOptionSelect")
    OnOptionHighlight = getdatafromkey(data, key, "OnOptionHighlight")
    OnOptionMenuOpen = getdatafromkey(data, key, "OnOptionMenuOpen")
    OnOptionMenuAccept = getdatafromkey(data, key, "OnOptionMenuAccept")
    OnOptionSliderOpen = getdatafromkey(data, key, "OnOptionSliderOpen")
    OnOptionSliderAccept = getdatafromkey(data, key, "OnOptionSliderAccept")
    OnOptionKeyMapChange = getdatafromkey(data, key, "OnOptionKeyMapChange")
    # Build AddOption
    loc = AddOption.find("(\"")
    AddOption = AddOption[:loc] + "ST" + AddOption[loc:]
    loc = AddOption.find("(\"") + 1
    AddOption = AddOption[:loc] + "\"{}\", ".format(statename) + AddOption[loc:]
    # Build State
    if OnOptionSelect:
        state1 = "state {}\n".format(statename)
        state2 = "\nendstate\n"
        select = buildEvent("OnSelectST", OnOptionSelect)
        highlight = buildEvent("OnHighlightST", OnOptionHighlight)
        myState = ("{}{}{}{}".format(state1, select, highlight, state2))

    if OnOptionMenuOpen:
        state1 = "state {}\n".format(statename)
        state2 = "\nendstate\n"
        openMenu = buildEvent("OnMenuOpenST", OnOptionMenuOpen)
        acceptMenu = buildEvent("OnMenuAcceptST", OnOptionMenuAccept)
        highlight = buildEvent("OnHighlightST", OnOptionHighlight)
        myState = ("{}{}{}{}{}".format(state1, select, acceptMenu, highlight, state2))

    if OnOptionSliderOpen:
        state1 = "state {}\n".format(statename)
        state2 = "\nendstate\n"
        openMenu = buildEvent("OnSliderOpenST", OnOptionSliderOpen)
        acceptMenu = buildEvent("OnSliderAcceptST", OnOptionSliderAccept)
        highlight = buildEvent("OnHighlightST", OnOptionHighlight)
        myState = ("{}{}{}{}{}".format(state1, openMenu, acceptMenu, highlight, state2))

    outData1 += AddOption + "\n"
    outData2 += myState + "\n"

f = open("output.psc", "w")
f.write("\n---- AddOptions ----\n\n" + outData1 + "\n---- States ----\n\n" + outData2)
f.close()
