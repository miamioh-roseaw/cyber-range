# VLAN Practice Lab

In this lab you will create VLANs 10 and 20 on a switch, and assign ports.

## Tasks

- Create VLANs 10 and 20
- Name them `USERS` and `SERVERS`
- Assign interfaces as follows:
  - `Gi0/1-2` → VLAN 10
  - `Gi0/3-4` → VLAN 20

### Commands

```text
conf t
vlan 10
 name USERS
vlan 20
 name SERVERS
interface range gi0/1-2
 switchport mode access
 switchport access vlan 10
interface range gi0/3-4
 switchport mode access
 switchport access vlan 20
end
wr mem
```
