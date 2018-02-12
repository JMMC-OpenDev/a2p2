#!/usr/bin/env python

__all__ = ['A2p2Client']

from astropy.samp import SAMPIntegratedClient

class Receiver(object):
    def __init__(self, client):
        self.client = client
        self.received = False
    def receive_call(self, private_key, sender_id, msg_id, mtype, params, extra):
        self.params = params
        self.received = True
        self.client.reply(msg_id, {"samp.status": "samp.ok", "samp.result": {}})
    def receive_notification(self, private_key, sender_id, mtype, params, extra):
        self.params = params
        self.received = True

    def clear(self):
        self.received = False
        self.params = None

    def get_last_message(self):
        pass ## TODO handle here a buffer ...


class A2p2SampClient():
    # TODO watch hub disconnection
    def __init__(self):
        self.sampClient = SAMPIntegratedClient("A2P2 samp relay") # TODO get title from main program class instead of HardCoded value
        self.connected = False

    def __del__(self):
        self.disconnect()

    def connect(self):
        self.sampClient.connect()
        # an error is thrown here if no hub is present

        # TODO get samp client name and display it in the UI

        self.set_connected(True)

        # Instantiate the receiver
        self.r = Receiver(self.sampClient)
        # Listen for any instructions to load a table
        self.sampClient.bind_receive_call("ob.load.data", self.r.receive_call)
        self.sampClient.bind_receive_notification("ob.load.data", self.r.receive_notification)
        # TODO fix next call which thwrows an execption
        # <class 'astropy.samp.errors.SAMPProxyError'>,
        # <Fault 1: 'java.lang.IllegalArgumentException: Bad arguments: samp.hub.notifyAll[string, map] got [string, string]'>
        self.sampClient.notify_all("hello")

    def disconnect(self):
        self.sampClient.disconnect()
        self.set_connected(False)

    def is_connected(self):
        return self.connected

    def set_connected(self, flag):
        self.connected = flag

    def has_message(self):
        return self.connected and self.r.received

    def clear_message(self):
        return self.r.clear()

    def get_ob_url(self):
        url = self.r.params['url']
        if url.startswith("file:///"):
            return url[7:]
        elif url.startswith("file:/"): # work arround bugged file urls
            return url[5:]
        return url



