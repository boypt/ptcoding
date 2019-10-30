import getpass
import telnetlib

class HWTelnet(object):

    def __init__(self, device_name, username, password, delay="2", port="23", debug_level=0):
        self.device_name = device_name
        self.username = username
        self.password = password
        self.delay = float(delay)
        self.port = int(port)
        self.debug_level = debug_level 

    def connect(self):
        import telnetlib
        import sys

        self.access = telnetlib.Telnet(self.device_name, self.port)
        self.access.set_debuglevel(self.debug_level)

        login_prompt = self.read_until("\(Username: \)|\(login: \)").decode('ascii')
        if 'login' in login_prompt:
            self.is_nexus = True
            self.write(self.username)
        elif 'Username' in login_prompt:
            self.is_nexus = False
            self.write(self.username)

        password_prompt = self.read_until('Password:')
        self.write(self.password)
        return self.access

    def write(self, cmd):
        return self.access.write((cmd+'\n').encode('ascii'))

    def read_until(self, word):
        return self.access.read_until(word.encode('ascii'), self.delay)

    def close(self):
        return self.access.close()

    def clear_buffer(self):
        pass

    def set_enable(self):
        import re

        if re.search('>$', self.command('\n')):
            return self.command("system-view")
        elif re.search(']$', self.command('\n')):
            return "Action: None. Already in enable mode."
        else:
            return "Error: Unable to determine user privilege status."

    def disable_paging(self):
        self.command("terminal echo-mode line")
        self.command('screen-length 0 temporary')

    def command(self, command):
        self.write(command)
        return self.read_until("\(]\)|\(>\)").decode('ascii')




def setVlanIp6(hw, vlan, ip):
    hw.set_enable()
    hw.command("interface Vlanif " + str(vlan))
    rest = hw.command("dis this | include ipv6 address .+:")
    rest = rest.split("\r\n")

    print(rest)

hw = HWTelnet("172.16.192.250", "admin", "Drcom123", delay=1, debug_level = 9)
hw.connect()
hw.disable_paging()
setVlanIp6(hw, 1024, "fe80::1")
# out = hw.command('dis cpu-usage history')
# print(out.decode('ascii'))