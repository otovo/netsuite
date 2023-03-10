import urllib.parse

from . import zeep

__all__ = ("AsyncNetSuiteTransport",)


# def SuperInit(
#     self,
#     client=None,
#     wsdl_client=None,
#     cache=None,
#     timeout=300,
#     operation_timeout=None,
#     verify_ssl=True,
#     proxy=None,
#     ):
#     if httpx is None:
#         raise RuntimeError("The AsyncTransport is based on the httpx module")
#
#     self._close_session = False
#     self.cache = cache
#     self.wsdl_client = wsdl_client or httpx.Client(
#         verify=verify_ssl,
#         proxies=proxy,
#         timeout=timeout,
#         )
#     self.client = client or httpx.AsyncClient(
#         verify=verify_ssl,
#         proxies=proxy,
#         timeout=operation_timeout,
#         )
#     self.logger = logging.getLogger(__name__)
#
#     self.wsdl_client.headers = {
#         "User-Agent": "Zeep/%s (www.python-zeep.org)" % (get_version())
#         }
#     self.client.headers = {
#         "User-Agent": "Zeep/%s (www.python-zeep.org)" % (get_version())
#         }

class AsyncNetSuiteTransport(zeep.transports.AsyncTransport):
    """
    NetSuite company-specific domain wrapper for zeep.transports.transport

    Latest NetSuite WSDL now uses relative definition addresses

    zeep maps reflective remote calls to the base WSDL address,
    rather than the dynamic subscriber domain

    Wrap the zeep transports service with our address modifications
    """

    def __init__(self, wsdl_url, *args, **kwargs):
        parsed = urllib.parse.urlparse(wsdl_url)
        self._netsuite_base_url = f"{parsed.scheme}://{parsed.netloc}"
        self.session = kwargs.pop('session')
        super().__init__(*args, **kwargs)

    def _fix_address(self, address):
        """Munge the address to the company-specific domain, not the default"""
        idx = address.index("/", 8)
        path = address[idx:]
        return f"{self._netsuite_base_url}{path}"

    async def get(self, address, params, headers):
        return await super().get(self._fix_address(address), params, headers)

    async def post(self, address, message, headers):
        return await super().post(self._fix_address(address), message, headers)
