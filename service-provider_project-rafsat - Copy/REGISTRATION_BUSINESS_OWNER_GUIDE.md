# 🎯 Business Owner Registration Guide

## ✅ What Was Added to Registration Form

The registration form now includes a **Role Selection** field that allows users to choose between:

1. **Customer** (default)

   - Browse and book services
   - View business profiles
   - Manage their bookings

2. **Business Owner** (NEW!)
   - Create and manage service businesses
   - List services they provide
   - Accept/reject booking requests
   - View analytics

---

## 📋 Registration Form Structure

```
┌─────────────────────────────────────────┐
│           REGISTER FORM                 │
├─────────────────────────────────────────┤
│ Name: [_____________]                   │
│ Email: [_____________]                  │
│ Phone: [_____________]                  │
│ Password: [_____________]                │
│                                         │
│ ⭐ I am registering as:                 │
│ ◯ Customer                              │ (default)
│ ◉ Business Owner                        │ (NEW)
│                                         │
│ Street/House: [_____________]           │
│ City: [_____________]                   │
│ District: [_____________]               │
│                                         │
│ Verification Method:                    │
│ ◯ Captcha (Select color ball)          │
│ ◯ Email                                 │
│ ◯ Phone                                 │
│                                         │
│      [REGISTER BUTTON]                  │
└─────────────────────────────────────────┘
```

---

## 🚀 How to Register as a Business Owner

### Step 1: Navigate to Registration

```
Go to: http://localhost:5000/auth/register
```

### Step 2: Fill in Basic Information

- **Name:** Your business owner name (e.g., "John Smith")
- **Email:** Your email address
- **Phone:** Your phone number
- **Password:** Strong password (min 8 chars recommended)

### Step 3: Select Role as "Business Owner" ⭐

```
☐ Customer
☑ Business Owner  ← SELECT THIS
```

### Step 4: Enter Address

- **Street/House:** 123 Main Street
- **City:** New York
- **District:** Manhattan

### Step 5: Choose Verification Method

Pick one:

- **Captcha** (recommended - instant)
  - Verify by selecting the correct color ball
- **Email**
  - Receive verification code via email
- **Phone**
  - Receive verification code via SMS

### Step 6: Submit Registration

Click the **REGISTER** button

### Step 7: Login

```
After successful registration:
- Go to: http://localhost:5000/auth/login
- Use your email/phone and password
- Solve CAPTCHA
- You will be redirected to: /owner/dashboard ✅
```

---

## 📱 What Happens After Login

### Business Owner (role = 'business_owner')

```
Login → Redirected to /owner/dashboard
              ↓
    Business Owner Dashboard
    ├─ View Statistics
    ├─ See Pending Bookings
    ├─ Create New Business
    ├─ Manage Bookings
    └─ Accept/Reject Requests
```

### Regular Customer (role = 'customer')

```
Login → Redirected to / (Home)
              ↓
    Customer Home Page
    ├─ Browse Services
    ├─ Search Businesses
    ├─ Book Services
    └─ View My Bookings
```

---

## 🔐 Backend Implementation

### Frontend Form (register_v2.html)

The role field sends to backend:

```html
<input type="radio" name="role" value="customer" checked />
<input type="radio" name="role" value="business_owner" />
```

### Backend Processing (auth.py)

```python
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    role = data.get('role', 'customer')  # Extract role from form
    user, error = register_user(data, role=role)  # Pass to controller
```

### Controller (user_controller.py)

```python
def register_user(data, role='customer'):
    """Register user with specified role"""
    valid_roles = ('customer', 'business_owner')
    if role not in valid_roles:
        return None, f"Invalid role: {role}"

    user = User(
        name=data['name'],
        email=data['email'],
        role=role  # Set role here
    )
```

### User Model (user.py)

```python
class User(me.Document, UserMixin):
    ROLES = ('customer', 'business_owner', 'admin')
    role = me.StringField(
        default='customer',
        choices=ROLES,
        required=True
    )
```

---

## 🎯 Login Redirection by Role

### Login Flow

```python
if user.role == 'business_owner':
    → redirect to /owner/dashboard
elif user.role == 'admin':
    → redirect to /admin/dashboard
else:
    → redirect to / (home)
```

### URL Mapping

