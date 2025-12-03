# Strategy Pattern for Registration Verification

## Overview

This document explains how the **Strategy Design Pattern** is implemented for user registration verification in the Service Provider application. The Strategy pattern allows the system to dynamically switch between different verification methods (email, phone, etc.) without changing the core registration logic.

---

## Table of Contents

1. [Why Strategy Pattern?](#why-strategy-pattern)
2. [Implementation Architecture](#implementation-architecture)
3. [How It Works](#how-it-works)
4. [Registration Flow](#registration-flow)
5. [Adding New Verification Methods](#adding-new-verification-methods)
6. [Benefits](#benefits)

---

## Why Strategy Pattern?

### Problems Without Strategy:
```python
# ❌ BAD: Tightly coupled, hard to maintain
def register():
    if verification_method == 'email':
        code = generate_code()
        send_email(email, code)
        session['email'] = email
    elif verification_method == 'phone':
        code = generate_code()
        send_sms(phone, code)
        session['phone'] = phone
    elif verification_method == 'totp':
        # Add new method = modify existing code!
        # Violates Open/Closed Principle
```

**Issues:**
- ❌ Violates **Open/Closed Principle** (modify code to add features)
- ❌ Tightly coupled verification logic
- ❌ Difficult to test individual methods
- ❌ Hard to add new verification methods
- ❌ Code becomes complex with many if-else statements

### Solution with Strategy Pattern:
```python
# ✅ GOOD: Loosely coupled, easy to extend
def register():
    # Create strategy based on user choice
    strategy = VerificationStrategyFactory.create_strategy(verification_method)
    context = VerificationContext(strategy)
    
    # Send verification using chosen strategy
    code = context.send_verification(contact)
    
    # Adding new method = create new strategy class!
    # No modification to existing code
```

**Benefits:**
- ✅ Follows **Open/Closed Principle** (open for extension, closed for modification)
- ✅ Loosely coupled
- ✅ Easy to test each strategy independently
- ✅ Simple to add new verification methods
- ✅ Clean, readable code

---

## Implementation Architecture

### Component Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│            VerificationStrategy (Interface)              │
│  • send_verification(contact, user_data)                │
│  • verify_code(contact, code)                           │
│  • get_contact_field()                                  │
└─────────────────────────────────────────────────────────┘
                        ↑ implements
        ┌───────────────┴───────────────┐
        │                               │
┌───────────────────┐         ┌───────────────────┐
│ EmailVerification │         │ PhoneVerification │
│    Strategy       │         │    Strategy       │
├───────────────────┤         ├───────────────────┤
│ • send via email  │         │ • send via SMS    │
│ • verify email    │         │ • verify phone    │
│ • field: 'email'  │         │ • field: 'phone'  │
└───────────────────┘         └───────────────────┘

┌─────────────────────────────────────────────────────────┐
│         VerificationContext (Uses Strategy)              │
│  • Holds current strategy                               │
│  • Delegates operations to strategy                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│    VerificationStrategyFactory (Creates Strategies)      │
│  • create_strategy('email') → EmailVerificationStrategy │
│  • create_strategy('phone') → PhoneVerificationStrategy │
└─────────────────────────────────────────────────────────┘
```

---

## How It Works

### 1. Strategy Interface

**File:** `backend/patterns/auth_strategy.py`

```python
class VerificationStrategy(ABC):
    """Abstract base class defining the contract for all verification strategies"""
    
    @abstractmethod
    def send_verification(self, contact, user_data=None):
        """Send verification code to the user"""
        pass
    
    @abstractmethod
    def verify_code(self, contact, code):
        """Verify the code entered by user"""
        pass
    
    @abstractmethod
    def get_contact_field(self):
        """Return the field name (email, phone, etc.)"""
        pass
```

**Purpose:** Defines the contract that all verification strategies must follow

---

### 2. Concrete Strategies

#### Email Verification Strategy

```python
class EmailVerificationStrategy(VerificationStrategy):
    """Strategy for email-based verification"""
    
    def send_verification(self, contact, user_data=None):
        """Send verification code via email"""
        code = generate_verification_code()  # Returns "12345" in dev
        send_verification_email(contact, code)  # Prints to console
        
        # Store in session for later verification
        session['reg_email'] = contact
        session['reg_code'] = code
        session['reg_method'] = 'email'
        
        return code
    
    def verify_code(self, contact, code):
        """Verify email verification code"""
        stored_code = session.get('reg_code')
        stored_email = session.get('reg_email')
        stored_method = session.get('reg_method')
        
        return (stored_method == 'email' and 
                stored_email == contact and 
                stored_code == code)
    
    def get_contact_field(self):
        return 'email'
```

#### Phone Verification Strategy

```python
class PhoneVerificationStrategy(VerificationStrategy):
    """Strategy for phone-based verification"""
    
    def send_verification(self, contact, user_data=None):
        """Send verification code via SMS"""
        code = generate_verification_code()  # Returns "12345" in dev
        send_verification_sms(contact, code)  # Prints to console
        
        # Store in session for later verification
        session['reg_phone'] = contact
        session['reg_code'] = code
        session['reg_method'] = 'phone'
        
        return code
    
    def verify_code(self, contact, code):
        """Verify phone verification code"""
        stored_code = session.get('reg_code')
        stored_phone = session.get('reg_phone')
        stored_method = session.get('reg_method')
        
        return (stored_method == 'phone' and 
                stored_phone == contact and 
                stored_code == code)
    
    def get_contact_field(self):
        return 'phone'
```

---

### 3. Context Class

```python
class VerificationContext:
    """Context class that uses a verification strategy"""
    
    def __init__(self, strategy: VerificationStrategy):
        self._strategy = strategy
    
    @property
    def strategy(self):
        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy: VerificationStrategy):
        """Allow runtime strategy switching"""
        self._strategy = strategy
    
    def send_verification(self, contact, user_data=None):
        """Delegate to current strategy"""
        return self._strategy.send_verification(contact, user_data)
    
    def verify_code(self, contact, code):
        """Delegate to current strategy"""
        return self._strategy.verify_code(contact, code)
    
    def get_contact_field(self):
        """Delegate to current strategy"""
        return self._strategy.get_contact_field()
```

**Purpose:** Manages the current strategy and delegates operations to it

---

### 4. Factory for Strategy Creation

```python
class VerificationStrategyFactory:
    """Factory to create verification strategies"""
    
    @staticmethod
    def create_strategy(method: str) -> VerificationStrategy:
        """
        Create and return appropriate verification strategy
        
        Args:
            method: 'email', 'phone', or other verification method
            
        Returns:
            VerificationStrategy instance
        """
        strategies = {
            'email': EmailVerificationStrategy,
            'phone': PhoneVerificationStrategy,
        }
        
        strategy_class = strategies.get(method.lower())
        if not strategy_class:
            # Default to email if unknown method
            strategy_class = EmailVerificationStrategy
        
        return strategy_class()
```

**Purpose:** Encapsulates strategy creation logic

---

## Registration Flow

### Complete User Registration Journey

#### Step 1: User Submits Registration Form

**File:** `frontend/Auth/register_v2.html`

```html
<form method="POST">
    <input name="name" required>
    <input name="email" required>
    <input name="phone" required>
    <input name="password" required>
    
    <!-- User selects verification method -->
    <select name="verification_method">
        <option value="email">Email Verification</option>
        <option value="phone">Phone Verification</option>
    </select>
    
    <select name="role">
        <option value="customer">Customer</option>
        <option value="business_owner">Business Owner</option>
    </select>
    
    <button type="submit">Register</button>
</form>
```

**User Action:** Fills form and selects verification method (email or phone)

---

#### Step 2: Server Receives Registration Request

**File:** `backend/views/auth.py`

```python
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form.to_dict()
        verification_method = data.get('verification_method', 'email')
        role = data.get('role', 'customer')
```

**Flow:**
1. Extract form data
2. Get verification method (email/phone)
3. Get user role (customer/business_owner)

---

#### Step 3: Create User Account

```python
        # Register user with role
        user, error = register_user(data, role=role)
        if error:
            auth_notifier.notify(error, 'danger')
            return render_template('register_v2.html', role=role)
```

**File:** `backend/controllers/user_controller.py`

```python
def register_user(data, role='customer'):
    """Register a new user"""
    
    # Check if user already exists
    if User.objects(email=data.get('email')).first():
        return None, "Email already registered"
    
    # Create new user
    user = User(
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        role=role,
        is_verified=False  # Not verified yet
    )
    user.set_password(data.get('password'))
    user.save()  # Uses SingletonDB connection
    
    return user, None
```

**Result:** User account created but `is_verified=False`

---

#### Step 4: Strategy Pattern - Send Verification

```python
        # ===== Strategy Pattern Implementation =====
        from patterns.auth_strategy import VerificationStrategyFactory, VerificationContext
        
        # 1. Create appropriate strategy based on verification method
        strategy = VerificationStrategyFactory.create_strategy(verification_method)
        
        # 2. Create context with the strategy
        verification_context = VerificationContext(strategy)
        
        # 3. Get contact field name from strategy
        contact_field = verification_context.get_contact_field()
        contact = data.get(contact_field)
        
        # 4. Validate contact exists
        if not contact:
            auth_notifier.notify(f'No {contact_field} provided for verification.', 'danger')
            return render_template('register_v2.html', role=role)
        
        # 5. Send verification using strategy
        try:
            code = verification_context.send_verification(contact, user_data=data)
            auth_notifier.notify(f"Registration successful! Verification code sent to your {contact_field}: {code}", "success")
            return redirect(url_for('auth.verify_register'))
        except Exception as e:
            auth_notifier.notify(f'Failed to send verification: {str(e)}', 'danger')
            return render_template('register_v2.html', role=role)
```

**Behind the Scenes:**

**If User Selected Email:**
```
verification_method = 'email'
→ Factory creates EmailVerificationStrategy
→ Context delegates to EmailVerificationStrategy
→ contact_field = 'email'
→ contact = 'user@example.com'
→ EmailVerificationStrategy.send_verification('user@example.com')
    → generate_verification_code() returns "12345"
    → send_verification_email('user@example.com', '12345')
    → Prints: "Sending email to user@example.com with code: 12345"
    → Store in session: reg_email, reg_code, reg_method='email'
→ Redirect to verification page
```

**If User Selected Phone:**
```
verification_method = 'phone'
→ Factory creates PhoneVerificationStrategy
→ Context delegates to PhoneVerificationStrategy
→ contact_field = 'phone'
→ contact = '+8801234567890'
→ PhoneVerificationStrategy.send_verification('+8801234567890')
    → generate_verification_code() returns "12345"
    → send_verification_sms('+8801234567890', '12345')
    → Prints: "Sending SMS to +8801234567890 with code: 12345"
    → Store in session: reg_phone, reg_code, reg_method='phone'
→ Redirect to verification page
```

---

#### Step 5: User Enters Verification Code

**File:** `frontend/Auth/verify_register.html`

```html
<form method="POST">
    <p>Enter the verification code sent to your {{ method }}</p>
    <input name="code" required>
    <button type="submit">Verify</button>
</form>
```

**User Action:** Enters the code received via email/SMS (e.g., "12345")

---

#### Step 6: Strategy Pattern - Verify Code

**File:** `backend/views/auth.py`

```python
@auth_bp.route('/verify_register', methods=['GET', 'POST'])
def verify_register():
    method = session.get('reg_method')
    contact = session.get('reg_email') or session.get('reg_phone')
    
    if not contact or not method:
        auth_notifier.notify("No verification pending.", "warning")
        return redirect(url_for('auth.register'))
    
    if request.method == 'POST':
        code_entered = request.form.get('code')
        
        # ===== Strategy Pattern Implementation =====
        from patterns.auth_strategy import VerificationStrategyFactory, VerificationContext
        
        # 1. Create appropriate strategy based on stored method
        strategy = VerificationStrategyFactory.create_strategy(method)
        
        # 2. Create context with the strategy
        verification_context = VerificationContext(strategy)
        
        # 3. Verify code using strategy
        is_valid = verification_context.verify_code(contact, code_entered)
        
        if is_valid:
            # Mark user as verified
            from models.user import User
            contact_field = verification_context.get_contact_field()
            
            # Find user by appropriate field
            if contact_field == 'email':
                user = User.objects(email=contact).first()
            elif contact_field == 'phone':
                user = User.objects(phone=contact).first()
            
            if user:
                user.is_verified = True
                user.save()  # Uses SingletonDB connection
            
            # Clear session
            session.pop('reg_email', None)
            session.pop('reg_phone', None)
            session.pop('reg_code', None)
            session.pop('reg_method', None)
            
            auth_notifier.notify('Verification successful! You can now login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            auth_notifier.notify('Verification code incorrect. Try again.', 'danger')
    
    return render_template('verify_register.html', contact=contact, method=method)
```

**Behind the Scenes:**

**Email Verification:**
```
method = 'email' (from session)
code_entered = '12345' (from form)
→ Factory creates EmailVerificationStrategy
→ Context delegates to EmailVerificationStrategy
→ EmailVerificationStrategy.verify_code('user@example.com', '12345')
    → Compares with session['reg_code']
    → Returns True if match
→ Find user by email
→ Set user.is_verified = True
→ Save user
→ Clear session
→ Redirect to login
```

**Phone Verification:**
```
method = 'phone' (from session)
code_entered = '12345' (from form)
→ Factory creates PhoneVerificationStrategy
→ Context delegates to PhoneVerificationStrategy
→ PhoneVerificationStrategy.verify_code('+8801234567890', '12345')
    → Compares with session['reg_code']
    → Returns True if match
→ Find user by phone
→ Set user.is_verified = True
→ Save user
→ Clear session
→ Redirect to login
```

---

## Adding New Verification Methods

### Example: Adding TOTP (Time-based One-Time Password)

#### Step 1: Create New Strategy Class

**File:** `backend/patterns/auth_strategy.py`

```python
class TOTPVerificationStrategy(VerificationStrategy):
    """Strategy for TOTP-based verification (Google Authenticator, etc.)"""
    
    def send_verification(self, contact, user_data=None):
        """Generate TOTP secret and QR code"""
        import pyotp
        
        # Generate secret key
        secret = pyotp.random_base32()
        
        # Generate QR code URL
        totp = pyotp.TOTP(secret)
        qr_url = totp.provisioning_uri(
            name=contact,
            issuer_name='Service Provider App'
        )
        
        # Store in session
        session['reg_totp_secret'] = secret
        session['reg_user_id'] = user_data.get('user_id')
        session['reg_method'] = 'totp'
        
        return qr_url  # Return QR code URL for user to scan
    
    def verify_code(self, contact, code):
        """Verify TOTP code"""
        import pyotp
        
        stored_secret = session.get('reg_totp_secret')
        stored_method = session.get('reg_method')
        
        if stored_method != 'totp' or not stored_secret:
            return False
        
        totp = pyotp.TOTP(stored_secret)
        return totp.verify(code)  # Verify time-based code
    
    def get_contact_field(self):
        return 'user_id'
```

#### Step 2: Register in Factory

```python
class VerificationStrategyFactory:
    @staticmethod
    def create_strategy(method: str) -> VerificationStrategy:
        strategies = {
            'email': EmailVerificationStrategy,
            'phone': PhoneVerificationStrategy,
            'totp': TOTPVerificationStrategy,  # ✅ Add new strategy
        }
        
        strategy_class = strategies.get(method.lower())
        if not strategy_class:
            strategy_class = EmailVerificationStrategy
        
        return strategy_class()
```

#### Step 3: Update Registration Form

```html
<select name="verification_method">
    <option value="email">Email Verification</option>
    <option value="phone">Phone Verification</option>
    <option value="totp">Authenticator App (TOTP)</option> <!-- ✅ Add option -->
</select>
```

#### Step 4: Done! No Changes to Existing Code

```python
# Existing registration code still works!
strategy = VerificationStrategyFactory.create_strategy(verification_method)
verification_context = VerificationContext(strategy)
code = verification_context.send_verification(contact, user_data=data)
```

**Result:** New verification method added without modifying existing registration logic!

---

### Example: Adding Biometric Verification

```python
class BiometricVerificationStrategy(VerificationStrategy):
    """Strategy for biometric verification (fingerprint, face ID)"""
    
    def send_verification(self, contact, user_data=None):
        """Generate biometric challenge"""
        challenge_token = generate_random_token()
        
        session['reg_biometric_token'] = challenge_token
        session['reg_user_id'] = user_data.get('user_id')
        session['reg_method'] = 'biometric'
        
        return challenge_token  # Send to mobile app
    
    def verify_code(self, contact, code):
        """Verify biometric signature"""
        stored_token = session.get('reg_biometric_token')
        # Verify biometric signature from mobile device
        return verify_biometric_signature(stored_token, code)
    
    def get_contact_field(self):
        return 'device_id'
```

**Register:**
```python
strategies = {
    'email': EmailVerificationStrategy,
    'phone': PhoneVerificationStrategy,
    'totp': TOTPVerificationStrategy,
    'biometric': BiometricVerificationStrategy,  # ✅ Add
}
```

**Done!** No changes to registration flow needed.

---

## Benefits

### 1. **Open/Closed Principle**

```
✅ Open for Extension:
   - Add new verification methods by creating new strategy classes
   - No modification of existing code required

✅ Closed for Modification:
   - Existing strategies remain unchanged
   - Registration flow unchanged
   - Other parts of the system unaffected
```

### 2. **Single Responsibility**

Each strategy has **one responsibility**:
- `EmailVerificationStrategy` → Handle email verification only
- `PhoneVerificationStrategy` → Handle phone verification only
- `TOTPVerificationStrategy` → Handle TOTP verification only

### 3. **Flexibility**

```python
# Runtime strategy switching (if needed)
context = VerificationContext(EmailVerificationStrategy())

# User changes mind during registration?
context.strategy = PhoneVerificationStrategy()

# Works seamlessly!
code = context.send_verification(new_contact)
```

### 4. **Testability**

```python
# Test email strategy independently
def test_email_verification():
    strategy = EmailVerificationStrategy()
    code = strategy.send_verification('test@example.com')
    assert strategy.verify_code('test@example.com', code) == True

# Test phone strategy independently
def test_phone_verification():
    strategy = PhoneVerificationStrategy()
    code = strategy.send_verification('+1234567890')
    assert strategy.verify_code('+1234567890', code) == True

# No dependencies, clean tests!
```

### 5. **Maintainability**

```
Change email verification logic?
→ Modify EmailVerificationStrategy only
→ Phone verification unaffected
→ Registration flow unaffected
→ Other parts of app unaffected

Change phone verification provider?
→ Modify PhoneVerificationStrategy only
→ Email verification unaffected
→ Everything else unaffected
```

### 6. **Code Reusability**

```python
# Reuse strategies in other contexts

# Password reset verification
def reset_password():
    strategy = VerificationStrategyFactory.create_strategy('email')
    context = VerificationContext(strategy)
    code = context.send_verification(user.email)

# Two-factor authentication
def enable_2fa():
    strategy = VerificationStrategyFactory.create_strategy('totp')
    context = VerificationContext(strategy)
    qr_code = context.send_verification(user.email)
```

---

## Flow Comparison

### Without Strategy Pattern

```
User submits form
↓
if verification_method == 'email':
    generate code
    send email
    store email in session
elif verification_method == 'phone':
    generate code
    send SMS
    store phone in session
elif verification_method == 'totp':  ← Need to modify existing code
    generate secret
    create QR code
    store secret in session
↓
Redirect to verify page
↓
User enters code
↓
if verification_method == 'email':
    check email code
elif verification_method == 'phone':
    check phone code
elif verification_method == 'totp':  ← Need to modify existing code again
    check TOTP code
↓
Mark user as verified
```

**Issues:** Modify code twice (send + verify) for each new method

---

### With Strategy Pattern

```
User submits form
↓
Create strategy (Factory)  ← One line
↓
Send verification (Strategy)  ← One line
↓
Redirect to verify page
↓
User enters code
↓
Verify code (Strategy)  ← One line
↓
Mark user as verified
```

**Benefits:** Add new method = create new strategy class, update factory dict. Done!

---

## Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Registration Request                     │
│              (Form data + verification method)                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Create User Account (Controller)                │
│            User.save() → SingletonDB connection                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            VerificationStrategyFactory.create_strategy()         │
│                  (Based on verification_method)                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────┴─────────┐
                    │                   │
        ┌───────────────────┐  ┌───────────────────┐
        │ EmailVerification │  │ PhoneVerification │
        │    Strategy       │  │    Strategy       │
        └───────────────────┘  └───────────────────┘
                    │                   │
                    └─────────┬─────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    VerificationContext                           │
│           Delegates to selected strategy                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              Strategy.send_verification(contact)                 │
│    • EmailStrategy → send email with code                        │
│    • PhoneStrategy → send SMS with code                          │
│    • Store in session                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Redirect to Verification Page                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    User Enters Code                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          Strategy.verify_code(contact, code_entered)             │
│    • EmailStrategy → verify email code                           │
│    • PhoneStrategy → verify phone code                           │
│    • Compare with session                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              User.is_verified = True (if valid)                  │
│              User.save() → SingletonDB connection                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Redirect to Login Page                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Takeaways

1. **Flexibility**: Switch verification methods without changing core logic
2. **Extensibility**: Add new methods by creating new strategy classes
3. **Maintainability**: Each strategy is independent and easy to modify
4. **Testability**: Test each strategy in isolation
5. **Clean Code**: No complex if-else chains
6. **Open/Closed Principle**: Open for extension, closed for modification
7. **Reusability**: Strategies can be used in other contexts (password reset, 2FA, etc.)

---

## Real-World Usage Examples

### Email Verification Flow
```
User: karim@example.com
Method: Email
→ EmailVerificationStrategy
→ Sends email to karim@example.com
→ Code: 12345
→ User enters 12345
→ EmailVerificationStrategy.verify_code() returns True
→ User verified ✓
```

### Phone Verification Flow
```
User: +8801712345678
Method: Phone
→ PhoneVerificationStrategy
→ Sends SMS to +8801712345678
→ Code: 12345
→ User enters 12345
→ PhoneVerificationStrategy.verify_code() returns True
→ User verified ✓
```

### Future: TOTP Flow (After Implementation)
```
User: admin@example.com
Method: TOTP
→ TOTPVerificationStrategy
→ Generates QR code
→ User scans with Google Authenticator
→ User enters 6-digit TOTP code
→ TOTPVerificationStrategy.verify_code() returns True
→ User verified ✓
```

---

## Conclusion

The Strategy pattern makes registration verification:
- **Flexible**: Easy to switch between verification methods
- **Extensible**: Add new methods without modifying existing code
- **Maintainable**: Each strategy is self-contained
- **Testable**: Independent testing of each strategy
- **Professional**: Follows SOLID principles

**Every time a user registers, the Strategy pattern dynamically selects and executes the appropriate verification method without any code changes!** 🎯
