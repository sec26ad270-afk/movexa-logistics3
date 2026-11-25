# Movexa Logistics — Starter MVP

A local prototype for a small courier/logistics booking workflow.

## Run on Windows 10/11

1. Install Python 3.10 or newer.
2. Extract this ZIP.
3. Open Command Prompt inside the `movexa_logistics` folder.
4. Run:

```bat
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py app.py
```

5. Open `http://127.0.0.1:5000` in your browser.

## Included in this first version

- Seller shipment booking
- Automatic demo tracking ID
- Customer delivery date and time-slot selection
- Capacity limit of five bookings per date/time slot
- Shipment tracking page
- Basic admin shipment list
- Basic delivery-partner status update page
- SQLite database created automatically

## Important prototype notes

This is a development demo, not a live courier network. It does not connect to Amazon, Flipkart, Xpressbees, payment gateways, maps, SMS, or real carrier systems. Those require authorized business/API integrations. Admin and partner pages are not password-protected yet; do not deploy this publicly or enter real customer personal data. Before launch, add authentication, role permissions, privacy/security controls, validated capacity and service-area rules, and production hosting.
