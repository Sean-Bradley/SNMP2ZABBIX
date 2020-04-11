# SNMP2ZABBIX

Convert MIB files to Zabbix Templates

Usage: python SNMP2ZABBIX.py *Path-to-MIB* *Base-OID* 

eg,

```
python SNMP2ZABBIX.py /var/lib/snmp/mibs/ietf/SNMPv2-MIB 1.3.6.1.2.1.1
```
or

```
python SNMP2ZABBIX.py /var/lib/snmp/mibs/ietf/IF-MIB 1.3.6.1.2.1.2
```

## Requirements

The server that you will use to create the templates will need to have several SNMP configurations and tools pre installed, plus the MIB files that you want to convert, plus any dependencies they require, and they will need to be correctly placed within the file system.

The script is also written in Python 2.7

### Ubuntu 18.04

Install required SNMP dependencies

```bash
sudo apt update
sudo apt install snmp snmp-mibs-downloader libsnmp-perl libsnmp-dev 
```

Test **mib2c** works
```bash
mib2c -h
```

Output should resemble this below with no errors displayed.
```text
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

```bash
python -V
```

If it doesn't say python 2.7.# then install python

```bash
apt install python
```

Now download the **SNMP2ZABBIX.py** tool

```curl
curl https://raw.githubusercontent.com/Sean-Bradley/SNMP2ZABBIX/master/SNMP2ZABBIX.py --output SNMP2ZABBIX.py
```

or

```wget
wget -O SNMP2ZABBIX.py https://raw.githubusercontent.com/Sean-Bradley/SNMP2ZABBIX/master/SNMP2ZABBIX.py
```


Now you should be ready to continue.

## Example 1

Create a Zabbix Template for SNMPv2-MIB

```bash
python SNMP2ZABBIX.py /var/lib/snmp/mibs/ietf/SNMPv2-MIB 1.3.6.1.2.1.1
```

A new file called **template_SNMPv2-MIB.xml** should be created

You can import this into the **Zabbix**-->**Configuration**-->**Templates** and assign it to a host that has a SNMP interface configured.


## Example 2

Create a Zabbix Template for IF-MIB

```bash
python SNMP2ZABBIX.py /var/lib/snmp/mibs/ietf/IF-MIB 1.3.6.1.2.1.2
```

A new file called **template_IF-MIB.xml** should be created

You can import this into the **Zabbix**-->**Configuration**-->**Templates** and assign it to a host that has a SNMP interface configured.


## Example 3

This is slightly more complicated.
First we need to download a generic Huawei MIB file.

```curl
curl http://www.circitor.fr/Mibs/Mib/H/HUAWEI-MIB.mib > HUAWEI-MIB.mib
```

Now to create a ZAbbix Template for the generic Huawei device

```curl
python SNMP2ZABBIX.py ./HUAWEI-MIB.mib 1.3.6.1
```

A new file **template_HUAWEI-MIB.xml** should have been created.

You can import this into the **Zabbix**-->**Configuration**-->**Templates** and assign it to a HUAWEI host that has a SNMP interface configured.

## Example 4

This is even more complicated. This MIB file has dependencies.


## Important
Note that all items, discovery rules and their item prototypes will be disabled by default after the import. You should decide which elements are important to enable for your needs based on the devices official documentation. Enabling all items, discovery rules and their item prototypes may put unnecessary strain on your Zabbix server resources and the SNMP devices so it is important to be sure to only enable just the elements that you actually need.

