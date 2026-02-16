from wsgiref.simple_server import make_server
from spyne import Application, rpc, ServiceBase, Unicode, Integer, Iterable
from spyne import ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

# -----------------------------
# Data models
# -----------------------------
class Customer(ComplexModel):
    __namespace__ = "urn:demo"
    customerId = Integer
    email = Unicode
    fullName = Unicode

class Invoice(ComplexModel):
    __namespace__ = "urn:demo"
    invoiceId = Integer
    customerId = Integer
    amount = Integer
    currency = Unicode

# -----------------------------
# Fake in-memory "database"
# -----------------------------
CUSTOMERS = {
    "alex@example.com": {"customerId": 1001, "fullName": "Alex Johnson"},
    "sam@example.com": {"customerId": 1002, "fullName": "Sam Patel"},
}

INVOICES = {
    1001: [
        {"invoiceId": 501, "amount": 120, "currency": "GBP"},
        {"invoiceId": 502, "amount": 75,  "currency": "GBP"},
    ],
    1002: [
        {"invoiceId": 601, "amount": 210, "currency": "GBP"},
    ],
}

# -----------------------------
# Service #1: CustomerService
# -----------------------------
class CustomerService(ServiceBase):
    @rpc(Unicode, _returns=Customer)
    def GetCustomerByEmail(ctx, email):
        rec = CUSTOMERS.get(email)
        if not rec:
            return Customer(customerId=0, email=email, fullName="NOT_FOUND")
        return Customer(customerId=rec["customerId"], email=email, fullName=rec["fullName"])

# -----------------------------
# Service #2: InvoiceService
# Uses customerId returned by Service #1
# -----------------------------
class InvoiceService(ServiceBase):
    @rpc(Integer, _returns=Iterable(Invoice))
    def GetInvoicesByCustomerId(ctx, customerId):
        items = INVOICES.get(customerId, [])
        return [
            Invoice(
                invoiceId=i["invoiceId"],
                customerId=customerId,
                amount=i["amount"],
                currency=i["currency"],
            )
            for i in items
        ]

# One SOAP endpoint exposing both services
app = Application(
    [CustomerService, InvoiceService],
    tns="urn:demo",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11(),
)

if __name__ == "__main__":
    wsgi_app = WsgiApplication(app)
    server = make_server("0.0.0.0", 8000, wsgi_app)
    print("SOAP demo running:")
    print("  Endpoint: http://localhost:8000")
    print("  WSDL:     http://localhost:8000/?wsdl")
    server.serve_forever()
