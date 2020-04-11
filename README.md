# SNMP2ZABBIX

Convert MIB files to Zabbix Templates

Example Usage :

```
env MIBS="+./HUAWEI-MIB.mib" mib2c -c snmp2zabbix.conf 1.3.6.1

python snmp2zabbix.py ./HUAWEI-MIB.mib 1.3.6.1

python snmp2zabbix.py /var/lib/snmp/mibs/ietf/SNMPv2-MIB 1.3.6.1.2.1.1
python snmp2zabbix.py /var/lib/snmp/mibs/ietf/IF-MIB 1.3.6.1.2.1.2
```