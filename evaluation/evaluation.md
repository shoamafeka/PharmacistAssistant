# Evaluation Scenarios for Pharmacist Assistant

This document outlines manual testing scenarios for all three flows in the Pharmacist Assistant system. Each scenario should be tested in both English and Hebrew to ensure the agent works correctly in both languages.

## Test Data Reference

### Test Users
- **CUST001**: Has active prescriptions (RX001 - Lisinopril, RX002 - Amoxicillin)
- **CUST002**: Has prescriptions (RX003 - Metformin [expired], RX004 - Atorvastatin)
- **CUST006**: Has expired prescription (RX009 - Atorvastatin)

### Test Medications
- **Lisinopril**: In stock (25 units)
- **Metformin**: Low stock (8 units)
- **Atorvastatin**: Out of stock (0 units)
- **Amoxicillin**: In stock (15 units)
- **Ibuprofen**: In stock (50 units)

---

## Flow 1: Medication Stock Check

**Description:** This flow handles user queries about medication availability and stock status. The agent should ask for the medication name and then check stock availability.

**Note:** Each scenario in this flow should be tested in both English and Hebrew.

### Scenario 1.1: Simple Stock Check

**Testing Languages:** Test this scenario in both English and Hebrew.

**User Input Examples:**
- English: "Is Lisinopril in stock?"
- Hebrew: "האם יש ליזינופריל במלאי?"

**Expected Tool Sequence:**
- `check_medication_stock(["Lisinopril"])`

**Verification Points:**
- Agent calls `check_medication_stock` with correct medication name
- Response includes stock status (in_stock/low_stock/out_of_stock)
- Response includes stock quantity
- Agent responds appropriately in the language used by the user

**Expected Outcome:**
- Agent reports that Lisinopril is in stock (25 units)
- Response is in the same language as the user's input

---

### Scenario 1.2: Stock Check with Partial Medication Name

**Testing Languages:** Test this scenario in both English and Hebrew.

**User Input Examples:**
- English: "Do you have Metformin available?"
- Hebrew: "האם יש לכם מטפורמין זמין?"

**Expected Tool Sequence:**
- `check_medication_stock(["Metformin"])`

**Verification Points:**
- Agent correctly identifies medication from partial name
- Agent calls `check_medication_stock` with correct medication name
- Response includes stock status (should be low_stock for Metformin)
- Agent responds in the user's language

**Expected Outcome:**
- Agent reports that Metformin is in low stock (8 units)
- Response is in the same language as the user's input

---

### Scenario 1.3: Multiple Medications Stock Check

**Testing Languages:** Test this scenario in both English and Hebrew.

**User Input Examples:**
- English: "Check stock for Amoxicillin and Ibuprofen"
- Hebrew: "בדוק מלאי עבור אמוקסיצילין ואיבופרופן"

**Expected Tool Sequence:**
- `check_medication_stock(["Amoxicillin", "Ibuprofen"])`

**Verification Points:**
- Agent calls `check_medication_stock` with list of medication names
- Response includes stock status for each medication
- Both medications are reported correctly
- Agent responds in the user's language

**Expected Outcome:**
- Agent reports stock status for both medications:
  - Amoxicillin: in_stock (15 units)
  - Ibuprofen: in_stock (50 units)
- Response is in the same language as the user's input

---

### Scenario 1.4: Non-existent Medication (Error Handling)

**Testing Languages:** Test this scenario in both English and Hebrew.

**User Input Examples:**
- English: "Is Aspirin in stock?"
- Hebrew: "האם יש אספירין במלאי?"

**Expected Tool Sequence:**
- `check_medication_stock(["Aspirin"])`

**Verification Points:**
- Agent calls `check_medication_stock` with the medication name
- Agent handles the case where medication is not found gracefully
- Error message is clear and helpful
- Agent responds in the user's language

**Expected Outcome:**
- Agent reports that Aspirin is not found in the system
- Error message is appropriate and in the user's language
- Agent does not crash or provide incorrect information

---

## Flow 2: Usage Guidance

**Description:** This flow provides medication usage information, dosage instructions, and administration guidance. The agent retrieves medication information and optionally checks for user-specific special instructions.

**Note:** Each scenario in this flow should be tested in both English and Hebrew.

### Scenario 2.1: Basic Usage Question

**Testing Languages:** Test this scenario in both English and Hebrew.

**User Input Examples:**
- English: "How do I take Lisinopril?"
- Hebrew: "איך אני לוקח ליזינופריל?"

**Expected Tool Sequence:**
- `get_medication_info("Lisinopril")`

