from jabberbot import JabberBot, botcmd
import it_config as config
import requests
import logging
import xmpp
import time

class ItGifsBot(JabberBot):
    def __init__(self):
        self._last_send_time = 0
        self.PING_FREQUENCY = 50
        self.username = config.USER_JID
        self.password = config.PASSWORD
        self.host = config.MUC_HOST
        super(ItGifsBot, self).__init__(username=self.username,
                                        password=self.password)
        self.__debug = True
        for room in config.ROOMS:
            self.join_room(room, config.USERNAME)

    def _idle_ping(self):
        if self.PING_FREQUENCY \
           and time.time() - self._last_send_time > self.PING_FREQUENCY:
            self._last_send_time = time.time()
            self.send_message(' ')

    def to_bot(self, message, to):
        if message.startswith(config.HL_MSG):
            return message[len(config.HL_MSG):]

    def send_message(self, mess):
        self._last_send_time = time.time()
        self.connect().send(mess)

    def callback_message(self, conn, mess):
        message = unicode(mess.getBody()).strip()
        if message is None:
            return
        message = self.to_bot(message, mess.getTo())
        if message is None:
            return
        mess.setBody(message)
        super(ItGifsBot, self).callback_message(conn, mess)

    def join_room(self, room, username=None):
        NS_MUC = 'http://jabber.org/protocol/muc'
        if username is None:
            username = self.username.split('@')[0]
        my_room_JID = u'/'.join((room, username))
        pres = xmpp.Presence(to=my_room_JID)
        pres.setTag('x', namespace=NS_MUC)
        pres.getTag('x').addChild('history', {'maxchars': '0',
                                              'maxstanzas': '0'})
        self.connect().send(pres)

    def _get_gif(self, mess, args, path=""):
        if args is None:
            return
        r = requests.get(config.GIFS_URL + path + args)
        if r.status_code == 404:
            self.send_simple_reply(mess, "No gif found for %s" % args)
            return
        content = r.json()
        self.send_simple_reply(mess,  "(source from: " + str(content.values()[0][1]) +") "  + str(content.values()[0][0]))

    @botcmd
    def gif(self, mess=None, args=None):
        """ @gimme gif <your tags here> """
        self._get_gif(mess, args)

    @botcmd
    def idgif(self, mess=None, args=None):
        """ @gimme gifbyid <id> """
        self._get_gif(mess, args, "id/")

    @botcmd
    def delgif(self, mess=None, args=None):
        """ @gimme delgif <id> """
        if args is None:
            return
        r = requests.delete(config.GIFS_URL + "id/" + args)
        content = r.json()
        self.send_simple_reply(mess, "Done ! ;)")

    @botcmd
    def addgif(self, mess=None, args=None):
        """ @gimme addgif <url img> <url source> <tags> """
        if args is None:
            return
        l = args.split(' ', 2)
        if len(l) != 3:
            self.send_simple_reply(mess, "Bad format for %s, usage: addgif <url img> <url source> <tags>" % args)
            return
        r = requests.get(config.GIFS_URL + "?url=%s&source=%s&tags=%s" % (l[0], l[1], l[2]))
        content = r.json()
        if r.status_code != 200:
            self.send_simple_reply(mess, "Gif successfully added with id %s ! ;)" % content.values()[0][0])
            return
        self.send_simple_reply(mess, "Something bad happened during the add of the gif")

if __name__ == '__main__':
    logging.basicConfig()
    try:
        bot = ItGifsBot()
        bot.serve_forever()
    except Exception as e:
        print "Shit happens %s" % e
        raise
