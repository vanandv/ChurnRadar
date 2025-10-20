### ChurnRadar Payment-Failure Auto-Save Demo — Sponsor README

Demo URL: https://share.streamlit.io/YOUR_GITHUB_USERNAME/YOUR_REPO/main/app.py

One-line purpose  
Demonstrate detection of failed-payment risk, explain drivers, and auto-publish a vendor-neutral save payload to an ESP webhook.

Required sponsor actions before kickoff
- Provide an anonymized billing CSV export with header: user_id,event_date,last_payment_status,failed_payment_count_90d,days_since_last_payment,tenure_months,ARPU,email_token,phone_token.  
- Provide a webhook endpoint URL that accepts POST JSON for payload verification or approve use of webhook.site for testing.  
- Approve a 2-week paid POC LOI to enable production-grade data access and measurement.

What you will see in the demo
- Top N high-risk users with score, plain-language top-3 drivers, recommended action, and estimated dollars saved.  
- One-click publish of a vendor-neutral JSON payload to the provided webhook.  
- Example mock ESP email template populated with payload tokens.  
- Measurement plan summary for an 8-week randomized pilot.

Security and data handling commitments
- Only anonymized or tokenized identifiers will be used.  
- No raw payment card data or PII will be uploaded to the demo.  
- A simple Data Processing Agreement is required before using any sponsor production data in the POC.

Logistics and timeline
- Demo preparation time after receiving sample CSV and webhook: 24 to 48 hours.  
- Suggested kickoff: 30 to 45 minute walkthrough followed by a technical handoff call.  
- POC timeline: 2 weeks of integration and pilot measurement.

Contacts
- Product Lead: Mike Garcia — mike.garcia@example.com  
- ML Lead: Prashant Kulkarni — prashant.k@example.com  
- Engineering Lead: Rajesh Eddala — rajesh.e@example.com  
- Business Lead: Eric A Bruce — eric.bruce@example.com  
- GTM Lead: Jeanna Jones — jeanna.j@example.com  
- Design & Ops: Anand V. Vajjala — anand.v@example.com

Next steps to start
- Upload sample CSV to the repo or send via secure file transfer to the Engineering Lead.  
- Provide webhook URL and confirm a kickoff slot.  
- Sign the POC LOI and DPA to begin integration.