**Verification Points:**
- Agent calls `get_medication_info` with correct medication name
- Response includes dosage information
- Response includes frequency and administration instructions
- Agent offers to check for special instructions (optional)
- Agent includes policy warning about not providing medical advice
- Agent responds in the user's language

**Expected Outcome:**
- Agent provides complete usage instructions for Lisinopril:
  - Dosage: 5-40mg once daily
  - Administration: Take by mouth with or without food
  - Frequency: Once daily
- Agent mentions this is factual information only, not medical advice
- Response is in the same language as the user's input

---

### Scenario 2.2: Usage Question with User ID (Special Instructions)

**Testing Languages:** Test this scenario in both English and Hebrew.

**User Input Examples:**
- English: "I'm CUST001, how should I take my Lisinopril?"
- Hebrew: "אני CUST001, איך אני צריך לקחת את הליזינופריל שלי?"

**Expected Tool Sequence:**
- `get_medication_info("Lisinopril")`
- `get_user_prescriptions("CUST001")` (optional, if agent offers to check)

**Verification Points:**
- Agent calls `get_medication_info` first
- Agent recognizes user_id and offers to check for special instructions
- Agent optionally calls `get_user_prescriptions` to retrieve user-specific instructions
- Response includes both general and user-specific instructions
- Agent responds in the user's language

**Expected Outcome:**
- Agent provides general Lisinopril usage instructions
- Agent includes user-specific instruction: "Take with food to reduce stomach upset" (from RX001)
- Response is in the same language as the user's input

---

### Scenario 2.3: Dosage-Specific Question

**Testing Languages:** Test this scenario in both English and Hebrew.

**User Input Examples:**
- English: "What's the dosage for Metformin?"
- Hebrew: "מה המינון של מטפורמין?"

**Expected Tool Sequence:**
- `get_medication_info("Metformin")`

**Verification Points:**
- Agent calls `get_medication_info` with correct medication name
- Response focuses on dosage information
- Response includes complete usage instructions
- Agent responds in the user's language

**Expected Outcome:**
- Agent provides dosage information: 500-2000mg daily in divided doses
- Agent includes frequency: Usually twice daily with meals
- Response is in the same language as the user's input

---

### Scenario 2.4: Non-existent Medication (Error Handling)

**Testing Languages:** Test this scenario in both English and Hebrew.

**User Input Examples:**
- English: "How do I take Aspirin?"
- Hebrew: "איך אני לוקח אספירין?"

**Expected Tool Sequence:**
- `get_medication_info("Aspirin")`

**Verification Points:**
- Agent calls `get_medication_info` with the medication name
- Agent handles the case where medication is not found gracefully
- Error message is clear and helpful
- Agent responds in the user's language

**Expected Outcome:**
- Agent reports that Aspirin is not found in the system
- Error message is appropriate and in the user's language
- Agent does not provide incorrect information

---

## Flow 3: Prescription Verification

**Description:** This flow verifies prescription status, retrieves medication details, and checks stock availability. The agent requires both user_id and prescription_id to complete the verification.

**Note:** Each scenario in this flow should be tested in both English and Hebrew.

### Scenario 3.1: Valid Active Prescription Verification

**Testing Languages:** Test this scenario in both English and Hebrew.

**User Input Examples:**
- English: "Verify prescription RX001 for user CUST001"
- Hebrew: "אמת מרשם RX001 עבור משתמש CUST001"

**Expected Tool Sequence:**
- `verify_prescription("CUST001", "RX001")`
- `get_medication_info("Lisinopril")`
- `check_medication_stock(["Lisinopril"])`

**Verification Points:**
- Agent calls `verify_prescription` with correct user_id and prescription_id
- Agent calls `get_medication_info` with medication name from prescription
- Agent calls `check_medication_stock` with medication name
- Response includes prescription status (active/expired)
- Response includes prescription validity (is_valid)
- Response includes medication information
- Response includes stock availability
- Agent responds in the user's language

**Expected Outcome:**
- Agent reports prescription RX001 is active and valid
- Agent provides Lisinopril medication details
- Agent reports Lisinopril is in stock (25 units)
- Complete prescription status is provided
- Response is in the same language as the user's input

---

### Scenario 3.2: Expired Prescription Verification

**Testing Languages:** Test this scenario in both English and Hebrew.

**User Input Examples:**
- English: "Check prescription RX003 for user CUST002"
- Hebrew: "בדוק מרשם RX003 עבור משתמש CUST002"

**Expected Tool Sequence:**
- `verify_prescription("CUST002", "RX003")`
- `get_medication_info("Metformin")`
- `check_medication_stock(["Metformin"])`

**Verification Points:**
- Agent calls `verify_prescription` with correct IDs
- Agent correctly identifies prescription as expired
- Agent reports prescription is not valid
- Agent still provides medication information and stock status
- Agent responds in the user's language

**Expected Outcome:**
- Agent reports prescription RX003 is expired and not valid
- Agent provides Metformin medication details
- Agent reports Metformin stock status (low_stock, 8 units)
- Agent explains that prescription cannot be used for refill
- Response is in the same language as the user's input

---

### Scenario 3.3: Invalid User ID (Error Handling)

**Testing Languages:** Test this scenario in both English and Hebrew.

**User Input Examples:**
- English: "Verify prescription RX001 for user INVALID_USER"
- Hebrew: "אמת מרשם RX001 עבור משתמש INVALID_USER"

**Expected Tool Sequence:**
- `verify_prescription("INVALID_USER", "RX001")`

**Verification Points:**
- Agent calls `verify_prescription` with invalid user_id
- Agent handles error gracefully
- Error message is clear and helpful
- Agent does not proceed to call other tools
- Agent responds in the user's language

**Expected Outcome:**
- Agent reports that user INVALID_USER was not found
- Error message is appropriate and in the user's language
- Agent does not crash or provide incorrect information

---

### Scenario 3.4: Invalid Prescription ID (Error Handling)

**Testing Languages:** Test this scenario in both English and Hebrew.

**User Input Examples:**
- English: "Verify prescription INVALID_RX for user CUST001"
- Hebrew: "אמת מרשם INVALID_RX עבור משתמש CUST001"

**Expected Tool Sequence:**
- `verify_prescription("CUST001", "INVALID_RX")`

**Verification Points:**
- Agent calls `verify_prescription` with invalid prescription_id
- Agent handles error gracefully
- Error message indicates prescription not found for this user
- Agent does not proceed to call other tools
- Agent responds in the user's language

**Expected Outcome:**
- Agent reports that prescription INVALID_RX was not found for user CUST001
- Error message is appropriate and in the user's language
- Agent does not crash or provide incorrect information

---

### Scenario 3.5: Multi-turn Verification (Ask for IDs Separately)

**Testing Languages:** Test this scenario in both English and Hebrew.

**User Input Examples:**

**Turn 1:**
- English: "I want to verify my prescription"
- Hebrew: "אני רוצה לאמת את המרשם שלי"

**Turn 2 (after agent asks for IDs):**
- English: "My user ID is CUST001 and prescription ID is RX001"
- Hebrew: "מספר המשתמש שלי הוא CUST001 ומספר המרשם הוא RX001"

**Expected Tool Sequence:**
- Turn 1: Agent asks for user_id and prescription_id (no tool calls)
- Turn 2: 
  - `verify_prescription("CUST001", "RX001")`
  - `get_medication_info("Lisinopril")`
  - `check_medication_stock(["Lisinopril"])`

**Verification Points:**
- Agent recognizes intent to verify prescription
- Agent asks for both user_id and prescription_id in first turn
- Agent waits for user to provide IDs before calling tools
- After receiving IDs, agent follows complete tool sequence
- Agent responds in the user's language throughout

**Expected Outcome:**
- First turn: Agent asks for user_id and prescription_id
- Second turn: Agent completes full verification flow
- Agent provides complete prescription status
- All responses are in the same language as the user's input

---

## General Testing Guidelines

### Language Testing
- Each scenario must be tested in both English and Hebrew
- Verify that the agent responds in the same language as the user's input
- Verify that tool calls work correctly regardless of input language
- Verify that error messages are appropriate in both languages

### Tool Call Verification
- Verify that tools are called in the expected sequence
- Verify that tool parameters are correct
- Verify that tool results are properly interpreted and presented

### Error Handling
- Verify that errors are handled gracefully
- Verify that error messages are clear and helpful
- Verify that the agent does not crash on errors
- Verify that the agent does not proceed with invalid data

### Policy Compliance
- Verify that the agent includes appropriate warnings about not providing medical advice
- Verify that the agent only provides factual information from the database
- Verify that the agent does not suggest alternative purchasing methods unless explicitly part of the system

---

## Test Execution Notes

1. **Manual Testing:** These scenarios are designed for manual testing through the Streamlit interface
2. **Tool Call Monitoring:** Use the expandable tool call sections in the UI to verify tool sequences
3. **Language Switching:** Test each scenario twice - once in English, once in Hebrew
4. **Documentation:** Document any deviations from expected behavior
5. **Edge Cases:** Pay special attention to error handling scenarios

