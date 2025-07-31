"""
Customer Service Prompt Templates
"""

from .base import BaseTemplate, TemplateParameter

class CustomerServiceComplaintTemplate(BaseTemplate):
    """Template for handling customer complaints"""
    
    def __init__(self):
        super().__init__()
        self.name = "customer_service_complaint"
        self.description = "Handle customer complaints professionally and empathetically"
        self.category = "customer_service"
        self.examples = [
            {
                "customer_name": "John Doe",
                "issue_description": "Product arrived damaged",
                "order_number": "ORD-12345",
                "product_name": "Wireless Headphones"
            }
        ]
    
    def get_parameters(self):
        return [
            TemplateParameter(
                name="customer_name",
                description="Customer's full name",
                required=True,
                validation_regex=r"^[A-Za-z\s]+$"
            ),
            TemplateParameter(
                name="issue_description",
                description="Description of the customer's issue",
                required=True
            ),
            TemplateParameter(
                name="order_number",
                description="Customer's order number",
                required=True,
                validation_regex=r"^[A-Z]{3}-\d{5}$"
            ),
            TemplateParameter(
                name="product_name",
                description="Name of the product in question",
                required=False,
                default_value="the product"
            ),
            TemplateParameter(
                name="company_name",
                description="Your company name",
                required=False,
                default_value="our company"
            )
        ]
    
    def get_template_text(self):
        return """You are a professional customer service representative for {company_name}. 

A customer named {customer_name} has contacted us regarding order {order_number}. They are experiencing the following issue: {issue_description}

Please provide a professional, empathetic response that:
1. Acknowledges their concern
2. Shows understanding of the issue
3. Offers a specific solution or next steps
4. Maintains a positive, helpful tone
5. Includes relevant company policies if applicable

Keep the response concise but comprehensive, aiming for 2-3 paragraphs maximum."""

class CustomerServiceRefundTemplate(BaseTemplate):
    """Template for handling refund requests"""
    
    def __init__(self):
        super().__init__()
        self.name = "customer_service_refund"
        self.description = "Handle customer refund requests professionally"
        self.category = "customer_service"
        self.examples = [
            {
                "customer_name": "Jane Smith",
                "refund_reason": "Changed mind about purchase",
                "order_number": "ORD-67890",
                "purchase_date": "2024-01-15",
                "product_name": "Smart Watch"
            }
        ]
    
    def get_parameters(self):
        return [
            TemplateParameter(
                name="customer_name",
                description="Customer's full name",
                required=True,
                validation_regex=r"^[A-Za-z\s]+$"
            ),
            TemplateParameter(
                name="refund_reason",
                description="Reason for the refund request",
                required=True
            ),
            TemplateParameter(
                name="order_number",
                description="Customer's order number",
                required=True,
                validation_regex=r"^[A-Z]{3}-\d{5}$"
            ),
            TemplateParameter(
                name="purchase_date",
                description="Date of purchase",
                required=True,
                validation_regex=r"^\d{4}-\d{2}-\d{2}$"
            ),
            TemplateParameter(
                name="product_name",
                description="Name of the product",
                required=True
            ),
            TemplateParameter(
                name="company_name",
                description="Your company name",
                required=False,
                default_value="our company"
            )
        ]
    
    def get_template_text(self):
        return """You are a customer service representative for {company_name} handling a refund request.

Customer: {customer_name}
Order: {order_number}
Product: {product_name}
Purchase Date: {purchase_date}
Refund Reason: {refund_reason}

Please provide a professional response that:
1. Acknowledges their refund request
2. Explains the refund process and timeline
3. Mentions any relevant return policies
4. Provides clear next steps
5. Maintains a helpful, understanding tone

Include information about return shipping if applicable and any conditions that might affect the refund."""

class CustomerServiceProductInquiryTemplate(BaseTemplate):
    """Template for handling product inquiries"""
    
    def __init__(self):
        super().__init__()
        self.name = "customer_service_product_inquiry"
        self.description = "Handle customer product inquiries and questions"
        self.category = "customer_service"
        self.examples = [
            {
                "customer_name": "Mike Johnson",
                "product_name": "Gaming Laptop",
                "inquiry_type": "specifications",
                "specific_question": "What are the graphics card options?"
            }
        ]
    
    def get_parameters(self):
        return [
            TemplateParameter(
                name="customer_name",
                description="Customer's full name",
                required=True,
                validation_regex=r"^[A-Za-z\s]+$"
            ),
            TemplateParameter(
                name="product_name",
                description="Name of the product being inquired about",
                required=True
            ),
            TemplateParameter(
                name="inquiry_type",
                description="Type of inquiry (specifications, availability, pricing, etc.)",
                required=True
            ),
            TemplateParameter(
                name="specific_question",
                description="Customer's specific question or concern",
                required=True
            ),
            TemplateParameter(
                name="company_name",
                description="Your company name",
                required=False,
                default_value="our company"
            )
        ]
    
    def get_template_text(self):
        return """You are a knowledgeable customer service representative for {company_name}.

Customer {customer_name} has an inquiry about {product_name}.

Inquiry Type: {inquiry_type}
Specific Question: {specific_question}

Please provide a helpful, informative response that:
1. Addresses their specific question about {product_name}
2. Provides relevant technical details or information
3. Offers additional helpful information if appropriate
4. Maintains a professional, knowledgeable tone
5. Encourages further questions if needed

If you don't have specific information about {product_name}, provide general guidance and suggest they contact technical support for detailed specifications."""

class CustomerServiceTemplates:
    """Collection of customer service templates"""
    
    @staticmethod
    def get_all_templates():
        """Return all customer service templates"""
        return [
            CustomerServiceComplaintTemplate(),
            CustomerServiceRefundTemplate(),
            CustomerServiceProductInquiryTemplate()
        ] 