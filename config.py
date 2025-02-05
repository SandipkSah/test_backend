DEBUG = True  # Set to False for production environments

# Thresholds for tiers
TIERS = {
    "Gold": 1000,
    "Silber": 500,
    "Bronze": 0,
}

# Default admins
DEFAULT_ADMINS = [
    "653799c4-e7ea-4f28-b64d-b545e0700048",
    "78c4c12b-afb8-43eb-8111-364a4eaff302",
]

DB_URL="sqlite://essencifai"
##DB_URL=mssql+pyodbc://sa:Test0123%2BTest01@localhost:1433/essencifai?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes

