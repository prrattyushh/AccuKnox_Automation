import os
import sys
import subprocess
import random
import string
from datetime import datetime


# -----------------------------
# Auto-install dependencies
# -----------------------------

required = ["playwright"]
for pkg in required:
    try:
        __import__(pkg)
    except ImportError:
        print(f"Installing missing dependency: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

try:
    from playwright.sync_api import sync_playwright, expect
except ImportError:
    subprocess.check_call([sys.executable, "-m", "playwright", "install"])
    from playwright.sync_api import sync_playwright, expect


# -----------------------------
# Configuration
# -----------------------------

def get_config():
    return {
        "url": "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login",
        "username": "Admin",
        "password": "admin123",
    }


# -----------------------------
# Utility Functions
# -----------------------------

def random_username():
    """Generate random username"""
    return "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))


def wait_for_system_users(page, timeout=15000):
    """Ensure Admin > System Users page fully loaded"""
    expect(page.locator("h5:has-text('System Users')")).to_be_visible(timeout=timeout)
    expect(page.locator("//form//label[text()='Username']")).to_be_visible(timeout=timeout)
    page.wait_for_load_state("networkidle")


def select_dropdown_by_label(page, label_text: str, option_index: int):
    """
    Robust dropdown selection - selects specific option by index
    """
    print(f"⌛ Selecting dropdown '{label_text}' with index {option_index}")
    
    # Wait for dropdown icon to be visible and clickable
    icon = page.locator(f"//label[text()='{label_text}']/../following-sibling::div//i")
    expect(icon).to_be_visible(timeout=10000)
    
    # Scroll to element and click
    icon.scroll_into_view_if_needed()
    icon.click()
    
    # Wait for dropdown options to appear
    options = page.locator("//div[@role='listbox']//div[@role='option']")
    expect(options.first).to_be_visible(timeout=5000)
    
    # Get available options count and validate index
    count = options.count()
    print(f"📋 Dropdown '{label_text}' has {count} available options")
    
    if option_index >= count:
        option_index = max(0, count - 1)
        print(f"⚠️ Adjusted option index to {option_index} (available options: {count})")
    
    # Get the text of the option we're about to select for logging
    selected_option = options.nth(option_index)
    option_text = selected_option.inner_text() if selected_option.is_visible() else f"Option {option_index}"
    
    # Select the option
    expect(selected_option).to_be_visible(timeout=3000)
    selected_option.click()
    
    print(f"✅ Selected '{label_text}' - {option_text} (index {option_index})")
    return option_text


def choose_employee_any(page, employee_search_char="a"):
    """
    Deterministic Employee Name selector
    """
    print(f"⌛ Selecting employee with search character '{employee_search_char}'")
    
    emp_field = page.locator("input[placeholder='Type for hints...']")
    expect(emp_field).to_be_visible(timeout=10000)
    
    # Clear existing value and type new character
    emp_field.click()
    emp_field.fill("")  # Clear first
    emp_field.fill(employee_search_char)  # Trigger the autocomplete dropdown
    
    print("⌛ Waiting for employee suggestions...")
    
    # Wait for up to 15 seconds for dropdown to appear
    dropdown_visible = page.locator("//div[@role='listbox']//div[@role='option']")
    try:
        expect(dropdown_visible.first).to_be_visible(timeout=15000)
        
        # Mimic user behavior with keyboard navigation
        page.wait_for_timeout(2000)
        page.keyboard.press("ArrowDown")
        page.wait_for_timeout(500)
        page.keyboard.press("Enter")
        print("✅ Employee selected using keyboard navigation.")
        return True
        
    except Exception as e:
        print(f"❌ No employee suggestions appeared within 15 seconds: {e}")
        return False


def username_input_in_user_form(page):
    """Locate username input in user form"""
    return page.locator("//label[text()='Username']/../following-sibling::div//input")


def password_inputs_in_user_form(page):
    """Locate password inputs in user form"""
    return page.locator(
        "//label[text()='Password']/../following-sibling::div//input"
        " | //label[text()='Confirm Password']/../following-sibling::div//input"
    )


def search_username_field(page):
    """Locate username search field"""
    return page.locator("//form//label[text()='Username']/../following-sibling::div//input")


def click_search(page):
    """Click search button"""
    search_btn = page.locator("button:has-text('Search')")
    expect(search_btn).to_be_visible(timeout=5000)
    search_btn.click()


def click_reset(page):
    """Click reset button if visible"""
    reset_btn = page.locator("button:has-text('Reset')")
    if reset_btn.is_visible(timeout=3000):
        reset_btn.click()
        page.wait_for_timeout(1000)


def js_click_checkbox(page, checkbox_locator):
    """JavaScript click to bypass overlay issues for checkboxes"""
    try:
        page.evaluate("""checkbox => checkbox.click()""", checkbox_locator.element_handle())
        return True
    except Exception as e:
        print(f"❌ JS checkbox click failed: {e}")
        return False


def get_current_dropdown_value(page, label_text: str):
    """
    Get current value of a dropdown field
    """
    try:
        value_locator = page.locator(f"//label[text()='{label_text}']/../following-sibling::div//span")
        if value_locator.is_visible(timeout=3000):
            return value_locator.inner_text()
        return "Unknown"
    except:
        return "Unknown"


def get_available_dropdown_options(page, label_text: str):
    """
    Get all available options in a dropdown for debugging
    """
    try:
        # Open dropdown
        icon = page.locator(f"//label[text()='{label_text}']/../following-sibling::div//i")
        icon.click()
        
        # Get options
        options = page.locator("//div[@role='listbox']//div[@role='option']")
        expect(options.first).to_be_visible(timeout=3000)
        
        option_texts = []
        count = options.count()
        for i in range(count):
            option_text = options.nth(i).inner_text()
            option_texts.append(f"{i}: {option_text}")
        
        # Close dropdown
        page.keyboard.press("Escape")
        
        return option_texts
    except Exception as e:
        return [f"Error getting options: {e}"]


# -----------------------------
# Test Execution Functions
# -----------------------------

def execute_login(page, cfg, test_results):
    """Execute login step"""
    try:
        page.goto(cfg["url"])
        page.fill("input[name='username']", cfg["username"])
        page.fill("input[name='password']", cfg["password"])
        page.click("button[type='submit']")
        expect(page.locator("a:has-text('Admin')")).to_be_visible(timeout=10000)
        test_results.append(("Login", "✅", "Logged in successfully."))
        return True
    except Exception as e:
        test_results.append(("Login", "❌", str(e)))
        return False


def execute_navigate_to_admin(page, test_results):
    """Execute navigation to admin module"""
    try:
        page.click("a:has-text('Admin')")
        wait_for_system_users(page)
        test_results.append(("Navigate to Admin", "✅", "Admin page loaded."))
        return True
    except Exception as e:
        test_results.append(("Navigate to Admin", "❌", str(e)))
        return False


def execute_add_user(page, test_results):
    """
    Execute add user functionality
    - User Role: 2nd option (index 1)
    - Status: 2nd option (index 1)
    """
    try:
        new_user = random_username()
        print(f"🎯 Creating new user: {new_user}")
        print("📝 Add User Configuration:")
        print("   - User Role: 2nd option (index 1)")
        print("   - Status: 2nd option (index 1)")
        
        page.click("button:has-text('Add')")
        expect(page.locator("h6:has-text('Add User')")).to_be_visible(timeout=12000)
        
        # Fill user details with SPECIFIC OPTIONS
        user_role_text = select_dropdown_by_label(page, "User Role", 1)  # 2nd option
        choose_employee_any(page, "a")
        status_text = select_dropdown_by_label(page, "Status", 1)  # 2nd option
        
        username_field = username_input_in_user_form(page)
        expect(username_field).to_be_visible(timeout=15000)
        username_field.fill(new_user)
        
        pw = password_inputs_in_user_form(page)
        pw.nth(0).fill("Test@123")
        pw.nth(1).fill("Test@123")
        
        page.click("button:has-text('Save')")
        expect(page.locator("div.oxd-toast")).to_be_visible(timeout=12000)
        wait_for_system_users(page)
        
        test_results.append(("Add User", "✅", f"User: {new_user}, Role: {user_role_text}, Status: {status_text}"))
        return new_user
        
    except Exception as e:
        page.screenshot(path="fail_add_user.png", full_page=True)
        test_results.append(("Add User", "❌", str(e)))
        return None


def execute_search_user(page, username, test_results):
    """Execute user search functionality"""
    try:
        wait_for_system_users(page)
        click_reset(page)
        
        s = search_username_field(page)
        s.fill(username)
        click_search(page)
        
        row = page.locator(f"//div[@class='oxd-table-body']//div[text()='{username}']")
        expect(row).to_be_visible(timeout=15000)
        
        test_results.append(("Search User", "✅", f"User {username} found."))
        return True
        
    except Exception as e:
        page.screenshot(path="fail_search_user.png", full_page=True)
        test_results.append(("Search User", "❌", str(e)))
        return False


def execute_edit_user_all_fields(page, username, test_results):
    """
    Enhanced Edit User - Edit ALL fields with SPECIFIC OPTIONS
    - User Role: 3rd option (index 2)
    - Status: 3rd option (index 2)
    """
    try:
        print(f"🎯 Editing all fields for user: {username}")
        print("📝 Edit User Configuration:")
        print("   - User Role: 3rd option (index 2)")
        print("   - Status: 3rd option (index 2)")
        
        # Open Edit User modal
        edit_icon = page.locator(f"//div[text()='{username}']/../../..//i[contains(@class,'bi-pencil')]")
        expect(edit_icon).to_be_visible(timeout=10000)
        edit_icon.click()
        
        expect(page.locator("h6:has-text('Edit User')")).to_be_visible(timeout=12000)
        page.wait_for_timeout(2000)  # Wait for form to fully load
        
        # Get current values for logging
        current_role = get_current_dropdown_value(page, "User Role")
        current_status = get_current_dropdown_value(page, "Status")
        print(f"📊 Current state - Role: {current_role}, Status: {current_status}")
        
        # Debug: Show available options
        print("🔍 Available User Role options:")
        role_options = get_available_dropdown_options(page, "User Role")
        for option in role_options:
            print(f"   {option}")
        
        print("🔍 Available Status options:")
        status_options = get_available_dropdown_options(page, "Status")
        for option in status_options:
            print(f"   {option}")
        
        # --- EDIT USER ROLE - 3rd OPTION ---
        print("🔄 Editing User Role to 3rd option...")
        user_role_text = select_dropdown_by_label(page, "User Role", 2)  # 3rd option
        page.wait_for_timeout(1000)
        
        # --- EDIT EMPLOYEE NAME --- 
        print("🔄 Editing Employee Name...")
        emp_field = page.locator("input[placeholder='Type for hints...']")
        expect(emp_field).to_be_visible(timeout=10000)
        
        # Clear existing value using Select All + Delete
        emp_field.click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Delete")
        
        # Select different employee
        choose_employee_any(page, "c")
        page.wait_for_timeout(1000)
        
        # --- EDIT STATUS - 3rd OPTION ---
        print("🔄 Editing Status to 3rd option...")
        status_text = select_dropdown_by_label(page, "Status", 2)  # 3rd option
        page.wait_for_timeout(1500)
        
        # --- EDIT USERNAME ---
        print("🔄 Editing Username...")
        new_username = f"edited_{username}"
        username_field = username_input_in_user_form(page)
        expect(username_field).to_be_visible(timeout=10000)
        
        # Clear and fill new username
        username_field.click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Delete")
        username_field.fill(new_username)
        
        # --- CHANGE PASSWORD ---
        print("🔄 Changing Password...")
        change_pw_checkbox = page.locator(
            "//label[contains(.,'Change Password')]/../following-sibling::div//input[@type='checkbox']"
        )
        expect(change_pw_checkbox).to_be_visible(timeout=10000)
        
        # Use JavaScript click to bypass any overlays
        js_click_checkbox(page, change_pw_checkbox)
        print("✅ Enabled Change Password toggle.")
        
        # Wait for password fields to appear
        pw_fields = page.locator("//input[@type='password']")
        expect(pw_fields.first).to_be_visible(timeout=7000)
        
        # Fill new passwords
        new_password = "NewEditedPass@123"
        pw_fields.nth(0).fill(new_password)
        pw_fields.nth(1).fill(new_password)
        print("✅ Filled new password fields.")
        
        # --- SAVE CHANGES ---
        print("💾 Saving all changes...")
        save_btn = page.locator("button:has-text('Save')")
        expect(save_btn).to_be_visible(timeout=10000)
        save_btn.click()
        
        # Wait for success confirmation
        expect(page.locator("div.oxd-toast")).to_be_visible(timeout=15000)
        wait_for_system_users(page)
        
        test_results.append(("Edit User", "✅", 
                           f"New user: {new_username}, Role: {user_role_text}, Status: {status_text}"))
        return new_username
        
    except Exception as e:
        page.screenshot(path="fail_edit_user.png", full_page=True)
        test_results.append(("Edit User", "❌", str(e)))
        return username


def execute_validate_all_updates(page, original_username, new_username, test_results):
    """Execute comprehensive update validation"""
    try:
        click_reset(page)
        s = search_username_field(page)
        s.fill(new_username)
        click_search(page)
        
        # Verify new username appears
        expect(page.locator(f"//div[text()='{new_username}']")).to_be_visible(timeout=12000)
        
        # Verify old username doesn't exist
        old_user_cell = page.locator(f"//div[text()='{original_username}']")
        if old_user_cell.is_visible(timeout=3000):
            test_results.append(("Validate Update", "⚠️", "Old username still exists"))
        else:
            test_results.append(("Validate Update", "✅", "Old username correctly removed"))
        
        # Get updated role and status
        role_cell = page.locator(f"//div[text()='{new_username}']/../../div[3]")
        status_cell = page.locator(f"//div[text()='{new_username}']/../../div[5]")
        
        expect(role_cell).to_be_visible(timeout=12000)
        expect(status_cell).to_be_visible(timeout=12000)
        
        role_text = role_cell.inner_text()
        status_text = status_cell.inner_text()
        
        test_results.append(("Validate Update", "✅", 
                           f"User: {new_username}, Role: {role_text}, Status: {status_text}"))
        return True
        
    except Exception as e:
        page.screenshot(path="fail_validate_update.png", full_page=True)
        test_results.append(("Validate Update", "❌", str(e)))
        return False


def execute_delete_user(page, username, test_results):
    """Execute user deletion"""
    try:
        click_reset(page)
        s = search_username_field(page)
        s.fill(username)
        click_search(page)
        
        expect(page.locator(f"//div[text()='{username}']")).to_be_visible(timeout=10000)
        
        # Locate the checkbox input
        checkbox = page.locator(f"//div[text()='{username}']/../../..//input[@type='checkbox']")
        expect(checkbox).to_be_visible(timeout=8000)
        page.wait_for_timeout(800)
        
        # Force-check it using JS to bypass icon overlay
        js_click_checkbox(page, checkbox)
        print("✅ Checkbox selected via JS click.")
        
        # Wait for selection highlight
        page.wait_for_timeout(600)
        
        # Click delete buttons
        page.click("button:has-text('Delete Selected')")
        page.wait_for_timeout(500)
        page.click("button:has-text('Yes, Delete')")
        
        expect(page.locator("div.oxd-toast")).to_be_visible(timeout=15000)
        wait_for_system_users(page)
        
        test_results.append(("Delete User", "✅", f"Deleted {username}."))
        return True
        
    except Exception as e:
        page.screenshot(path="fail_delete_user.png", full_page=True)
        test_results.append(("Delete User", "❌", str(e)))
        return False


def execute_validate_deletion(page, username, test_results):
    """Execute deletion validation"""
    try:
        click_reset(page)
        s = search_username_field(page)
        s.fill(username)
        click_search(page)
        
        expect(page.locator("span:has-text('No Records Found')")).to_be_visible(timeout=12000)
        test_results.append(("Validate Deletion", "✅", f"{username} no longer present."))
        return True
        
    except Exception as e:
        page.screenshot(path="fail_validate_deletion.png", full_page=True)
        test_results.append(("Validate Deletion", "❌", str(e)))
        return False


# -----------------------------
# MAIN TEST FLOW
# -----------------------------

def main():
    cfg = get_config()
    test_results = []
    start_time = datetime.now()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=150)
        page = browser.new_page()
        page.set_default_timeout(15000)
        
        # ---------- 1. LOGIN ----------
        if not execute_login(page, cfg, test_results):
            browser.close()
            return
        
        # ---------- 2. NAVIGATE TO ADMIN ----------
        if not execute_navigate_to_admin(page, test_results):
            browser.close()
            return
        
        # ---------- 3. ADD USER (2nd OPTIONS) ----------
        original_username = execute_add_user(page, test_results)
        if not original_username:
            browser.close()
            return
        
        # ---------- 4. SEARCH USER ----------
        if not execute_search_user(page, original_username, test_results):
            browser.close()
            return
        
        # ---------- 5. EDIT USER (3rd OPTIONS) ----------
        new_username = execute_edit_user_all_fields(page, original_username, test_results)
        
        # ---------- 6. VALIDATE ALL UPDATES ----------
        if not execute_validate_all_updates(page, original_username, new_username, test_results):
            browser.close()
            return
        
        # ---------- 7. DELETE USER ----------
        if not execute_delete_user(page, new_username, test_results):
            browser.close()
            return
        
        # ---------- 8. VALIDATE DELETION ----------
        execute_validate_deletion(page, new_username, test_results)
        
        browser.close()
    
    # ---------- TEST SUMMARY ----------
    print("\n" + "="*70)
    print("📊 TEST EXECUTION SUMMARY")
    print("="*70)
    
    for step, status, details in test_results:
        print(f"{step:<25} {status} {details}")
    
    print("\n" + "="*70)
    print(f"⏰ Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏁 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Count results
    passed = sum(1 for _, status, _ in test_results if status == "✅")
    total = len(test_results)
    print(f"📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Specific option selection working perfectly!")
    else:
        print("⚠️ Some tests failed - Check logs for details")
    
    print("="*70 + "\n")


# -----------------------------
# Entry Point
# -----------------------------

if __name__ == "__main__":
    main()