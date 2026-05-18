# 📧 Contact Information Summary

## ✅ All Information Configured Successfully!

### 👨‍💻 Developer Information

**Name**: Mohana Krishnan  
**Email**: mohankrishnan4099@gmail.com  
**Phone**: +91 8610844594  
**Location**: Chennai  
**LinkedIn**: https://www.linkedin.com/in/mohanakrishnan-n-576565312/

#### Where It's Configured:
1. **Backend Config** (`stresssense-backend/config.py`):
   ```python
   DEVELOPER_NAME = "Mohana Krishnan"
   DEVELOPER_EMAIL = "mohankrishnan4099@gmail.com"
   DEVELOPER_PHONE = "+91 8610844594"
   DEVELOPER_LOCATION = "Chennai"
   DEVELOPER_LINKEDIN = "https://www.linkedin.com/in/mohanakrishnan-n-576565312/"
   ```

2. **Dashboard Footer** (`stress-sense-wellness-main/src/routes/dashboard.tsx`):
   ```tsx
   <p>
     Developed by{" "}
     <a
       href="https://www.linkedin.com/in/mohanakrishnan-n-576565312/"
       target="_blank"
       rel="noopener noreferrer"
       className="text-primary hover:underline"
     >
       Mohana Krishnan
     </a>{" "}
     | StressSense v1.0.0
   </p>
   <p className="mt-1">
     Contact: hello@stresssense.app | +1 (555) 010-2025 | 410 Market St, San Francisco, CA
   </p>
   ```

3. **Email Templates** (`stresssense-backend/services/email_service.py`):
   ```html
   <div class="footer">
     <p>StressSense | 410 Market St, San Francisco, CA</p>
     <p>hello@stresssense.app | +1 (555) 010-2025</p>
     <p>Developed by Mohana Krishnan</p>
   </div>
   ```

---

### 🏢 Company Information

**Company Name**: StressSense  
**Email**: hello@stresssense.app  
**Phone**: +1 (555) 010-2025  
**Address**: 410 Market St, San Francisco, CA

#### Where It's Configured:
1. **Backend Config** (`stresssense-backend/config.py`):
   ```python
   EMAIL_FROM = "hello@stresssense.app"
   SUPPORT_EMAIL = "hello@stresssense.app"
   SUPPORT_PHONE = "+1 (555) 010-2025"
   COMPANY_ADDRESS = "410 Market St, San Francisco, CA"
   ```

2. **Email Service** (`stresssense-backend/services/email_service.py`):
   - Used in all email templates
   - Welcome emails
   - Stress alert emails

3. **Frontend Footer** (Dashboard):
   - Displayed at bottom of dashboard
   - Visible to all users

---

### 📧 Email Configuration (Resend API)

**API Key**: `re_dhkUgG1m_MhHK9PyTyzrtE3WhCm4U5dqN`  
**From Email**: hello@stresssense.app

#### Where It's Configured:
1. **Backend Config** (`stresssense-backend/config.py`):
   ```python
   RESEND_API_KEY = "re_dhkUgG1m_MhHK9PyTyzrtE3WhCm4U5dqN"
   EMAIL_FROM = "hello@stresssense.app"
   ```

2. **Email Service** (`stresssense-backend/services/email_service.py`):
   - Sends welcome emails on registration
   - Sends stress alert emails
   - Professional HTML templates

---

## 📍 Where Users See This Information

### 1. Dashboard Page
**Location**: Bottom of dashboard  
**Visible**: Always  
**Content**:
```
Developed by Mohana Krishnan | StressSense v1.0.0
Contact: hello@stresssense.app | +1 (555) 010-2025 | 410 Market St, San Francisco, CA
```

### 2. Welcome Email
**Sent**: On user registration  
**Content**:
- Company branding
- Support contact info
- Developer credits in footer

### 3. Stress Alert Email
**Sent**: When high stress detected  
**Content**:
- Company contact info
- Support email and phone
- Professional footer

---

## 🔍 How to Verify

### 1. Check Backend Config
```bash
cd stresssense-backend
cat config.py | grep -A 5 "Developer Info"
```

### 2. Check Dashboard Footer
1. Open http://localhost:8080/dashboard
2. Scroll to bottom
3. See developer and company info

### 3. Test Email
1. Register a new user
2. Check email for welcome message
3. See company and developer info in footer

---

## 📊 Information Summary Table

| Category | Field | Value | Location |
|----------|-------|-------|----------|
| **Developer** | Name | Mohana Krishnan | config.py, dashboard.tsx, emails |
| | Email | mohankrishnan4099@gmail.com | config.py |
| | Phone | +91 8610844594 | config.py |
| | Location | Chennai | config.py |
| | LinkedIn | [Profile Link](https://www.linkedin.com/in/mohanakrishnan-n-576565312/) | config.py, dashboard.tsx |
| **Company** | Name | StressSense | All pages |
| | Email | hello@stresssense.app | config.py, emails, footer |
| | Phone | +1 (555) 010-2025 | config.py, emails, footer |
| | Address | 410 Market St, San Francisco, CA | config.py, emails, footer |
| **Email** | API Key | re_dhkUgG1m_MhHK9PyTyzrtE3WhCm4U5dqN | config.py |
| | From | hello@stresssense.app | config.py, email_service.py |

---

## ✅ Verification Checklist

- [x] Developer name in config.py
- [x] Developer email in config.py
- [x] Developer phone in config.py
- [x] Developer location in config.py
- [x] Developer LinkedIn in config.py
- [x] Company email in config.py
- [x] Company phone in config.py
- [x] Company address in config.py
- [x] Resend API key in config.py
- [x] Developer credits in dashboard footer
- [x] Company info in dashboard footer
- [x] Developer credits in email templates
- [x] Company info in email templates
- [x] LinkedIn link clickable in dashboard

---

## 🎯 Quick Access

### View Dashboard Footer
```
http://localhost:8080/dashboard
(Scroll to bottom)
```

### View Config File
```bash
cd stresssense-backend
cat config.py
```

### View Email Service
```bash
cd stresssense-backend
cat services/email_service.py
```

### Test Email
```bash
# Register a new user at:
http://localhost:8080/register

# Check console for email sent confirmation
```

---

## 📝 Notes

1. **All information is properly configured** in both backend and frontend
2. **Developer credits** appear on dashboard footer with clickable LinkedIn link
3. **Company information** appears in footer and all email templates
4. **Email service** is configured with Resend API and ready to send
5. **Professional presentation** with proper formatting and styling

---

**Last Updated**: May 18, 2026  
**Status**: ✅ All Information Configured  
**Verified**: Backend Config, Frontend Display, Email Templates
