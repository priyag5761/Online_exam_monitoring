from rule_engine import deduct_marks, get_score, reset_score

print("Initial Score:", get_score())

deduct_marks("Face Absent")
print("After Face Absent:", get_score())

deduct_marks("Tab Switched")
print("After Tab Switch:", get_score())

deduct_marks("Multiple Faces")
print("After Multiple Faces:", get_score())

reset_score()
print("After Reset:", get_score())