from zeep import Client



# Config soap server url
SOAP_URL = 'http://192.168.0.55:8090/wsdl/IOrionPro'

# Config client
client = Client(wsdl = SOAP_URL)
