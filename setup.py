from setuptools import setup, find_packages

setup(
    name="azure-cost-optimizer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "azure-mgmt-costmanagement==3.0.0",
        "azure-mgmt-monitor==5.0.0",
        "azure-mgmt-resource==21.1.0",
        "azure-mgmt-advisor==9.0.0",
        "azure-mgmt-compute==29.1.0",
        "azure-mgmt-subscription==3.1.1",
        "azure-identity==1.12.0",
        "pandas==2.0.3",
        "numpy==1.24.3",
        "scikit-learn==1.3.0",
        "plotly==5.15.0",
        "dash==2.11.1",
        "dash-bootstrap-components==1.4.1",
        "python-dotenv==1.0.0",
    ],
    python_requires=">=3.8",
)
