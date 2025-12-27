# How to Test the SkillBridge Application

Since notifications are now implemented, follow these steps to verify the full "Order -> Notification" flow.

## Prerequisites
1.  **Restart the Server**: Make sure you have restarted `python app.py` to apply the latest code changes.
2.  **Two Browsers**: Use two different browsers (e.g., Chrome and Firefox) or one browser + one **Incognito/Private** window. This allows you to be logged in as two different users simultaneously.

## Step-by-Step Test

### 1. Prepare the Provider (Seller)
1.  Open **Browser A**.
2.  Log in as your main user (or register a new one, e.g., `provider`).
3.  Go to **Sell Your Skills** and create a service (if you haven't already).
    *   *Note: This automatically makes you a "Provider".*
4.  **Stay logged in** on this browser.

### 2. Prepare the Client (Buyer)
1.  Open **Browser B** (Incognito).
2.  Register a *brand new user* (e.g., `buyer`).
    *   *Note: You should see the default avatar (initials) for this new user.*
3.  Go to **Find Services**.
4.  Click on the service created by the Provider in Step 1.

### 3. Place an Order
1.  In **Browser B** (Client), on the service detail page, scroll down or click "Order Now".
2.  Fill in some mock requirements (e.g., "I need this done ASAP").
3.  Click **Place Order**.
4.  You should be redirected to your Dashboard with a success message: "Order placed successfully!".

### 4. Verify Notification
1.  Switch back to **Browser A** (Provider).
2.  **Refresh the page**. (Notifications are checked when the page loads).
3.  Look at the **Bell Icon** in the top right header.
    *   You should see a **red badge** with the number `1`.
4.  Click the Bell Icon.
    *   You should see notification: **"New Order Received"**.
    *   Message: "You have a new order for [Service Name] from [Client Name]".
5.  Click the notification item.
    *   It should take you to your **Dashboard > Orders** tab.
    *   You will see the new order listed under "Orders Received".

## Notes
- **Email/Facebook Login**: If you click these buttons on the Login page, you will now see an alert explaining they are not configured.
- **Search Bar**: On the home page, the search bar is now a clean, pill-shaped design.
