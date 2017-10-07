class StrawPoll:
    import requests, lxml.html, json

    url = "http://www.strawpoll.me"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    id = 0

    def __init__(self, id):
        self.id = id

    def getOptions(self, proxy = None):
        request = self.requests.get("%s/%s" % (self.url, self.id), headers=self.headers, proxies=proxy, timeout=10)
        html = self.lxml.html.fromstring(request.text)

        options = []

        for option in html.xpath("//input[starts-with(@id,'field-options-')]"):
            label = option.getnext().find("span").text.strip()
            name = option.get("name")
            value = int(option.get("value"))

            options.append({"label": label, "name": name, "value": value})

        return options

    def getTokens(self, proxy = None):
        try:
            request = self.requests.get("%s/%s" % (self.url, self.id), headers=self.headers, proxies=proxy, timeout=10)
            html = self.lxml.html.fromstring(request.text)

            return [html.xpath('//*[@id="field-security-token"]')[0].get("value"), html.xpath('//*[@id="field-authenticity-token"]')[0].get("name")]
        except:
            return None

    def vote(self, options, proxy = None):
        try:
            tokens = self.getTokens(proxy)

            if tokens == None:
                return False

            data = [("security-token", tokens[0]), (tokens[1], "")]

            for option in strawpoll.getOptions(proxy):
                if (type(options) is tuple and option['value'] in options) or (
                        type(options) is str and str(option['value']) == options):
                    data.append((option['name'], option['value']))

            request = self.requests.post("%s/%s" % (self.url, self.id), headers=self.headers, data=data, proxies=proxy, timeout=10)
            json = self.json.loads(request.text)
            return json['success'] == "success"
        except:
            return False

class StrawPollBot:
    import threading, time

    strawpoll = None

    def __init__(self, strawpoll):
        self.strawpoll = strawpoll

    def vote(self, threadId, options, proxies):
        for proxy in proxies:
            print("threadId: %d [ proxy: %s - result: %s - status: %d/%d ]" % (threadId, proxy, self.strawpoll.vote(options, {"http": proxy}), proxies.index(proxy), len(proxies)))

    def start(self, options, proxies):
        threads = []
        threadId = 0

        for i in range(0, len(proxies), 20):
            threads.append(self.threading.Thread(target=self.vote, args=(threadId, options, proxies[i:i + 20])))
            threadId += 1

        [ thread.start() for thread in threads ]
        [ thread.join() for thread in threads ]

if __name__ == "__main__":
    pollId = input("Please enter the poll id: ")
    strawpoll = StrawPoll(pollId)

    print("# Available options ( id, label ):")
    for option in strawpoll.getOptions():
        print("%d - %s" % (option['value'], option['label']))

    options = input("Please select the option(s): ")
    proxies = [ line.strip() for line in open('proxies.txt', 'r') ]

    StrawPollBot(strawpoll).start(options, proxies)
