import json

def _read_json(config):
    with open(config, "r") as f:
        c = f.read()

    js = json.loads(c)

    return js

class UtilityConfig:
    def __init__(self, config):
        if type(config) is str:
            config = _read_json(config)

        self.name = config["name"]
        self.ip = config["ip"]
        self.port = config["port"]
        self.rsa_n = int(config["rsa_n"], 10)
        self.rsa_pub = int(config["rsa_pub"], 10)
        self.rsa_pri = int(config["rsa_pri"], 10)
        self.dh_p = int(config["dh_p"], 10)
        self.dh_g = int(config["dh_g"], 10)
        self.contacts = config["contacts"]


    def get_contacts(self):
        r = []
        for i in self.contacts:
            r.append(i["name"])

        return r

    def get_contact(self, name):
        for x in self.contacts:
            if x["name"] == name:
                return x
        raise Exception("Contact:", name, "not found.")

    def get_rsa_n(self, name):
        return int(self.get_contact(name)["rsa_n"], 10)
