# Copyright 2020 Sean Bradley https://sbcode.net/zabbix/

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import re
from io import StringIO
import csv

if(not os.path.exists("snmp2zabbix.conf")):
    MIB2C_CONFIG = """@open -@
@foreach $s scalar@
* scalar, $s, $s.decl, $s.objectID, $s.module, $s.parent, $s.subid, $s.enums, "$s.description"
    @foreach $LABEL, $VALUE enum@
* enum, $LABEL, $VALUE, " "
    @end@
@end@
@foreach $t table@
* table, $t, $t.decl, $t.objectID, $t.module, $t.parent, $t.subid, $t.enums, "$t.description"
    @foreach $i index@
* index, $i, $i.decl, $i.objectID, $i.module, $i.parent, $i.subid, $i.enums, "$i.description"
        @foreach $LABEL, $VALUE enum@
* enum, $LABEL, $VALUE, " "
        @end@
    @end@
    @foreach $i nonindex@
* nonindex, $i, $i.decl, $i.objectID, $i.module, $i.parent, $i.subid, $i.enums, "$i.description"
        @foreach $LABEL, $VALUE enum@
* enum, $LABEL, $VALUE, " "
        @end@
    @end@
@end@

"""

    with open("snmp2zabbix.conf", "w") as mib2c_config_file:
        mib2c_config_file.write(MIB2C_CONFIG)


MIB_FILE = sys.argv[1]
BASE_OID = sys.argv[2]
MIB2C_DATA = os.popen('env MIBS="+' + MIB_FILE +
                      '" mib2c -c snmp2zabbix.conf ' + BASE_OID).read()
# print(MIB2C_DATA)
# exit()

MIB_NAME = os.path.basename(MIB_FILE).split(".")[0].replace(" ", "_")
SCALARS = []
ENUMS = {}
LAST_ENUM_NAME = ""  # the one that is being built now
DISCOVERY_RULES = {}
LAST_DISCOVERY_RULE_NAME = ""  # the one that is being built now

DATATYPES = {
    "U_LONG": "",  # translates to Numeric (unsigned) in Zabbix
    "U64": "",  # translates to Numeric (unsigned) in Zabbix
    "OID": "CHAR",
    "U_CHAR": "CHAR",
    "LONG": "FLOAT",
    "CHAR": "TEXT",
    "IN_ADDR_T": "TEXT"
}


def getDataType(s):
    dataType = "TEXT"
    if s.upper() in DATATYPES:
        dataType = DATATYPES[s.upper()]
    else:
        print("Unhandled data type [" + s + "] so assigning TEXT")
    if len(dataType) > 0:  # if data type is INTEGER or other unsigned int, then don't create the node since zabbix will assign it the default which is already unsigned int
        return dataType
    else:
        return None


def removeColons(s):
    return s.replace("::", " ")


it = re.finditer(r'\* (.*"[^"]*")', MIB2C_DATA)
for l in it:
    line = l.groups()[0]
    groups = re.search(r'.*("[^"]*")', line)
    description = ""
    if groups is not None:
        if groups.group(1) is not None:
            description = groups.group(1).encode('string_escape')
            description = description.replace('"', '')
            description = description.replace('\\n', '&#13;')
            description = re.sub(r"\s\s+", " ", description)

    f = StringIO(u'' + line + '')
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        if len(row) > 0:
            if row[0] == "scalar":
                #print("scaler:\t" + row[4].strip() + "::" + row[1].strip() + "\t" + row[3].strip() + ".0")
                scalar = [row[4].strip() + "::" + row[1].strip(), row[3].strip() +
                          ".0", getDataType(row[2].strip()), description]
                SCALARS.append(scalar)
                LAST_ENUM_NAME = row[4].strip() + "::" + row[1].strip()
            elif row[0] == "table":
                #print("table:\t" + row[4].strip() + "::" + row[1].strip() + "\t" + row[3].strip())
                discovery_rule = [
                    row[4].strip() + "::" + row[1].strip(), row[3].strip(), [], description]
                if not row[4].strip() + "::" + row[1].strip() in DISCOVERY_RULES:
                    DISCOVERY_RULES[row[4].strip() + "::" +
                                    row[1].strip()] = []
                DISCOVERY_RULES[row[4].strip() + "::" +
                                row[1].strip()].append(discovery_rule)
                LAST_DISCOVERY_RULE_NAME = row[4].strip(
                ) + "::" + row[1].strip()
            elif row[0] == "enum":
                #print("enum:\t" + row[1].strip() + "=" + row[2].strip())
                if LAST_ENUM_NAME not in ENUMS:
                    ENUMS[LAST_ENUM_NAME] = []
                ENUMS[LAST_ENUM_NAME].append([row[1].strip(), row[2].strip()])
            elif row[0] == "index":
                #print("index:\t" + row[4].strip() + "::" +
                #      row[1].strip() + "\t" + row[3].strip())
                pass
            elif row[0] == "nonindex":
                #print("nonindex:\t" + row[4].strip() + "::" + row[1].strip() + "\t" + row[3].strip())
                if int(row[7]) == 1:
                    # print(row)
                    #print("is an enum title : " + row[4].strip() + "::" + row[1].strip())
                    LAST_ENUM_NAME = row[4].strip() + "::" + row[1].strip()
                    column = [row[4].strip() + "::" + row[1].strip(), row[3].strip(),
                              getDataType(row[2].strip()), description, LAST_ENUM_NAME]
                    DISCOVERY_RULES[LAST_DISCOVERY_RULE_NAME][0][2].append(
                        column)
                else:
                    # print(row)
                    column = [row[4].strip() + "::" + row[1].strip(),
                              row[3].strip(), getDataType(row[2].strip()), description]
                    # print(description)
                    # print(len(DISCOVERY_RULES[LAST_DISCOVERY_RULE_NAME][0][2]))
                    DISCOVERY_RULES[LAST_DISCOVERY_RULE_NAME][0][2].append(
                        column)
            # else:
            #     print("not handled row")
            #     print(row)
            # if len(row) >= 5 and MIB_NAME == "":
            #    #print(row[5])
            #    MIB_NAME = row[4].strip() + "::" + row[5].strip()


