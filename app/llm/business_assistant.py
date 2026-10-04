
import os

from dotenv import load_dotenv
from groq import Groq

from app.database.database_manager import DatabaseManager


class BusinessAssistant:
    """Provides an LLM-powered assistant for business data."""

    def __init__(self, database_manager=None):
        # Load the API key from the project's .env file.
        load_dotenv()

        self.database_manager = (
            database_manager or DatabaseManager()
        )

        api_key = os.getenv("GROQ_API_KEY")

        self.client = None
        self.model = "openai/gpt-oss-20b"

        if not api_key:
            return

        self.client = Groq(
            api_key=api_key
        )

    def get_business_summary(self):
        """Return counts of the current business records."""

        customers = self.database_manager.get_customers()
        products = self.database_manager.get_products()
        orders = self.database_manager.get_orders()
        invoices = self.database_manager.get_invoices()
        payments = self.database_manager.get_payments()

        return {
            "customers": len(customers),
            "products": len(products),
            "orders": len(orders),
            "invoices": len(invoices),
            "payments": len(payments),
        }

    def get_business_data(self):
        """Return the actual business records from the database."""

        return {
            "customers": self.database_manager.get_customers(),
            "products": self.database_manager.get_products(),
            "orders": self.database_manager.get_orders(),
            "invoices": self.database_manager.get_invoices(),
            "payments": self.database_manager.get_payments(),
        }

    def get_business_context(self):
        """Create detailed business context for the LLM."""

        data = self.get_business_data()

        customers = data["customers"]
        products = data["products"]
        orders = data["orders"]
        invoices = data["invoices"]
        payments = data["payments"]

        context = "CURRENT BUSINESS DATA\n"
        context += "=====================\n\n"

        context += f"CUSTOMERS ({len(customers)}):\n"

        for customer in customers:
            customer_id, name, email = customer

            context += (
                f"- ID: {customer_id}, "
                f"Name: {name}, "
                f"Email: {email}\n"
            )

        context += "\n"

        context += f"PRODUCTS ({len(products)}):\n"

        for product in products:
            product_id, name, price = product

            context += (
                f"- ID: {product_id}, "
                f"Name: {name}, "
                f"Price: {price}\n"
            )

        context += "\n"

        context += f"ORDERS ({len(orders)}):\n"

        for order in orders:
            order_id, customer_id, product_id, quantity = order

            context += (
                f"- Order ID: {order_id}, "
                f"Customer ID: {customer_id}, "
                f"Product ID: {product_id}, "
                f"Quantity: {quantity}\n"
            )

        context += "\n"

        context += f"INVOICES ({len(invoices)}):\n"

        for invoice in invoices:
            invoice_id, order_id, total_amount = invoice

            context += (
                f"- Invoice ID: {invoice_id}, "
                f"Order ID: {order_id}, "
                f"Total Amount: {total_amount}\n"
            )

        context += "\n"

        context += f"PAYMENTS ({len(payments)}):\n"

        for payment in payments:
            payment_id, invoice_id, amount = payment

            context += (
                f"- Payment ID: {payment_id}, "
                f"Invoice ID: {invoice_id}, "
                f"Amount: {amount}\n"
            )

        return context

    def ask(self, question):
        """Ask the LLM a question using current business data."""

        if not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        if self.client is None:
            raise RuntimeError(
                "AI Copilot is not configured. Add GROQ_API_KEY to your environment or .env file."
            )

        business_context = (
            self.get_business_context()
        )

        system_prompt = (
            "You are a helpful business assistant. "
            "Answer questions using ONLY the provided "
            "business data. "
            "Do not invent business facts. "
            "Use the actual records when answering questions "
            "about customers, products, orders, invoices, "
            "or payments. "
            "If the available data is not enough to answer, "
            "clearly say that the information is not available.\n\n"
            f"{business_context}"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content