| Role           | Login Redirects To | Route              |
| -------------- | ------------------ | ------------------ |
| customer       | Home Page          | `/`                |
| business_owner | Business Dashboard | `/owner/dashboard` |
| admin          | Admin Panel        | `/admin/dashboard` |

---

## 📊 Database Storage

### What Gets Saved

When you register as a Business Owner:

```javascript
// MongoDB - users collection
{
  _id: ObjectId(...),
  user_id: "uuid-string",
  name: "John Smith",
  email: "john@example.com",
  phone: "5551234567",
  password_hash: "hashed_password_here",
  street_house: "123 Main St",
  city: "New York",
  district: "Manhattan",
  role: "business_owner",        // ← This determines access level
  is_verified: false,
  created_at: ISODate(...),
  updated_at: ISODate(...)
}
```

---

## ✨ Business Owner Features (After Login)

Once logged in, Business Owners can access:

### 1. Dashboard (`/owner/dashboard`)

- View all pending bookings
- See booking statistics
- Quick access to manage businesses
- Recent activity

### 2. Create Business (`/owner/business/create`)

- Fill business details
- Upload profile picture
- Upload gallery images (to Cloudinary)
- Publish business

### 3. Manage Bookings (`/owner/bookings`)

- View all booking requests
- Filter by status
- Accept bookings (Command Pattern)
- Reject bookings with reason

### 4. View Business (`/owner/business/<id>`)

- Edit business details
- View services offered
- See gallery
- Update availability

---

## 🔒 Security Features

### Multi-Layer Authorization

1. **Route Protection** (Decorator Pattern)

   ```python
   @owner_business_bp.route('/dashboard')
   @business_owner_required  # Checks role == 'business_owner'
   def dashboard():
       pass
   ```

2. **Command Verification** (Command Pattern)

   ```python
   command = AcceptBookingCommand(booking_id, owner_id)
   result = command.execute()  # Verifies ownership
   ```

3. **Database Constraints**
   - role field validates choices
   - owner_id links business to user

---

## 🧪 Test It Now

### Quick Test Steps

**1. Register as Business Owner**

```
Go to: http://localhost:5000/auth/register
- Name: Test Owner
- Email: test@owner.com
- Phone: 5551234567
- Password: TestPass123!
- Role: ☑ Business Owner
- Verification: Captcha
- Click Register
```

**2. Verify in Database**

```
// MongoDB Console
db.users.findOne({email: "test@owner.com"})
// Should show: role: "business_owner"
```

**3. Login**

```
Go to: http://localhost:5000/auth/login
- Email: test@owner.com
- Password: TestPass123!
- Solve Captcha
```

**4. Expected Result**

```
✅ Login successful
✅ Redirected to /owner/dashboard
✅ See business owner dashboard
```

---

## 🐛 Troubleshooting

### Issue: Don't see "Business Owner" option in registration form

**Solution:**

1. Clear browser cache: `Ctrl+Shift+Delete`
2. Refresh page: `Ctrl+F5`
3. Check file: `frontend/Auth/register_v2.html` line 48-56
4. Restart Flask server

### Issue: Can't find registration page

**Solution:**

```
Make sure server is running:
http://localhost:5000/auth/register

If not found, restart:
python backend/app.py
```

### Issue: Selected "Business Owner" but role not saved

**Solution:**

1. Check form submission includes `name="role"`
2. Verify backend is receiving role: Add print statement
3. Check user_controller.py accepts role parameter
4. Restart Flask server

### Issue: Business Owner option visible but redirects to home after login

**Solution:**

1. Check user.role is 'business_owner' in database
2. Verify auth.py login route has role-based redirection
3. Ensure owner_business_bp is registered in app.py
4. Check decorator imports in owner_business.py

---

## 📞 Support

### Files to Check

- Frontend: `frontend/Auth/register_v2.html`
- Backend: `backend/views/auth.py`
- Controller: `backend/controllers/user_controller.py`
- Model: `backend/models/user.py`
- Routes: `backend/views/owner_business.py`
- App Config: `backend/app.py`

### Next Steps

1. ✅ Register as Business Owner
2. ✅ Login and verify dashboard
3. ✅ Create a business
4. ✅ Test booking management
5. ✅ Review documentation

---

**Status:** ✅ Ready to Use  
**Last Updated:** November 28, 2025  
**Version:** 1.0.0
