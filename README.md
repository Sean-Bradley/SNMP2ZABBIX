# SNMP2ZABBIX

snmp2zabbix is a python script that allows you to create Zabbix Templates from MIB files.

Usage: python SNMP2ZABBIX.py *Path-to-MIB-file* *Base-OID* 

eg, 

### Ubuntu 18
``` 
python SNMP2ZABBIX.py /var/lib/snmp/mibs/ietf/SNMPv2-MIB 1.3.6.1.2.1.1
```

### Centos 7

``` 
python SNMP2ZABBIX.py /usr/share/snmp/mibs/SNMPv2-MIB.txt 1.3.6.1.2.1.1
```

## Requirements

The server that you will use to create the templates will need to have several SNMP configurations and tools pre installed, plus the MIB files that you want to convert, plus any dependencies they require, and they will need to be correctly placed within the file system.

The **SNMP2ZABBIX.py** script is also written in Python 2.7

## Install required SNMP dependencies

### Ubuntu 18

``` bash
sudo apt update
sudo apt install snmp snmp-mibs-downloader libsnmp-perl libsnmp-dev 
```

### Centos 7 

``` bash
yum check-update
yum install net-snmp-utils net-snmp-libs net-snmp-perl
```

Test **mib2c** works

``` bash
mib2c -h
```

Output should resemble this below with no errors displayed.

``` bash
/usr/bin/mib2c [-h] [-c configfile] [-f prefix] mibNode

  -h            This message.

  -c configfile Specifies the configuration file to use
                that dictates what the output of mib2c will look like.

  -I PATH       Specifies a path to look for configuration files in

  -f prefix     Specifies the output prefix to use.  All code
                will be put into prefix.c and prefix.h

  -d            debugging output (don't do it.  trust me.)

  -S VAR=VAL    Set $VAR variable to $VAL

  -i            Don't run indent on the resulting code

  -s            Don't look for mibNode.sed and run sed on the resulting code

  mibNode       The name of the top level mib node you want to
                generate code for.  By default, the code will be stored in
                mibNode.c and mibNode.h (use the -f flag to change this)
```

Try python

``` bash
python -V
```

If it doesn't say python 2.7.# then install python

### Ubuntu 18

``` bash
apt install python
```

### Centos 7

``` bash
yum install python
```

Now download the **SNMP2ZABBIX.py** tool

``` bash
curl https://raw.githubusercontent.com/Sean-Bradley/SNMP2ZABBIX/master/SNMP2ZABBIX.py --output SNMP2ZABBIX.py
```

Now you should be ready to continue.

## Example 1

Create a Zabbix Template for SNMPv2-MIB

### Ubuntu 18

``` bash
python SNMP2ZABBIX.py /var/lib/snmp/mibs/ietf/SNMPv2-MIB 1.3.6.1.2.1.1
```

### Centos 7

``` bash
python SNMP2ZABBIX.py /usr/share/snmp/mibs/SNMPv2-MIB.txt 1.3.6.1.2.1.1
```

A new file called **template_SNMPv2-MIB.xml** should be created

You can import this into the **Zabbix**-->**Configuration**-->**Templates** and assign it to a host that has an SNMP interface configured.

## Example 2

Create a Zabbix Template for IF-MIB

### Ubuntu 18

``` bash
python SNMP2ZABBIX.py /var/lib/snmp/mibs/ietf/IF-MIB 1.3.6.1.2.1.2
```

### Centos 7

``` bash
python SNMP2ZABBIX.py /usr/share/snmp/mibs/IF-MIB.txt 1.3.6.1.2.1.2
```

A new file called **template_IF-MIB.xml** should be created

You can import this into the **Zabbix**-->**Configuration**-->**Templates** and assign it to a host that has an SNMP interface configured.

## Example 3

This is slightly more complicated.
First we need to download a generic Huawei MIB file.

``` bash
curl http://www.circitor.fr/Mibs/Mib/H/HUAWEI-MIB.mib > HUAWEI-MIB.mib
```

Now to create a Zabbix Template for the generic Huawei device

``` bash
python SNMP2ZABBIX.py ./HUAWEI-MIB.mib 1.3.6.1
```

A new file **template_HUAWEI-MIB.xml** should have been created.

You can import this into the **Zabbix**-->**Configuration**-->**Templates** and assign it to a HUAWEI host that has an SNMP interface configured.

## Example 4

