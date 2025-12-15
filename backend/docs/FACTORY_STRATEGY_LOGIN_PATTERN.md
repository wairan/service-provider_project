# Factory & Strategy Patterns for Login Authentication

## Overview

This document explains how **Factory Pattern** and **Strategy Pattern** work together for login authentication in the Service Provider application. The Factory pattern creates different types of captchas dynamically, while the Strategy pattern handles captcha verification, making the login system flexible and extensible.

---

## Table of Contents

1. [Why These Patterns?](#why-these-patterns)
2. [Factory Pattern - Captcha Generation](#factory-pattern---captcha-generation)
3. [Strategy Pattern - Captcha Verification](#strategy-pattern---captcha-verification)
4. [Login Flow](#login-flow)
5. [Adding New Captcha Types](#adding-new-captcha-types)
6. [Benefits](#benefits)

---

## Why These Patterns?

### Problems Without Design Patterns:

```python
# ❌ BAD: Hardcoded, inflexible
def login():
    # Hardcoded captcha generation
    colors = ['red', 'blue', 'green']
    correct = random.choice(colors)
    captcha = {'challenge': f'Select {correct}', 'answer': correct}
    
    # Hardcoded verification
    if request.form.get('captcha') != session.get('answer'):
        return "Wrong captcha"
    
    # Can't easily add math captcha, image captcha, etc.
    # Violates Open/Closed Principle
```

**Issues:**
- ❌ Can't easily add new captcha types
- ❌ Captcha generation and verification tightly coupled
- ❌ Difficult to test independently
- ❌ Violates SOLID principles

### Solution with Design Patterns:

```python
# ✅ GOOD: Flexible, extensible
def login():
    # Factory Pattern: Create captcha dynamically
    captcha = CaptchaFactory.create_captcha(type=captcha_type)
    
    # Strategy Pattern: Verify captcha
    auth_context = LoginAuthContext(CaptchaAuthStrategy())
    is_valid = auth_context.authenticate(user_input, session)
    
    # Easy to add: image captcha, slider captcha, audio captcha
    # No modification to existing code!
```

**Benefits:**
- ✅ Add new captcha types easily
- ✅ Loosely coupled design
- ✅ Easy to test each component
- ✅ Follows SOLID principles

---

## Factory Pattern - Captcha Generation

### Design Pattern: Factory

**Purpose:** Create different types of captcha objects without exposing creation logic to the client.

### Component Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│              Captcha (Product Interface)                 │
│  • generate_challenge()                                 │
│  • get_answer()                                         │
│  • get_type()                                           │
└─────────────────────────────────────────────────────────┘
                        ↑ implements
        ┌───────────────┴───────────────┐
        │                               │
┌───────────────────┐         ┌───────────────────┐
│  ColorBallCaptcha │         │    MathCaptcha    │
│   (Concrete)      │         │    (Concrete)     │
├───────────────────┤         ├───────────────────┤
│ • Color selection │         │ • Math problems   │
│ • Random color    │         │ • +, -, * ops     │
│ • Visual options  │         │ • Number range    │
└───────────────────┘         └───────────────────┘

┌─────────────────────────────────────────────────────────┐
│            CaptchaFactory (Creator)                      │
│  • create_captcha(type) → Captcha instance              │
│  • get_available_types()                                │
│  • register_captcha_type(name, class)                   │
└─────────────────────────────────────────────────────────┘
```

---

### 1. Product Interface

**File:** `backend/patterns/captcha_factory.py`

```python
class Captcha(ABC):
    """Abstract base class for all captcha types"""
    
    @abstractmethod
    def generate_challenge(self):
        """Generate and return captcha challenge data"""
        pass
    
    @abstractmethod
    def get_answer(self):
        """Get the correct answer for this captcha"""
        pass
    
    @abstractmethod
    def get_type(self):
        """Get the captcha type identifier"""
        pass
```

**Purpose:** Defines the contract that all captcha products must follow

---

### 2. Concrete Products

#### Color Ball Captcha

```python
class ColorBallCaptcha(Captcha):
    """Color ball selection captcha"""
    
    def __init__(self):
        self.colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
        self.correct_color = random.choice(self.colors)
        self.options = random.sample(self.colors, 3)  # Show 3 random colors
        
        # Ensure correct color is in options
        if self.correct_color not in self.options:
            self.options[0] = self.correct_color
        random.shuffle(self.options)
    
    def generate_challenge(self):
        """Generate color ball challenge"""
        return {
            'type': self.get_type(),
            'challenge': f'Select the {self.correct_color} ball',
            'answer': self.correct_color,
            'options': self.options
        }
    
    def get_answer(self):
        return self.correct_color
    
    def get_type(self):
        return 'color_ball'
```

**Features:**
- Random color selection from 6 colors
- Shows 3 color options to user
- Ensures correct answer is always in options
- Visual, easy for humans, hard for bots

---

#### Math Captcha

```python
class MathCaptcha(Captcha):
    """Simple math problem captcha"""
    
    def __init__(self):
        self.num1 = random.randint(1, 10)
        self.num2 = random.randint(1, 10)
        self.operation = random.choice(['+', '-', '*'])
        self.correct_answer = self._calculate_answer()
    
    def _calculate_answer(self):
        """Calculate the correct answer based on operation"""
        if self.operation == '+':
            return str(self.num1 + self.num2)
        elif self.operation == '-':
            return str(self.num1 - self.num2)
        elif self.operation == '*':
            return str(self.num1 * self.num2)
        return '0'
    
    def generate_challenge(self):
        """Generate math challenge"""
        return {
            'type': self.get_type(),
            'challenge': f'What is {self.num1} {self.operation} {self.num2}?',
            'answer': self.correct_answer,
            'options': None  # No pre-defined options for math
        }
    
    def get_answer(self):
        return self.correct_answer
    
    def get_type(self):
        return 'math'
```

**Features:**
- Random numbers (1-10)
- Random operations (+, -, *)
- Text-based input
- Good for accessibility

---

### 3. Factory (Creator)

```python
class CaptchaFactory:
    """Factory class for creating different types of captchas"""
    
    # Registry of available captcha types
    _captcha_types = {
        'color_ball': ColorBallCaptcha,
        'math': MathCaptcha,
    }
    
    @staticmethod
    def create_captcha(type='color_ball'):
        """
        Factory method to create captcha instances
        
        Args:
            type: Type of captcha to create ('color_ball', 'math')
            
        Returns:
            dict: Captcha challenge data
        """
        captcha_class = CaptchaFactory._captcha_types.get(type.lower())
        
        if not captcha_class:
            # Default to color_ball if unknown type
            captcha_class = ColorBallCaptcha
        
        # Create captcha instance and generate challenge
        captcha_instance = captcha_class()
        return captcha_instance.generate_challenge()
    
    @staticmethod
    def get_available_types():
        """Get list of available captcha types"""
        return list(CaptchaFactory._captcha_types.keys())
    
    @staticmethod
    def register_captcha_type(type_name: str, captcha_class: type):
        """
        Register a new captcha type (for extensibility)
        
        Args:
            type_name: Identifier for the captcha type
            captcha_class: Class that implements Captcha interface
        """
        if not issubclass(captcha_class, Captcha):
            raise TypeError(f"{captcha_class} must inherit from Captcha")
        CaptchaFactory._captcha_types[type_name.lower()] = captcha_class
```

**Key Features:**
- **Registry Pattern**: Stores available captcha types in dictionary
- **Factory Method**: `create_captcha()` returns captcha data
- **Extensibility**: `register_captcha_type()` allows adding new types at runtime
- **Default Fallback**: Uses color_ball if unknown type requested

---

## Strategy Pattern - Captcha Verification

### Design Pattern: Strategy

**Purpose:** Define a family of authentication algorithms, encapsulate each one, and make them interchangeable.

### Component Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│          LoginAuthStrategy (Strategy Interface)          │
│  • verify(user_input, session_data)                     │
└─────────────────────────────────────────────────────────┘
                        ↑ implements
                        │
┌───────────────────────────────────────────────────────────┐
│           CaptchaAuthStrategy (Concrete Strategy)         │
│  • Verifies captcha answers                              │
│  • Compares user input with session answer               │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│          LoginAuthContext (Context/Manager)               │
│  • Holds current strategy                                │
│  • Delegates authentication to strategy                  │
└───────────────────────────────────────────────────────────┘
```

---

### 1. Strategy Interface

**File:** `backend/patterns/auth_strategy.py`

```python
class LoginAuthStrategy(ABC):
    """Abstract strategy for login authentication methods"""
    
    @abstractmethod
    def verify(self, user_input, session_data):
        """Verify the authentication challenge"""
        pass
```

**Purpose:** Defines the contract for all login authentication strategies

---

### 2. Concrete Strategy

```python
class CaptchaAuthStrategy(LoginAuthStrategy):
    """Strategy for captcha-based login authentication"""
    
    def verify(self, user_input, session_data):
        """
        Verify captcha answer
        
        Args:
            user_input: User's captcha answer
            session_data: Session containing correct answer
            
        Returns:
            bool: True if captcha is correct
        """
        expected_answer = session_data.get('captcha_answer')
        return user_input == expected_answer
```

**Features:**
- Simple comparison logic
- Works with any captcha type (color_ball, math, etc.)
- Session-based verification
- Returns boolean result

---

### 3. Context Class

```python
class LoginAuthContext:
    """Context class for managing login authentication strategies"""
    
    def __init__(self, strategy: LoginAuthStrategy = None):
        self._strategy = strategy or CaptchaAuthStrategy()
    
    @property
    def strategy(self):
        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy: LoginAuthStrategy):
        self._strategy = strategy
    
    def authenticate(self, user_input, session_data):
        """Delegate authentication to strategy"""
        return self._strategy.verify(user_input, session_data)
```

**Features:**
- Manages current authentication strategy
- Delegates verification to strategy
- Allows runtime strategy switching
- Default to CaptchaAuthStrategy

---

## Login Flow

### Complete Login Journey with Both Patterns

#### Step 1: User Visits Login Page (GET Request)

**File:** `frontend/Auth/login.html`

```html
<!-- User sees login form -->
<form method="POST">
    <input name="identifier" placeholder="Email or Phone" required>
    <input name="password" type="password" required>
    
    <!-- Captcha Type Selector (user can switch types) -->
    <div>
        <a href="?type=color_ball">Color Ball</a> |
        <a href="?type=math">Math Problem</a>
    </div>
    
    <!-- Captcha Challenge Display -->
    <div id="captcha-challenge">
        {{ captcha.challenge }}
    </div>
    
    <input name="captcha_answer" placeholder="Captcha Answer" required>
    
    <select name="login_as">
        <option value="customer">Login as Customer</option>
        <option value="business_owner">Login as Business Owner</option>
    </select>
    
    <button type="submit">Login</button>
</form>
```

---

#### Step 2: Server Generates Captcha (Factory Pattern)

**File:** `backend/views/auth.py`

```python
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # ===== Factory Pattern for Captcha Generation =====
        
        # 1. Get requested captcha type (default: color_ball)
        captcha_type = request.args.get('type', 'color_ball')
        
        # 2. Use Factory to create appropriate captcha
        captcha = CaptchaFactory.create_captcha(type=captcha_type)
        
        # 3. Store answer in session for later verification
        session['captcha_answer'] = captcha['answer']
        
        # 4. Get available captcha types for template
        available_types = CaptchaFactory.get_available_types()
        
        # 5. Render login page with captcha
        return render_template('login.html', 
                             captcha=captcha, 
                             captcha_type=captcha_type,
                             available_captcha_types=available_types)
```

**Behind the Scenes:**

**If User Requests Color Ball Captcha:**
```
captcha_type = 'color_ball'
→ CaptchaFactory.create_captcha('color_ball')
    → Looks up registry: _captcha_types['color_ball'] = ColorBallCaptcha
    → Creates instance: ColorBallCaptcha()
        → __init__: colors=['red','blue','green','yellow','purple','orange']
        → __init__: correct_color = 'blue' (random)
        → __init__: options = ['blue', 'red', 'green'] (random sample)
    → Calls: captcha_instance.generate_challenge()
        → Returns: {
            'type': 'color_ball',
            'challenge': 'Select the blue ball',
            'answer': 'blue',
            'options': ['blue', 'red', 'green']
          }
→ session['captcha_answer'] = 'blue'
→ Render login page with color ball challenge
```

**If User Requests Math Captcha:**
```
captcha_type = 'math'
→ CaptchaFactory.create_captcha('math')
    → Looks up registry: _captcha_types['math'] = MathCaptcha
    → Creates instance: MathCaptcha()
        → __init__: num1 = 7 (random 1-10)
        → __init__: num2 = 3 (random 1-10)
        → __init__: operation = '+' (random +, -, *)
        → __init__: correct_answer = '10' (7 + 3)
    → Calls: captcha_instance.generate_challenge()
        → Returns: {
            'type': 'math',
            'challenge': 'What is 7 + 3?',
            'answer': '10',
            'options': None
          }
→ session['captcha_answer'] = '10'
→ Render login page with math challenge
```

---

#### Step 3: User Submits Login Form (POST Request)

```html
<!-- User fills form and submits -->
<form method="POST">
    identifier: karim@example.com
    password: SecurePass123
    captcha_answer: blue  (or 10 for math)
    login_as: customer
</form>
```

---

#### Step 4: Server Verifies Captcha (Strategy Pattern)

**File:** `backend/views/auth.py`

```python
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 1. Extract form data
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        login_as = request.form.get('login_as', 'customer')
        user_captcha = request.form.get('captcha_answer')
        
        # ===== Strategy Pattern for Captcha Verification =====
        from patterns.auth_strategy import LoginAuthContext, CaptchaAuthStrategy
        
        # 2. Create authentication context with captcha strategy
        auth_context = LoginAuthContext(CaptchaAuthStrategy())
        
        # 3. Verify captcha using strategy
        is_captcha_valid = auth_context.authenticate(user_captcha, session)
        
        # 4. Check captcha result
        if not is_captcha_valid:
            auth_notifier.notify("Captcha incorrect. Try again.", "danger")
            return redirect(url_for('auth.login'))
        
        # 5. Captcha valid - proceed with user authentication
        user, error = controller_login(identifier, password)
        
        if not user:
            auth_notifier.notify(error or "Invalid credentials.", "danger")
            return redirect(url_for('auth.login'))
        
        # 6. Validate user role matches login intent
        user_role = getattr(user, 'role', 'customer')
        
        if login_as == 'business_owner' and user_role != 'business_owner':
            auth_notifier.notify(
                f"Login failed: Your account is '{user_role}', not 'business_owner'.",
                'danger'
            )
            return redirect(url_for('auth.login'))
        
        if login_as == 'customer' and user_role not in ['customer', None]:
            auth_notifier.notify(
                f"Login failed: Your account is '{user_role}', not 'customer'.",
                'danger'
            )
            return redirect(url_for('auth.login'))
        
        # 7. All checks passed - login user
        login_user(user, remember=False)
        auth_notifier.notify(f"Login successful! Welcome, {user.name}", "success")
        
        # 8. Role-based redirection
        if user_role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user_role == 'business_owner':
            return redirect(url_for('owner_business.dashboard'))
        else:
            return redirect(url_for('home.index'))
```

**Behind the Scenes:**

**Captcha Verification with Strategy:**
```
user_captcha = 'blue' (from form)
session = {'captcha_answer': 'blue'}

→ Create LoginAuthContext with CaptchaAuthStrategy
→ Call: auth_context.authenticate('blue', session)
    → Delegates to CaptchaAuthStrategy.verify('blue', session)
        → expected_answer = session.get('captcha_answer')  # 'blue'
        → return 'blue' == 'blue'  # True
    → Returns: True
→ is_captcha_valid = True
→ Proceed with user authentication
```

**If Captcha is Wrong:**
```
user_captcha = 'red' (from form)
session = {'captcha_answer': 'blue'}

→ Call: auth_context.authenticate('red', session)
    → CaptchaAuthStrategy.verify('red', session)
        → return 'red' == 'blue'  # False
    → Returns: False
→ is_captcha_valid = False
→ Show error: "Captcha incorrect. Try again."
→ Redirect back to login page
→ User never sees password validation
```

---

#### Step 5: User Authentication & Role Validation

**File:** `backend/controllers/user_controller.py`

```python
def login_user(identifier, password):
    """Authenticate user by email or phone"""
    
    # Try to find user by email
    user = User.objects(email=identifier).first()
    
    # If not found, try phone
    if not user:
        user = User.objects(phone=identifier).first()
    
    # Verify password
    if user and user.check_password(password):
        # Check if user is verified
        if not user.is_verified:
            return None, "Please verify your account first."
        return user, None
    
    return None, "Invalid credentials."
```

---

#### Step 6: Successful Login & Redirection

```
User: karim@example.com (customer)
Password: Correct
Captcha: Correct
Login As: Customer

→ Captcha verification: ✓ Pass
→ User authentication: ✓ Pass
→ Role validation: ✓ Pass (customer = customer)
→ Flask-Login: login_user(karim)
→ Redirect to: home.index (customer home page)
```

---

## Adding New Captcha Types

### Example 1: Image Selection Captcha

#### Step 1: Create Captcha Class

**File:** `backend/patterns/captcha_factory.py`

```python
class ImageCaptcha(Captcha):
    """Select images containing specific objects (like reCAPTCHA)"""
    
    def __init__(self):
        self.objects = ['car', 'bicycle', 'traffic light', 'crosswalk']
        self.target_object = random.choice(self.objects)
        # In production, you'd have actual image URLs
        self.images = [
            f'/static/captcha/img_{i}.jpg' for i in range(9)
        ]
        # Randomly select which images contain the target object
        self.correct_indices = random.sample(range(9), k=random.randint(2, 4))
    
    def generate_challenge(self):
        return {
            'type': self.get_type(),
            'challenge': f'Select all images containing a {self.target_object}',
            'answer': ','.join(map(str, sorted(self.correct_indices))),
            'options': self.images,
            'correct_indices': self.correct_indices
        }
    
    def get_answer(self):
        return ','.join(map(str, sorted(self.correct_indices)))
    
    def get_type(self):
        return 'image'
```

#### Step 2: Register in Factory

```python
class CaptchaFactory:
    _captcha_types = {
        'color_ball': ColorBallCaptcha,
        'math': MathCaptcha,
        'image': ImageCaptcha,  # ✅ Add new type
    }
```

#### Step 3: Update Login Template

```html
<div>
    <a href="?type=color_ball">Color Ball</a> |
    <a href="?type=math">Math Problem</a> |
    <a href="?type=image">Image Selection</a>  <!-- ✅ Add link -->
</div>
```

#### Step 4: Done! No Changes to Login Logic

```python
# Existing code still works!
captcha = CaptchaFactory.create_captcha(type=captcha_type)
auth_context = LoginAuthContext(CaptchaAuthStrategy())
is_valid = auth_context.authenticate(user_input, session)
```

---

### Example 2: Slider Captcha

```python
class SliderCaptcha(Captcha):
    """Slide puzzle piece to complete image"""
    
    def __init__(self):
        self.correct_position = random.randint(50, 250)
        self.tolerance = 10  # Acceptable margin of error (±10px)
    
    def generate_challenge(self):
        return {
            'type': self.get_type(),
            'challenge': 'Slide the puzzle piece to complete the image',
            'answer': str(self.correct_position),
            'options': None,
            'tolerance': self.tolerance,
            'puzzle_image': '/static/captcha/puzzle.jpg'
        }
    
    def get_answer(self):
        return str(self.correct_position)
    
    def get_type(self):
        return 'slider'
```

**Register:**
```python
_captcha_types = {
    'color_ball': ColorBallCaptcha,
    'math': MathCaptcha,
    'image': ImageCaptcha,
    'slider': SliderCaptcha,  # ✅ Add
}
```

---

### Example 3: Audio Captcha (Accessibility)

```python
class AudioCaptcha(Captcha):
    """Listen to audio and type what you hear"""
    
    def __init__(self):
        self.code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.audio_url = f'/static/captcha/audio/{self.code}.mp3'
    
    def generate_challenge(self):
        return {
            'type': self.get_type(),
            'challenge': 'Listen to the audio and type the numbers you hear',
            'answer': self.code,
            'options': None,
            'audio_url': self.audio_url
        }
    
    def get_answer(self):
        return self.code
    
    def get_type(self):
        return 'audio'
```

**Register:**
```python
_captcha_types = {
    'color_ball': ColorBallCaptcha,
    'math': MathCaptcha,
    'image': ImageCaptcha,
    'slider': SliderCaptcha,
    'audio': AudioCaptcha,  # ✅ Add
}
```

---

## Benefits

### 1. Separation of Concerns

```
Factory Pattern → Responsible for CREATING captchas
Strategy Pattern → Responsible for VERIFYING captchas

Clear separation!
```

### 2. Open/Closed Principle

```
✅ Open for Extension:
   - Add new captcha types without modifying existing code
   - Just create new Captcha class and register it

✅ Closed for Modification:
   - Login flow unchanged
   - Verification logic unchanged
   - Other captcha types unaffected
```

### 3. Single Responsibility

```
ColorBallCaptcha → Generate color challenges only
MathCaptcha → Generate math challenges only
CaptchaAuthStrategy → Verify captcha answers only
LoginAuthContext → Manage authentication strategies only

Each class has ONE job!
```

### 4. Flexibility

```python
# Easy to switch captcha types at runtime
captcha_type = user_preference or 'color_ball'
captcha = CaptchaFactory.create_captcha(type=captcha_type)

# Easy to switch authentication strategies
context = LoginAuthContext(CaptchaAuthStrategy())
# Later, if needed:
context.strategy = BiometricAuthStrategy()
```

### 5. Testability

```python
# Test color ball captcha independently
def test_color_ball_captcha():
    captcha = ColorBallCaptcha()
    challenge = captcha.generate_challenge()
    assert challenge['type'] == 'color_ball'
    assert challenge['answer'] in challenge['options']

# Test math captcha independently
def test_math_captcha():
    captcha = MathCaptcha()
    challenge = captcha.generate_challenge()
    assert challenge['type'] == 'math'
    # Verify math is correct
    
# Test verification strategy independently
def test_captcha_verification():
    strategy = CaptchaAuthStrategy()
    session = {'captcha_answer': 'blue'}
    assert strategy.verify('blue', session) == True
    assert strategy.verify('red', session) == False
```

### 6. Maintainability

```
Change color ball logic?
→ Modify ColorBallCaptcha only
→ Math captcha unaffected
→ Login flow unaffected
→ Verification logic unaffected

Change verification logic?
→ Modify CaptchaAuthStrategy only
→ Captcha generation unaffected
→ Login flow unaffected
```

### 7. Extensibility

```python
# Want to add difficulty levels?
class HardMathCaptcha(MathCaptcha):
    def __init__(self):
        self.num1 = random.randint(10, 100)  # Harder numbers
        self.num2 = random.randint(10, 100)
        self.operation = random.choice(['+', '-', '*', '/'])

# Register it
CaptchaFactory.register_captcha_type('hard_math', HardMathCaptcha)

# Use it
captcha = CaptchaFactory.create_captcha('hard_math')
```

---

## Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Visits Login Page                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│               GET /login?type=color_ball                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│     ===== FACTORY PATTERN: Captcha Generation =====             │
│                                                                  │
│  CaptchaFactory.create_captcha('color_ball')                    │
│    ↓                                                             │
│  Registry lookup: _captcha_types['color_ball']                  │
│    ↓                                                             │
│  Create instance: ColorBallCaptcha()                            │
│    ↓                                                             │
│  Generate challenge: captcha.generate_challenge()               │
│    ↓                                                             │
│  Returns: {                                                      │
│    'type': 'color_ball',                                        │
│    'challenge': 'Select the blue ball',                         │
│    'answer': 'blue',                                            │
│    'options': ['blue', 'red', 'green']                          │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         session['captcha_answer'] = 'blue'                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│           Render login page with captcha challenge               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│           User sees: "Select the blue ball"                      │
│           User submits: email, password, captcha='blue'          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    POST /login (Form Submission)                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│     ===== STRATEGY PATTERN: Captcha Verification =====          │
│                                                                  │
│  Create context: LoginAuthContext(CaptchaAuthStrategy())        │
│    ↓                                                             │
│  Verify captcha: auth_context.authenticate('blue', session)     │
│    ↓                                                             │
│  Delegates to: CaptchaAuthStrategy.verify('blue', session)      │
│    ↓                                                             │
│  expected = session.get('captcha_answer')  # 'blue'             │
│  return 'blue' == 'blue'  # True                                │
│    ↓                                                             │
│  is_captcha_valid = True                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            Proceed with User Authentication                      │
│              (Password check, role validation)                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Login Successful                               │
│              Redirect to appropriate dashboard                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Takeaways

1. **Factory Pattern** creates different captcha types dynamically
2. **Strategy Pattern** handles captcha verification uniformly
3. **Both patterns work together** for flexible login authentication
4. **Easy to extend** - Add new captcha types without modifying existing code
5. **Clean separation** - Generation and verification are independent
6. **Highly testable** - Each component can be tested in isolation
7. **User-friendly** - Users can choose their preferred captcha type
8. **Accessible** - Easy to add audio captcha for visually impaired users

---

## Real-World Usage Examples

### Color Ball Captcha Flow
```
User visits: /login
→ Factory creates ColorBallCaptcha
→ Challenge: "Select the blue ball"
→ User clicks blue
→ Strategy verifies: 'blue' == 'blue' ✓
→ Login successful
```

### Math Captcha Flow
```
User visits: /login?type=math
→ Factory creates MathCaptcha
→ Challenge: "What is 7 + 3?"
→ User enters: 10
→ Strategy verifies: '10' == '10' ✓
→ Login successful
```

### Future: Image Captcha Flow
```
User visits: /login?type=image
→ Factory creates ImageCaptcha
→ Challenge: "Select all images with cars"
→ User selects: images 1, 4, 7
→ Strategy verifies: '1,4,7' == '1,4,7' ✓
→ Login successful
```

---

## Conclusion

The combination of **Factory Pattern** and **Strategy Pattern** makes the login system:
- **Flexible**: Switch between captcha types easily
- **Extensible**: Add new captcha types without code changes
- **Maintainable**: Clear separation of concerns
- **Testable**: Independent unit testing
- **User-friendly**: Multiple captcha options for different preferences
- **Accessible**: Easy to add audio/text alternatives

**Every login attempt uses both patterns seamlessly: Factory creates the challenge, Strategy verifies the response!** 🎯
