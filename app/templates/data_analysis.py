"""
Data Analysis Prompt Templates
"""

from .base import BaseTemplate, TemplateParameter

class DataAnalysisCSVTemplate(BaseTemplate):
    """Template for CSV data analysis"""
    
    def __init__(self):
        super().__init__()
        self.name = "data_analysis_csv"
        self.description = "Analyze CSV data and provide insights"
        self.category = "data_analysis"
        self.examples = [
            {
                "data_description": "Sales data for Q1 2024",
                "analysis_goal": "Identify top performing products",
                "data_columns": "Product, Sales, Revenue, Region",
                "specific_questions": "Which products have the highest revenue?"
            }
        ]
    
    def get_parameters(self):
        return [
            TemplateParameter(
                name="data_description",
                description="Description of the CSV data being analyzed",
                required=True
            ),
            TemplateParameter(
                name="analysis_goal",
                description="Primary goal of the analysis",
                required=True
            ),
            TemplateParameter(
                name="data_columns",
                description="List of columns in the CSV data",
                required=True
            ),
            TemplateParameter(
                name="specific_questions",
                description="Specific questions to answer from the data",
                required=True
            ),
            TemplateParameter(
                name="data_format",
                description="Format of the data (CSV, JSON, etc.)",
                required=False,
                default_value="CSV"
            )
        ]
    
    def get_template_text(self):
        return """You are a data analyst working with {data_format} data.

Data Description: {data_description}
Data Columns: {data_columns}
Analysis Goal: {analysis_goal}
Specific Questions: {specific_questions}

Please provide a comprehensive analysis that includes:
1. Key insights from the data
2. Statistical summaries (if applicable)
3. Patterns or trends identified
4. Recommendations based on the findings
5. Visual suggestions (charts, graphs) that would be helpful

Focus on actionable insights and clear explanations that a business audience can understand."""

class DataAnalysisStatisticalTemplate(BaseTemplate):
    """Template for statistical data analysis"""
    
    def __init__(self):
        super().__init__()
        self.name = "data_analysis_statistical"
        self.description = "Provide statistical summaries and analysis"
        self.category = "data_analysis"
        self.examples = [
            {
                "data_description": "Customer satisfaction scores",
                "analysis_type": "descriptive statistics",
                "variables": "Satisfaction Score, Response Time, Support Quality",
                "sample_size": "1000 responses"
            }
        ]
    
    def get_parameters(self):
        return [
            TemplateParameter(
                name="data_description",
                description="Description of the data being analyzed",
                required=True
            ),
            TemplateParameter(
                name="analysis_type",
                description="Type of statistical analysis needed",
                required=True
            ),
            TemplateParameter(
                name="variables",
                description="Variables or metrics to analyze",
                required=True
            ),
            TemplateParameter(
                name="sample_size",
                description="Size of the dataset",
                required=False,
                default_value="unknown"
            ),
            TemplateParameter(
                name="confidence_level",
                description="Confidence level for statistical tests",
                required=False,
                default_value="95%"
            )
        ]
    
    def get_template_text(self):
        return """You are a statistical analyst working with the following data:

Data Description: {data_description}
Analysis Type: {analysis_type}
Variables: {variables}
Sample Size: {sample_size}
Confidence Level: {confidence_level}

Please provide a statistical analysis that includes:
1. Descriptive statistics (mean, median, standard deviation, etc.)
2. Distribution analysis
3. Correlation analysis (if multiple variables)
4. Statistical significance tests (if applicable)
5. Interpretation of results in plain language
6. Recommendations based on statistical findings

Present the results in a clear, professional manner suitable for both technical and non-technical audiences."""

class DataAnalysisTrendTemplate(BaseTemplate):
    """Template for trend analysis"""
    
    def __init__(self):
        super().__init__()
        self.name = "data_analysis_trend"
        self.description = "Analyze trends and patterns in time-series data"
        self.category = "data_analysis"
        self.examples = [
            {
                "data_description": "Monthly sales data for 2023",
                "trend_period": "12 months",
                "key_metrics": "Revenue, Units Sold, Customer Acquisition",
                "seasonality": "Quarterly patterns"
            }
        ]
    
    def get_parameters(self):
        return [
            TemplateParameter(
                name="data_description",
                description="Description of the time-series data",
                required=True
            ),
            TemplateParameter(
                name="trend_period",
                description="Time period for trend analysis",
                required=True
            ),
            TemplateParameter(
                name="key_metrics",
                description="Key metrics to analyze for trends",
                required=True
            ),
            TemplateParameter(
                name="seasonality",
                description="Expected seasonal patterns",
                required=False,
                default_value="None identified"
            ),
            TemplateParameter(
                name="forecast_horizon",
                description="Future period to forecast",
                required=False,
                default_value="3 months"
            )
        ]
    
    def get_template_text(self):
        return """You are a trend analyst examining time-series data.

Data Description: {data_description}
Trend Period: {trend_period}
Key Metrics: {key_metrics}
Seasonality: {seasonality}
Forecast Horizon: {forecast_horizon}

Please provide a comprehensive trend analysis that includes:
1. Overall trend direction and magnitude
2. Seasonal patterns and variations
3. Anomalies or unusual patterns
4. Trend drivers and contributing factors
5. Forecast projections and confidence intervals
6. Business implications and recommendations

Focus on identifying actionable insights and explaining the business impact of the trends observed."""

class DataAnalysisTemplates:
    """Collection of data analysis templates"""
    
    @staticmethod
    def get_all_templates():
        """Return all data analysis templates"""
        return [
            DataAnalysisCSVTemplate(),
            DataAnalysisStatisticalTemplate(),
            DataAnalysisTrendTemplate()
        ] 