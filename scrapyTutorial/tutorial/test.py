class Response(object):
    def __init__(self):
        pass
    def xpath(self, xpath_expression):
	return Selector(xpath_expression)

class Selector(object):
    def __init__(self, exp):
    	pass
    def extract(self):
        return 'hello'


response = Response()
print response.xpath("//title").extract()