This is even more complicated. This MIB file has dependencies.

This is for a CISCO-VTP

``` bash
curl -s ftp://ftp.cisco.com/pub/mibs/v2/CISCO-VTP-MIB.my > CISCO-VTP-MIB.my
```

This MIB requires 2 other MIBs, so also download them. The script won't work otherwise.

``` bash
curl -s ftp://ftp.cisco.com/pub/mibs/v2/CISCO-TC.my > CISCO-TC.my
curl -s ftp://ftp.cisco.com/pub/mibs/v2/CISCO-SMI.my > CISCO-SMI.my
```

Now place all 3 files into one of the mib search paths. I will use */usr/share/snmp/mibs/*

``` bash
cp CISCO-SMI.my /usr/share/snmp/mibs/
cp CISCO-TC.my /usr/share/snmp/mibs/
cp CISCO-VTP-MIB.my /usr/share/snmp/mibs/
```

``` bash
python SNMP2ZABBIX.py /usr/share/snmp/mibs/CISCO-VTP-MIB.my 1.3.6.1.2
```

A new file **template_CISCO-VTP-MIB.xml** should have been created.

You can import this into the **Zabbix**-->**Configuration**-->**Templates** and assign it to a CISCO host that has an SNMP interface configured.

## Important

Note that all items, discovery rules and their item prototypes will be disabled by default after the import. You should decide which elements are important to enable for your needs based on the devices official documentation. Enabling all items, discovery rules and their item prototypes may put unnecessary strain on your Zabbix server resources and the SNMP devices so it is important to be sure to only enable just the elements that you actually need.

## Further Notes

You need to tell it which MIB file you want to convert and which base OID to start translating from.

Selecting which Base OID to use will take some research.

I suggest doing an *snmptranslate* on the MIB file first, and select one of the Base OIDs returned.(see below)

If you choose a Base OID to close to the root, it will result in a larger template file being generated.

If you choose an OID to specific, then the script may error, or your generated template will contain no useful items or discovery rules.

eg, 

This produces a very small template file with almost no useful information.

``` bash
python SNMP2ZABBIX.py /usr/share/snmp/mibs/CISCO-VTP-MIB.my 1.3.6.1.2.1.1
```

This is better, but it could be better still, 

``` bash
python SNMP2ZABBIX.py /usr/share/snmp/mibs/CISCO-VTP-MIB.my 1.3.6.1.2.1
```

this may be just fine, 

``` bash
python SNMP2ZABBIX.py /usr/share/snmp/mibs/CISCO-VTP-MIB.my 1.3.6.1.2
```

this may even be better. Only you can decide.

``` bash
python SNMP2ZABBIX.py /usr/share/snmp/mibs/CISCO-VTP-MIB.my 1.3.6.1
```

### Example *snmptranslate*

Example *snmptranslate* to find an appropriate OID to start from.

``` bash
snmptranslate -Tz -m /usr/share/snmp/mibs/CISCO-VTP-MIB.my
```

This will produce a lot of MIBs and corresponding OIDs

``` text
"org"                   "1.3"
"dod"                   "1.3.6"
"internet"              "1.3.6.1"
"directory"             "1.3.6.1.1"
"mgmt"                  "1.3.6.1.2"
"mib-2"                 "1.3.6.1.2.1"
"system"                "1.3.6.1.2.1.1"
"sysDescr"              "1.3.6.1.2.1.1.1"
"sysObjectID"           "1.3.6.1.2.1.1.2"
"sysUpTime"             "1.3.6.1.2.1.1.3"
...
etc
```

From the above response, 

* Using 1.3.6.1.2.1.1 will produce a template to small, 
* Using 1.3.6.1.2.1 will produce a better template, 
* Using 1.3.6.1.2 will produce an even better template with more coverage.

Only you can decide which you find is more useful for your needs.

Other *snmptranslate* examples

### Ubuntu 18

``` bash
snmptranslate -Tz -m /var/lib/snmp/mibs/ietf/SNMPv2-MIB
```

``` bash
snmptranslate -Tz -m /var/lib/snmp/mibs/ietf/IF-MIB
```

### Centos 7

``` bash
snmptranslate -Tz -m /usr/share/snmp/mibs/SNMPv2-MIB.txt
```

``` bash
snmptranslate -Tz -m /usr/share/snmp/mibs/IF-MIB.txt
```

The correct path of your MIBs files will depend on your OS.

