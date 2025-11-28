# Create Business Feature - Builder Design Pattern

## Overview

A new **admin feature** has been added to allow administrators to create new businesses directly from the admin panel. This implementation uses the **Builder Design Pattern** for fluent, step-by-step business creation with built-in validation.

## Design Pattern: Builder

The Builder pattern provides a flexible way to construct complex objects (Business) step-by-step. This allows:

- **Fluent interface**: chain method calls for readable, maintainable code
- **Validation**: each setter validates its input
- **Flexibility**: optional fields don't need to be set
- **Reusability**: can build multiple businesses without duplication

### Why Builder for Business Creation?

The `Business` model has many fields (name, email, phone, address, category, etc.). Using the Builder pattern:

1. Ensures required fields are always validated
2. Makes optional fields optional (owner_name, description, gallery)
3. Provides clear, self-documenting code
4. Allows future extensions (e.g., `build_with_services()`)

## Files Added/Modified

### New Files

#### 1. `backend/patterns/builder_business.py`

- **Class**: `BusinessBuilder`

  - **Methods**:
    - `set_name()`, `set_email()`, `set_phone()`, `set_street_house()`, `set_city()`, `set_district()`, `set_category()` — required setters with validation
    - `set_description()`, `set_owner_name()`, `set_profile_pic_url()`, `set_gallery_urls()` — optional setters
    - `set_is_active()` — set status (default: True)
    - `build()` — construct and validate the Business object (doesn't save)
    - `build_and_save()` — construct, validate, and save to MongoDB
    - `validate()` — check all required fields
    - `reset()` — reinitialize builder for reuse

- **Function**: `create_business_from_dict(data)`
  - Convenience function to build from a dictionary

#### 2. `frontend/admin/create_business.html`

- New form page for admin to create businesses
- Organized into sections:
  - **Basic Information**: name, category, description
  - **Contact Information**: email, phone, owner name
  - **Address**: street, city, district
- Client-side JavaScript validation
- Bootstrap 5 styling matching admin panel design
- Form data repopulation on validation error

### Modified Files

#### 1. `backend/views/admin.py`

- Added import: `from patterns.builder_business import BusinessBuilder`
- **New route**: `GET /admin/businesses/create` — shows create form
- **New route**: `POST /admin/businesses/create` — processes form and creates business
  - Uses `BusinessBuilder()` to construct the business
  - Catches validation errors and re-displays form with error messages
  - Redirects to business detail page on success
- Fixed: `name__icontains` search query (was `business_name__icontains`)

#### 2. `frontend/admin/businesses.html`

- Added "Create New Business" button (green, top-right of page)
- Links to `/admin/businesses/create`

#### 3. `backend/views/home.py` (no changes needed)

- The `/services` route already fetches all businesses via `get_all_businesses()`
- Newly created businesses automatically appear in the services list

## How to Use

### Admin Creates a Business

1. **Login to Admin Panel**

   - Go to: http://127.0.0.1:5000/admin/login
   - Credentials: `admin` / `admin123`

2. **Navigate to Businesses**

   - Click "Businesses" in the sidebar
   - Or go directly to: http://127.0.0.1:5000/admin/businesses

3. **Create Business**

   - Click "Create New Business" button (green, top-right)
   - Fill out the form:
     - **Name**: Business name (required)
     - **Category**: Select from dropdown (required)
     - **Email**: Business email (required)
     - **Phone**: Business phone (required)
     - **Address**: Street, city, district (required)
     - **Owner Name**: Optional
     - **Description**: Optional
   - Click "Create Business"

4. **Verify Business Created**
   - Admin is redirected to the new business detail page
   - Success message appears: "Business '...' created successfully!"
   - Business is now in the admin list: http://127.0.0.1:5000/admin/businesses

### Users See New Business

5. **Browse Services**
   - Regular users visit: http://127.0.0.1:5000/services
   - The new business appears in the services list
   - Users can filter by category or city
   - Users can book services from the new business

## Code Examples

### Using BusinessBuilder Directly (in Python)

```python
from patterns.builder_business import BusinessBuilder

# Create a business using the builder
business = (BusinessBuilder()
    .set_name("Smith Plumbing")
    .set_email("smith@plumbing.com")
    .set_phone("555-1234")
    .set_category("plumbing")
    .set_city("New York")
    .set_district("Manhattan")
    .set_street_house("123 Main St")
    .set_description("Professional plumbing services for residential and commercial")
    .set_owner_name("John Smith")
    .build_and_save())

print(f"Business created: {business.business_id}")
```

### Using create_business_from_dict (convenience function)

```python
from patterns.builder_business import create_business_from_dict

data = {
    'name': 'Smith Plumbing',
    'email': 'smith@plumbing.com',
    'phone': '555-1234',
    'category': 'plumbing',
    'city': 'New York',
    'district': 'Manhattan',
    'street_house': '123 Main St',
    'description': 'Professional plumbing services',
    'owner_name': 'John Smith'
}

business = create_business_from_dict(data)
print(f"Business created: {business.business_id}")
```

### In Admin Route (Form Processing)

```python
@admin_bp.route('/businesses/create', methods=['POST'])
@admin_required
def create_business():
    try:
        builder = (BusinessBuilder()
                   .set_name(request.form.get('name'))
                   .set_email(request.form.get('email'))
                   .set_phone(request.form.get('phone'))
                   # ... set other fields ...
                   )
        business = builder.build_and_save()
        flash('Business created successfully!', 'success')
        return redirect(url_for('admin.business_detail', business_id=business.business_id))
    except ValueError as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template('admin/create_business.html'), 400
```

## Validation Rules

All required fields are validated by the builder:

| Field           | Required | Validation                 |
| --------------- | -------- | -------------------------- |
| name            | Yes      | Cannot be empty            |
| email           | Yes      | Must be valid email format |
| phone           | Yes      | Cannot be empty            |
| street_house    | Yes      | Cannot be empty            |
| city            | Yes      | Cannot be empty            |
| district        | Yes      | Cannot be empty            |
| category        | Yes      | Cannot be empty            |
| description     | No       | Optional, stored as-is     |
| owner_name      | No       | Optional                   |
| profile_pic_url | No       | Optional                   |
| gallery_urls    | No       | Optional list of URLs      |
| is_active       | No       | Defaults to True           |

## Error Handling

### Builder Validation Errors

- If required fields are missing, builder raises `ValueError` with descriptive message
- Examples:
  - `ValueError: Cannot build business: Missing required field: name`
  - `ValueError: Invalid email address`
  - `ValueError: Phone number cannot be empty`

### Form Processing Errors

- Admin form catches `ValueError` and displays error message
- Form is re-rendered with user's previous input (except password-like fields)
- HTTP 400 status returned on validation error
- HTTP 500 status returned on unexpected errors (with flash message)

## Database Integration

- All new businesses are saved to MongoDB via `business.save()`
- Business is assigned a unique `business_id` (UUID)
- Auto-timestamped with `created_at` and `updated_at`
- Can be queried immediately in `get_all_businesses()`

## Testing the Feature

### Smoke Test

```bash
# 1. Start backend
cd backend
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py

# 2. In browser:
# - Admin login: http://127.0.0.1:5000/admin/login (admin/admin123)
# - Create business: http://127.0.0.1:5000/admin/businesses/create
# - Fill form and submit
# - Verify success page and check services list: http://127.0.0.1:5000/services
```

### Unit Test Example (with pytest)

```python
from patterns.builder_business import BusinessBuilder
import pytest

def test_builder_requires_name():
    """Test that builder validates required fields"""
    builder = BusinessBuilder()
    with pytest.raises(ValueError, match="name cannot be empty"):
        builder.build()

def test_builder_fluent_interface():
    """Test builder chaining works"""
    builder = (BusinessBuilder()
               .set_name("Test Business")
               .set_email("test@test.com")
               .set_phone("555-1234")
               .set_category("cleaning")
               .set_city("NYC")
               .set_district("Manhattan")
               .set_street_house("123 Main"))

    business = builder.build()
    assert business.name == "Test Business"
    assert business.is_active == True
```

## Future Enhancements

- [ ] Allow admin to upload profile pictures during creation
- [ ] Add initial services/pricing during business creation
- [ ] Bulk import businesses from CSV
- [ ] Email notification to business owner on creation
- [ ] Assign business to existing user account
- [ ] Add business logos/branding during setup
- [ ] Pre-populate address fields from geolocation API

## Summary

This feature allows admins to quickly add new businesses to the platform using a clean, validated, and extensible builder pattern. The implementation follows design best practices:

- **Validation**: All required fields checked before save
- **Error handling**: User-friendly error messages
- **Separation of concerns**: Builder logic separate from route logic
- **Reusability**: Builder can be used in scripts, tests, or other routes
- **Maintainability**: Code is clear and self-documenting

---

**Last Updated**: November 25, 2025
