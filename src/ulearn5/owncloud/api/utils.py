import xml.etree.ElementTree as ET


class ResponseError(Exception):
    def __init__(self, res, errorType):
        if type(res) is int:
            code = res
        else:
            code = res.status_code
            self.res = res
        Exception.__init__(self, errorType + " error: %i" % code)
        self.status_code = code

    def get_resource_body(self):
        if self.res is not None:
            return self.res.content
        else:
            return None


class OCSResponseError(ResponseError):
    def __init__(self, res):
        ResponseError.__init__(self, res, "OCS")

    def get_resource_body(self):
        if self.res is not None:
            import xml.etree.ElementTree as ElementTree
            try:
                root_element = ElementTree.fromstringlist(self.res.content)
                if root_element.tag == 'message':
                    return root_element.text
            except ET.ParseError:
                return self.res.content
        else:
            return None


class HTTPResponseError(ResponseError):
    def __init__(self, res):
        ResponseError.__init__(self, res, "HTTP")
