"""Tests for soap_demo.py — CustomerService and InvoiceService."""

from soap_demo import CustomerService, InvoiceService, Customer, Invoice, app
from spyne.server.wsgi import WsgiApplication


class TestCustomerService:
    def test_get_customer_by_known_email(self):
        result = CustomerService.GetCustomerByEmail(None, "alex@example.com")
        assert result.customerId == 1001
        assert result.fullName == "Alex Johnson"

    def test_get_customer_by_second_known_email(self):
        result = CustomerService.GetCustomerByEmail(None, "sam@example.com")
        assert result.customerId == 1002
        assert result.fullName == "Sam Patel"

    def test_get_customer_by_unknown_email(self):
        result = CustomerService.GetCustomerByEmail(None, "unknown@test.com")
        assert result.customerId == 0
        assert result.fullName == "NOT_FOUND"

    def test_get_customer_preserves_email_in_response(self):
        result = CustomerService.GetCustomerByEmail(None, "alex@example.com")
        assert result.email == "alex@example.com"


class TestInvoiceService:
    def test_get_invoices_for_customer_with_two_invoices(self):
        results = InvoiceService.GetInvoicesByCustomerId(None, 1001)
        assert len(results) == 2

    def test_get_invoices_for_customer_with_one_invoice(self):
        results = InvoiceService.GetInvoicesByCustomerId(None, 1002)
        assert len(results) == 1
        assert results[0].amount == 210

    def test_get_invoices_for_unknown_customer_returns_empty(self):
        results = InvoiceService.GetInvoicesByCustomerId(None, 9999)
        assert results == []

    def test_invoice_has_correct_currency(self):
        results = InvoiceService.GetInvoicesByCustomerId(None, 1001)
        assert all(inv.currency == "GBP" for inv in results)

    def test_invoice_has_correct_customer_id(self):
        results = InvoiceService.GetInvoicesByCustomerId(None, 1001)
        assert all(inv.customerId == 1001 for inv in results)


class TestSpyneWsgiApp:
    def test_wsdl_is_accessible(self):
        from io import BytesIO
        wsgi_app = WsgiApplication(app)

        environ = {
            "REQUEST_METHOD": "GET",
            "QUERY_STRING": "wsdl",
            "PATH_INFO": "/",
            "SERVER_NAME": "localhost",
            "SERVER_PORT": "8000",
            "wsgi.input": BytesIO(),
            "wsgi.url_scheme": "http",
        }
        response_body = []
        status_holder = []

        def start_response(status, headers):
            status_holder.append(status)

        for chunk in wsgi_app(environ, start_response):
            response_body.append(chunk)

        body = b"".join(response_body)
        assert "200" in status_holder[0]
        assert b"definitions" in body
