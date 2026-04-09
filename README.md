# Hackathon Multi-Dashboard Food Delivery App

A Python Flask web app with 4 dashboard roles:
- Customer
- Shopkeeper
- Delivery person
- Admin

Features:
- Role-based login/registration
- Email OTP verification for signup and password reset
- Order flow with 4-digit customer code
- Shopkeeper order acceptance and payment status
- Delivery acceptance and status tracking
- Admin panel with user/order overview
- SQLite backend

## Setup

1. Open terminal in `c:\Users\HP\Desktop\hackthon`
2. Create and activate a Python environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
4. (Optional) Configure email for real OTP delivery:
   - Create a `.env` file in the project root with:
     ```
     MAIL_USERNAME=your-email@gmail.com
     MAIL_PASSWORD=your-gmail-app-password
     MAIL_DEFAULT_SENDER=your-email@gmail.com
     DEBUG_OTP=false
     ```
   - For Gmail SMTP setup:
     1. Go to https://myaccount.google.com/security
     2. Enable 2-Step Verification
     3. Generate App Password: Search for "App passwords" > Select "Mail" > Generate
     4. Use the 16-character password in `.env` (not your regular password)
   - Alternative: Use any SMTP server (Outlook, Yahoo, etc.) with similar settings
   - For testing without email, set `DEBUG_OTP=true` to show OTPs on the page
   - Test email: Login as admin and click "Test Email" in dashboard
5. (Optional) Configure Razorpay for online payments:
   - Sign up at https://razorpay.com
   - Go to Dashboard > Settings > API Keys
   - Generate Test API Key ID and Key Secret
   - Add to `.env` file:
     ```
     RAZORPAY_KEY_ID=rzp_test_your_key_id_here
     RAZORPAY_KEY_SECRET=your_secret_key_here
     ```
   - For production, use Live API keys and set up webhooks for payment verification
6. Run the app:
   ```powershell
   python app.py
   ```
6. Open browser at `http://127.0.0.1:5000`
## For Network Access (Multiple Laptops)

To make the app accessible on other devices in the same network:

1. Find your computer's IP address (run `ipconfig` in PowerShell, look for IPv4 Address under your network adapter)
2. Edit `app.py` and change the last line to:
   ```python
   app.run(host='0.0.0.0', debug=True)
   ```
3. Run the app again
4. Open `http://YOUR_IP:5000` on other laptops (e.g., `http://192.168.1.100:5000`)

> Allow port 5000 in Windows Firewall if needed.
## Notes
- Admin account is created automatically if missing: `admin@rapidodelivery.app` / `Admin123!`
- Delivery tracking is simulated with timeline UI.
- Use different browser tabs or devices to open each dashboard role.