#print("MIB_NAME = " + MIB_NAME)

XML = """<?xml version="1.0" encoding="UTF-8"?>
<zabbix_export>
    <version>4.4</version>
    <templates>
        <template>
            <template>Template SNMP """ + removeColons(MIB_NAME) + """</template>
            <name>Template SNMP """ + removeColons(MIB_NAME) + """</name>
            <applications>
                <application>
                    <name>""" + MIB_NAME + """</name>
                </application>
            </applications>
            <description>Created By Sean Bradley's SNMP2ZABBIX.py at https://github.com/Sean-Bradley/SNMP2ZABBIX</description>
            <groups>
                <group>
                    <name>Templates</name>
                </group>
            </groups>
"""

# SCALARS
if SCALARS.count > 0:
    XML += """            <items>
"""
for s in SCALARS:
    XML += """                <item>
                    <name>""" + s[0] + """</name>
                    <type>SNMPV2</type>
                    <snmp_community>{$SNMP_COMMUNITY}</snmp_community>
                    <snmp_oid>""" + s[1] + """</snmp_oid>
                    <key>""" + s[1] + """</key>
"""
    if s[2] is not None:
        XML += """                    <value_type>""" + s[2] + """</value_type>
"""
    XML += """                    <description>""" + s[3] + """</description>
                    <delay>1h</delay>
                    <history>2w</history>
                    <trends>0</trends>               
                    <applications>
                        <application>
                            <name>""" + MIB_NAME + """</name>
                        </application>
                    </applications>
                    <status>DISABLED</status>
                </item>
"""
if SCALARS.count > 0:
    XML += """            </items>
"""


# Add Macros
XML += """            <macros>
                <macro>
                    <macro>{$SNMP_PORT}</macro>
                    <value>161</value>
                </macro>
            </macros>
"""

# DISCOVERY RULES
if len(DISCOVERY_RULES):
    SNMPOIDS = ""
    XML += """            <discovery_rules>
"""
    for x in DISCOVERY_RULES:
        XML += """                <discovery_rule>
                    <name>""" + x + """</name>
"""
        for y in DISCOVERY_RULES[x]:
            XML += """                    <description>""" + y[3] + """</description>
                    <delay>3600</delay>
                    <key>""" + y[1] + """</key>
                    <port>{$SNMP_PORT}</port>
                    <snmp_community>{$SNMP_COMMUNITY}</snmp_community>
                    <status>DISABLED</status>
                    <type>SNMPV2</type>
                    <item_prototypes>
"""
            for z in y[2]:
                XML += """                        <item_prototype>
                            <name>""" + z[0] + """[{#SNMPINDEX}]</name>
                            <type>SNMPV2</type>
                            <description>""" + z[3] + """</description>
                            <applications>
                                <application>
                                    <name>""" + MIB_NAME + """</name>
                                </application>
                            </applications>
                            <port>{$SNMP_PORT}</port>
                            <snmp_community>{$SNMP_COMMUNITY}</snmp_community>
                            <key>""" + z[1] + """.[{#SNMPINDEX}]</key>
                            <snmp_oid>""" + z[1] + """.{#SNMPINDEX}</snmp_oid>
                            <delay>1h</delay>
                            <history>2w</history>
                            <trends>0</trends>
                            <status>DISABLED</status>
"""
                if z[2] is not None:
                    XML += """                            <value_type>""" + z[2] + """</value_type>
"""
                if len(z) >= 5:
                    XML += """                            <valuemap>
                                <name>""" + z[4] + """</name>
                            </valuemap>
"""
                SNMPOID2APPEND = "{#" + \
                    z[0].split("::")[1].upper() + "}," + z[1] + ","
                if(len(SNMPOIDS + SNMPOID2APPEND) < 501):
                    SNMPOIDS += SNMPOID2APPEND
                XML += """                        </item_prototype>
"""
            XML += """                    </item_prototypes>
                    <snmp_oid>discovery[""" + SNMPOIDS[:-1] + """]</snmp_oid>
"""
        XML += """                </discovery_rule>
"""
if len(DISCOVERY_RULES):
    XML += """            </discovery_rules>
"""

XML += """        </template>
    </templates>
"""

ENUMS
if len(ENUMS):
    XML += """    <value_maps>
"""
    for x in ENUMS:
        XML += """        <value_map>
            <name>""" + x + """</name>
            <mappings>
"""
        for y in ENUMS[x]:
            XML += """                <mapping>
                    <newvalue>""" + y[0] + """</newvalue>
                    <value>""" + y[1] + """</value>
                </mapping>
"""
        XML += """            </mappings>
        </value_map>
"""
if len(ENUMS):
    XML += """    </value_maps>
"""


# Finish the XML
XML += "</zabbix_export>"

# print(XML)
with open("template_" + removeColons(MIB_NAME).replace(" ", "_") + ".xml", "w") as xml_file:
    xml_file.write(XML)

print("Done")
